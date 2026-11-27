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
    student_skills = {}
    if g.career_user["role"] == "student":
        jobs = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
        saved_profile = db.execute(
            "SELECT skills FROM profiles WHERE student_id = ?", (g.career_user["id"],)
        ).fetchone()
        applications = {
            row["job_id"]: row for row in db.execute(
                "SELECT job_id, status, submitted_at FROM applications WHERE student_id = ?",
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
        has_profile_skills=bool(student_skills), applications=applications,
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
