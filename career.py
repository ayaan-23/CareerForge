"""Student profiles and recruiter job postings."""
import json
import re
import sqlite3
from functools import wraps
from io import BytesIO
from pathlib import Path

from docx import Document
from flask import (
    Blueprint, abort, current_app, flash, g, redirect, render_template,
    request, send_file, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from interview_generator import evaluate_answer, generate_interview_questions
from scoring import calculate_skill_score

career = Blueprint("career", __name__, url_prefix="/career")
ROLES = {"student", "recruiter"}
PROFILE_FIELDS = {
    "education": "Education", "skills": "Technical skills",
    "projects": "Projects", "certifications": "Certifications",
}
JOB_FIELDS = {
    "title": "Job title", "company": "Company", "description": "Job description",
    "qualifications": "Required qualifications", "skills": "Required skills",
}
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'recruiter'))
);
CREATE TABLE IF NOT EXISTS profiles (
    student_id INTEGER PRIMARY KEY REFERENCES users(id),
    education TEXT NOT NULL,
    skills TEXT NOT NULL,
    projects TEXT NOT NULL,
    certifications TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    recruiter_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    description TEXT NOT NULL,
    qualifications TEXT NOT NULL,
    skills TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS applications (
    student_id INTEGER NOT NULL REFERENCES users(id),
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    profile_snapshot TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Submitted',
    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, job_id)
);
CREATE TABLE IF NOT EXISTS practice_interviews (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id),
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    questions TEXT NOT NULL,
    job_context TEXT NOT NULL,
    profile_context TEXT NOT NULL,
    results TEXT,
    score REAL,
    badge TEXT,
    completed_at TEXT
);
CREATE INDEX IF NOT EXISTS practice_interviews_student ON practice_interviews(student_id);
CREATE TABLE IF NOT EXISTS shared_interview_badges (
    student_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    badge TEXT NOT NULL,
    PRIMARY KEY (student_id, job_id),
    FOREIGN KEY (student_id, job_id) REFERENCES applications(student_id, job_id)
);
"""


def init_career(app, limiter):
    app.config.setdefault("CAREER_DATABASE", Path(app.instance_path) / "career.sqlite3")
    app.register_blueprint(career)
    app.teardown_appcontext(close_db)
    for endpoint in ("career.login", "career.register"):
        app.view_functions[endpoint] = limiter.limit(
            "10 per minute", methods=["POST"]
        )(app.view_functions[endpoint])
    with app.app_context():
        Path(app.config["CAREER_DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
        get_db().executescript(SCHEMA)


def get_db():
    if "career_db" not in g:
        g.career_db = sqlite3.connect(current_app.config["CAREER_DATABASE"])
        g.career_db.row_factory = sqlite3.Row
        g.career_db.execute("PRAGMA foreign_keys = ON")
    return g.career_db


def close_db(error=None):
    db = g.pop("career_db", None)
    if db is not None:
        db.close()


@career.before_request
def load_user():
    user_id = session.get("career_user_id")
    g.career_user = None
    if user_id is not None:
        g.career_user = get_db().execute(
            "SELECT id, name, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def require_role(role=None):
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.career_user is None:
                return redirect(url_for("career.login"))
            if role is not None and g.career_user["role"] != role:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorate


@career.get("/")
def home():
    endpoint = "career.dashboard" if g.career_user else "career.login"
    return redirect(url_for(endpoint))


@career.route("/register", methods=["GET", "POST"])
def register():
    if g.career_user:
        return redirect(url_for("career.dashboard"))
    if request.method == "GET":
        return render_template("career.html", page="register")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "")
    if not (
        0 < len(name) <= 100
        and len(email) <= 254
        and email.count("@") == 1
        and all(email.split("@"))
        and not any(char.isspace() for char in email)
        and 8 <= len(password) <= 128
        and role in ROLES
    ):
        flash("Enter a name, valid email, account type, and password of 8–128 characters.")
        return render_template("career.html", page="register"), 400

    db = get_db()
    try:
        with db:
            db.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (name, email, generate_password_hash(password), role),
            )
    except sqlite3.IntegrityError:
        flash("That email is already registered. Sign in with your existing account.")
        return render_template("career.html", page="register"), 409
    flash("Account created. Sign in to continue.")
    return redirect(url_for("career.login"))


@career.route("/login", methods=["GET", "POST"])
def login():
    if g.career_user:
        return redirect(url_for("career.dashboard"))
    if request.method == "GET":
        return render_template("career.html", page="login")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = get_db().execute(
        "SELECT id, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()
    if not user or len(password) > 128 or not check_password_hash(user["password_hash"], password):
        flash("Email or password is incorrect.")
        return render_template("career.html", page="login"), 401

    session.clear()
    session["career_user_id"] = user["id"]
    return redirect(url_for("career.dashboard"))


@career.post("/logout")
@require_role()
def logout():
    session.clear()
    return redirect(url_for("career.login"))


def skill_entries(text):
    """Read explicit skill lists while preserving the recruiter's spelling."""
    entries = {}
    for skill in re.split(r"[,;\n]+", text):
        label = " ".join(skill.split())
        if label:
            entries.setdefault(label.casefold(), label)
    return entries


def job_match(student_skills, required_text):
    required = skill_entries(required_text)
    if not required:
        return None

    return {
        "score": calculate_skill_score(student_skills, required),
        "matched": [label for key, label in required.items() if key in student_skills],
        "missing": [label for key, label in required.items() if key not in student_skills],
        "total": len(required),
    }


@career.get("/dashboard")
@require_role()
def dashboard():
    db = get_db()
    matches = {}
    applications = {}
    query = ""
    student_skills = {}
    if g.career_user["role"] == "student":
        query = request.args.get("q", "").strip()[:100]
        jobs = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
        if query:
            terms = query.casefold().split()
            jobs = [
                job for job in jobs
                if all(
                    any(term in job[field].casefold() for field in ("title", "company", "skills"))
                    for term in terms
                )
            ]
        saved_profile = db.execute(
            "SELECT skills FROM profiles WHERE student_id = ?", (g.career_user["id"],)
        ).fetchone()
        applications = {
            row["job_id"]: row for row in db.execute(
                """
                SELECT applications.job_id, status, submitted_at, shared.badge,
                       EXISTS (
                           SELECT 1 FROM practice_interviews AS practice
                           WHERE practice.student_id = applications.student_id
                             AND practice.job_id = applications.job_id
                             AND practice.badge IS NOT NULL
                             AND practice.completed_at IS NOT NULL
                       ) AS can_share_badge
                FROM applications
                LEFT JOIN shared_interview_badges AS shared USING (student_id, job_id)
                WHERE applications.student_id = ?
                """,
                (g.career_user["id"],),
            )
        }
        if saved_profile:
            student_skills = skill_entries(saved_profile["skills"])
        if student_skills:
            matches = {job["id"]: job_match(student_skills, job["skills"]) for job in jobs}
            jobs.sort(
                key=lambda job: matches[job["id"]]["score"] if matches[job["id"]] else -1,
                reverse=True,
            )
    else:
        jobs = db.execute(
            "SELECT * FROM jobs WHERE recruiter_id = ? ORDER BY id DESC",
            (g.career_user["id"],),
        ).fetchall()
    return render_template(
        "career.html", page="dashboard", jobs=jobs, matches=matches,
        has_profile_skills=bool(student_skills), applications=applications, query=query,
    )


@career.route("/profile", methods=["GET", "POST"])
@require_role("student")
def profile():
    db = get_db()
    user_id = g.career_user["id"]
    if request.method == "GET":
        values = db.execute(
            "SELECT * FROM profiles WHERE student_id = ?", (user_id,)
        ).fetchone()
        return render_template(
            "career.html", page="profile", fields=PROFILE_FIELDS, values=values or {}
        )

    values = {key: request.form.get(key, "").strip() for key in PROFILE_FIELDS}
    if not values["education"] or not skill_entries(values["skills"]) or any(
        len(value) > 4000 for value in values.values()
    ):
        flash("Education and skills are required. Each field can contain up to 4,000 characters.")
        return render_template(
            "career.html", page="profile", fields=PROFILE_FIELDS, values=values
        ), 400

    with db:
        db.execute(
            """
            INSERT INTO profiles (student_id, education, skills, projects, certifications)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                education = excluded.education, skills = excluded.skills,
                projects = excluded.projects, certifications = excluded.certifications
            """,
            (user_id, *values.values()),
        )
    flash("Profile saved.")
    return redirect(url_for("career.profile"))


@career.route("/jobs/new", methods=["GET", "POST"])
@require_role("recruiter")
def new_job():
    if request.method == "GET":
        return render_template("career.html", page="job", fields=JOB_FIELDS, values={})

    values = {key: request.form.get(key, "").strip() for key in JOB_FIELDS}
    if not skill_entries(values["skills"]) or any(
        not value or len(value) > 4000 for value in values.values()
    ):
        flash("Fill in every field and keep each entry within 4,000 characters.")
        return render_template(
            "career.html", page="job", fields=JOB_FIELDS, values=values
        ), 400

    db = get_db()
    with db:
        db.execute(
            """
            INSERT INTO jobs (recruiter_id, title, company, description, qualifications, skills)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (g.career_user["id"], *values.values()),
        )
    flash("Job published.")
    return redirect(url_for("career.dashboard"))


def job_and_profile(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if job is None:
        abort(404)
    saved_profile = db.execute(
        """
        SELECT users.name, users.email, profiles.education, profiles.skills,
               profiles.projects, profiles.certifications
        FROM profiles JOIN users ON users.id = profiles.student_id
        WHERE profiles.student_id = ?
        """,
        (g.career_user["id"],),
    ).fetchone()
    return job, saved_profile


@career.get("/jobs/<int:job_id>/resume")
@require_role("student")
def download_resume(job_id):
    job, saved_profile = job_and_profile(job_id)
    if saved_profile is None:
        flash("Save your profile to generate a resume.")
        return redirect(url_for("career.profile"))

    document = Document()
    document.add_heading(saved_profile["name"], 0)
    document.add_paragraph(saved_profile["email"])
    document.add_paragraph(f'Target role: {job["title"]} at {job["company"]}')

    skills = skill_entries(saved_profile["skills"])
    required = skill_entries(job["skills"])
    relevant = [skills[key] for key in skills if key in required]
    additional = [skills[key] for key in skills if key not in required]
    for heading, entries in (("Relevant skills", relevant), ("Additional skills", additional)):
        if entries:
            document.add_heading(heading, level=1)
            document.add_paragraph(", ".join(entries))

    for key in ("education", "projects", "certifications"):
        if saved_profile[key]:
            document.add_heading(PROFILE_FIELDS[key], level=1)
            for line in saved_profile[key].splitlines():
                if line.strip():
                    document.add_paragraph(line.strip())

    output = BytesIO()
    document.save(output)
    output.seek(0)
    response = send_file(
        output, as_attachment=True, download_name=f"careerforge-resume-{job_id}.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response.cache_control.no_store = True
    return response


@career.post("/jobs/<int:job_id>/apply")
@require_role("student")
def apply_for_job(job_id):
    _, saved_profile = job_and_profile(job_id)
    if saved_profile is None:
        flash("Save your profile before applying.")
        return redirect(url_for("career.profile"))

    db = get_db()
    with db:
        result = db.execute(
            """
            INSERT INTO applications (student_id, job_id, profile_snapshot)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, job_id) DO NOTHING
            """,
            (g.career_user["id"], job_id, json.dumps(dict(saved_profile))),
        )
    if result.rowcount:
        flash("Application submitted.")
    else:
        flash("You already applied for this job.")
    return redirect(url_for("career.dashboard", _anchor=f"job-{job_id}"))


def recruiter_job(job_id):
    job = get_db().execute(
        "SELECT * FROM jobs WHERE id = ? AND recruiter_id = ?",
        (job_id, g.career_user["id"]),
    ).fetchone()
    if job is None:
        abort(404)
    return job


@career.get("/jobs/<int:job_id>/applicants")
@require_role("recruiter")
def applicants(job_id):
    job = recruiter_job(job_id)
    status = request.args.get("status", "")
    if status not in ("", "Submitted", "Shortlisted"):
        abort(400)

    applicants = []
    rows = get_db().execute(
        """
        SELECT applications.student_id, profile_snapshot, status, submitted_at, shared.badge
        FROM applications
        LEFT JOIN shared_interview_badges AS shared USING (student_id, job_id)
        WHERE applications.job_id = ? AND (? = '' OR status = ?)
        ORDER BY submitted_at, applications.student_id
        """,
        (job_id, status, status),
    )
    for row in rows:
        profile = json.loads(row["profile_snapshot"])
        match = job_match(skill_entries(profile["skills"]), job["skills"])
        applicants.append({"application": row, "profile": profile, "match": match})
    applicants.sort(
        key=lambda applicant: applicant["match"]["score"] if applicant["match"] else -1,
        reverse=True,
    )
    return render_template(
        "career.html", page="applicants", job=job, applicants=applicants,
        status=status, profile_fields=PROFILE_FIELDS,
    )


@career.post("/jobs/<int:job_id>/applicants/<int:student_id>/shortlist")
@require_role("recruiter")
def shortlist_applicant(job_id, student_id):
    recruiter_job(job_id)
    db = get_db()
    with db:
        result = db.execute(
            """
            UPDATE applications SET status = 'Shortlisted'
            WHERE job_id = ? AND student_id = ? AND status = 'Submitted'
            """,
            (job_id, student_id),
        )
        if not result.rowcount:
            existing = db.execute(
                "SELECT status FROM applications WHERE job_id = ? AND student_id = ?",
                (job_id, student_id),
            ).fetchone()
            if existing is None:
                abort(404)
    flash("Applicant shortlisted." if result.rowcount else "Applicant is already shortlisted.")
    return redirect(url_for("career.applicants", job_id=job_id))


BADGE_MINIMUM = 75
BADGE_NAME = "Interview Ready"


@career.post("/jobs/<int:job_id>/practice")
@require_role("student")
def start_practice(job_id):
    job, saved_profile = job_and_profile(job_id)
    if saved_profile is None:
        flash("Save your profile to start a mock interview.")
        return redirect(url_for("career.profile"))

    job_context = "\n".join(job[key] for key in ("title", "description", "qualifications", "skills"))
    profile_context = "\n".join(
        f"{label}: {saved_profile[key]}" for key, label in PROFILE_FIELDS.items()
    )
    questions = generate_interview_questions(job_context, profile_context)
    db = get_db()
    with db:
        attempt = db.execute(
            """
            INSERT INTO practice_interviews
                (student_id, job_id, questions, job_context, profile_context)
            VALUES (?, ?, ?, ?, ?)
            """,
            (g.career_user["id"], job_id, json.dumps(questions), job_context, profile_context),
        )
    return redirect(url_for("career.practice", attempt_id=attempt.lastrowid))


@career.get("/practice")
@require_role("student")
def practice_history():
    attempts = get_db().execute(
        """
        SELECT practice_interviews.id, jobs.title, jobs.company, score, badge, completed_at
        FROM practice_interviews JOIN jobs ON jobs.id = practice_interviews.job_id
        WHERE practice_interviews.student_id = ?
        ORDER BY practice_interviews.id DESC
        """,
        (g.career_user["id"],),
    ).fetchall()
    return render_template("career.html", page="practice_history", attempts=attempts)


@career.route("/practice/<int:attempt_id>", methods=["GET", "POST"])
@require_role("student")
def practice(attempt_id):
    db = get_db()
    attempt = db.execute(
        """
        SELECT practice_interviews.*, jobs.title, jobs.company
        FROM practice_interviews JOIN jobs ON jobs.id = practice_interviews.job_id
        WHERE practice_interviews.id = ? AND student_id = ?
        """,
        (attempt_id, g.career_user["id"]),
    ).fetchone()
    if attempt is None:
        abort(404)
    if attempt["completed_at"]:
        if request.method == "POST":
            return redirect(url_for("career.practice", attempt_id=attempt_id))
        return render_template(
            "career.html", page="practice_result", attempt=attempt,
            results=json.loads(attempt["results"]), badge_minimum=BADGE_MINIMUM,
        )

    questions = json.loads(attempt["questions"])
    if request.method == "GET":
        return render_template(
            "career.html", page="practice", attempt=attempt, questions=questions, answers=[]
        )

    answers = [answer.strip() for answer in request.form.getlist("answer")]
    if len(answers) != len(questions) or any(len(answer) > 4000 for answer in answers):
        flash("Submit one response field per question, with up to 4,000 characters each.")
        return render_template(
            "career.html", page="practice", attempt=attempt, questions=questions, answers=answers,
        ), 400

    results = []
    for item, answer in zip(questions, answers):
        evaluation = evaluate_answer(
            item["question"], answer, attempt["job_context"], attempt["profile_context"]
        )
        results.append({**item, "answer": answer, **evaluation})
    score = round(sum(result["score"] for result in results) / len(results), 2)
    badge = BADGE_NAME if all(answers) and score >= BADGE_MINIMUM else None
    with db:
        db.execute(
            """
            UPDATE practice_interviews
            SET results = ?, score = ?, badge = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND student_id = ? AND completed_at IS NULL
            """,
            (json.dumps(results), score, badge, attempt_id, g.career_user["id"]),
        )
    return redirect(url_for("career.practice", attempt_id=attempt_id))


@career.post("/jobs/<int:job_id>/application/badge")
@require_role("student")
def update_shared_badge(job_id):
    student_id = g.career_user["id"]
    db = get_db()
    application = db.execute(
        "SELECT 1 FROM applications WHERE student_id = ? AND job_id = ?",
        (student_id, job_id),
    ).fetchone()
    if application is None:
        abort(404)

    action = request.form.get("action")
    with db:
        if action == "share":
            result = db.execute(
                """
                INSERT INTO shared_interview_badges (student_id, job_id, badge)
                SELECT student_id, job_id, badge FROM practice_interviews
                WHERE student_id = ? AND job_id = ? AND badge IS NOT NULL
                  AND completed_at IS NOT NULL
                ORDER BY id DESC LIMIT 1
                ON CONFLICT(student_id, job_id) DO UPDATE SET badge = excluded.badge
                """,
                (student_id, job_id),
            )
            flash("Interview badge shared." if result.rowcount else "Earn a badge for this job before sharing.")
        elif action == "remove":
            db.execute(
                "DELETE FROM shared_interview_badges WHERE student_id = ? AND job_id = ?",
                (student_id, job_id),
            )
            flash("Interview badge sharing removed.")
        else:
            abort(400)
    return redirect(url_for("career.dashboard", _anchor=f"job-{job_id}"))
