
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import send_file
from report_generator import generate_report
from career import init_career
from docx import Document
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect, generate_csrf
from apscheduler.schedulers.background import BackgroundScheduler
import os
import uuid
import pymupdf
import time
import json
import re

from interview_generator import (
    generate_interview_questions,
    evaluate_answer
)

from sentence_transformers import SentenceTransformer, util
from utils import extract_skills, extract_certifications

from scoring import (
    calculate_skill_score,
    calculate_weighted_score,
    calculate_education_score,
    calculate_project_score,
    calculate_experience_score,
    analyze_projects
)


# =========================================================
# 1. APPLICATION CONFIGURATION
# =========================================================

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app = Flask(__name__)

# Secret key for session and CSRF security
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "SECRET_KEY environment variable is not configured."
    )

# Enable CSRF protection once
csrf = CSRFProtect(app)

# Register CSRF token function for HTML templates
app.jinja_env.globals["csrf_token"] = generate_csrf

# Enable rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Store temporary uploads outside the public static folder
UPLOAD_FOLDER = os.path.join(
    app.instance_path,
    "temporary_uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

init_career(app, limiter)


# =========================================================
# 2. EXTRACT TEXT FROM PDF OR DOCX
# =========================================================

def extract_resume_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == '.pdf':

        text = ""

        with pymupdf.open(file_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"

        return text.strip()

    elif extension == '.docx':

        document = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs).strip()

    raise ValueError("Unsupported resume format.")


# =========================================================
# 3. LOAD AI MODEL
# =========================================================

print("Loading AI model...")

model = SentenceTransformer('stsb-roberta-large')

model.eval()

print("AI model loaded successfully!")


# =========================================================
# 4. CHECK ALLOWED FILE TYPE
# =========================================================

def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def validate_file_content(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        try:
            with pymupdf.open(file_path) as doc:
                return len(doc) > 0
        except Exception:
            return False

    elif extension == ".docx":
        try:
            Document(file_path)
            return True
        except Exception:
            return False

    return False


# =========================================================
# 5. HOME PAGE
# =========================================================

@app.route('/')
def index():

    return render_template('index.html')


# =========================================================
# 6. RESUME ANALYSIS
# =========================================================

@app.route('/analyze', methods=['POST'])
@limiter.limit("5 per minute")
def analyze():

    resume_file = request.files.get('resume')

    job_desc = request.form.get(
        'job_description', ''
    ).strip()

    # Validate uploaded resume

    if not resume_file or not resume_file.filename:
        return "Please upload a resume.", 400

    if not allowed_file(resume_file.filename):
        return "Only PDF and DOCX files are allowed.", 400

    if not job_desc:
        return "Please enter a job description.", 400

    # Save uploaded file securely

    filename = secure_filename(resume_file.filename)

    if not filename:
        return "Invalid filename.", 400

    unique_filename = f"{uuid.uuid4().hex}_{filename}"

    save_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        unique_filename
    )

    try:
        resume_file.save(save_path)

        if not validate_file_content(save_path):
            return "Invalid or corrupted PDF/DOCX file.", 400

        # 1. Extract resume text
        resume_text = extract_resume_text(save_path)

        if not resume_text or not resume_text.strip():
            return "No readable text found in the uploaded resume.", 400

        # 2. Calculate semantic similarity

        embeddings = model.encode(
            [resume_text, job_desc],
            convert_to_tensor=True
        )

        similarity_score = util.pytorch_cos_sim(
            embeddings[0],
            embeddings[1]
        ).item()

        semantic_score = round(
            max(0, min(100, similarity_score * 100)), 2
        )

        # 3. Extract skills and certifications

        resume_skills = set(extract_skills(resume_text))

        # Resume Section Completeness Checker

        resume_lower = resume_text.lower()

        resume_sections = {
            "Contact Information": any(
                item in resume_lower
                for item in ["email", "phone", "mobile"]
            ),
            "Education": any(
                item in resume_lower
                for item in ["education", "bachelor", "degree", "university"]
            ),
            "Technical Skills": any(
                item in resume_lower
                for item in ["technical skills", "skills", "programming"]
            ),
            "Projects": "project" in resume_lower,
            "Experience": any(
                item in resume_lower
                for item in ["experience", "internship", "work history"]
            ),
            "Certifications": any(
                item in resume_lower
                for item in ["certification", "certifications", "certificate"]
            )
        }

        completed_sections = sum(resume_sections.values())
        total_sections = len(resume_sections)

        section_completeness = round(
            (completed_sections / total_sections) * 100, 2
        )

        resume_certifications = extract_certifications(resume_text)

        jd_certifications = extract_certifications(job_desc)

        # Analyze individual resume projects

        project_analysis = analyze_projects(
            resume_text,
            job_desc
        )

        # Compare certifications

        matched_certifications = sorted(
            set(resume_certifications) & set(jd_certifications)
        )

        missing_certifications = sorted(
            set(jd_certifications) - set(resume_certifications)
        )

        jd_skills = set(extract_skills(job_desc))

        # 4. Find matched and missing skills

        matched_skills = sorted(
            jd_skills & resume_skills
        )

        missing_skills = sorted(
            jd_skills - resume_skills
        )

        # Intelligent Skill Gap Recommendations

        skill_recommendations = {
            "python": "Learn Python fundamentals and practical programming.",
            "sql": "Practice SQL queries, joins and database management.",
            "machine learning": "Study ML algorithms and model evaluation.",
            "flask": "Build web applications using Flask.",
            "django": "Learn Django and backend development.",
            "aws": "Learn cloud computing and AWS fundamentals.",
            "git": "Practice version control using Git.",
            "c++": "Study C++ and object-oriented programming.",
            "react": "Learn React components and frontend development.",
            "communication": "Improve professional communication skills.",
            "teamwork": "Develop collaboration and teamwork skills.",
            "problem solving": "Practice logical reasoning and coding problems.",
            "microsoft azure": "Study Microsoft Azure fundamentals.",
            "technical documentation": "Practice writing technical documentation."
        }

        job_desc_lower = job_desc.lower()

        skill_gap_recommendations = []

        for skill in missing_skills:

            occurrences = job_desc_lower.count(skill.lower())

            if occurrences >= 3:
                priority = "High"
            elif occurrences >= 2:
                priority = "Medium"
            else:
                priority = "Low"

            skill_gap_recommendations.append({
                "skill": skill,
                "priority": priority,
                "recommendation": skill_recommendations.get(
                    skill,
                    f"Learn {skill} and practice it through projects."
                )
            })

        # 5. Calculate skill score

        skill_score = calculate_skill_score(
            resume_skills,
            jd_skills
        )

        # 6. Calculate education score

        education_score = calculate_education_score(
            resume_text,
            job_desc
        )

        # 7. Calculate project and experience scores

        if project_analysis:

            project_score = round(
                sum(
                    project["relevance_score"]
                    for project in project_analysis
                ) / len(project_analysis),
                2
            )

        else:
            project_score = 0.0

        experience_score = calculate_experience_score(
            resume_text,
            job_desc
        )

        # 8. Calculate final weighted score

        match_score = calculate_weighted_score(
            skill_score,
            semantic_score,
            education_score,
            project_score,
            experience_score
        )

        # 9. Generate intelligent resume improvement suggestions

        suggestions = []

        resume_lower = resume_text.lower()

        # Missing technical skills

        if missing_skills:
            suggestions.append(
                "Add relevant missing technical skills to your resume "
                "only after gaining practical knowledge of them."
            )

        # Improve project descriptions

        if project_analysis and all(
            len(project.get("description", "").split()) < 25
            for project in project_analysis
        ):
            suggestions.append(
                "Your project descriptions are brief. Explain the "
                "problem, technologies used, your contribution and outcome."
            )

        # Add measurable achievements

        achievement_keywords = [
            "%", "increased", "reduced", "improved",
            "achieved", "saved", "accuracy"
        ]

        if not any(
            keyword in resume_lower
            for keyword in achievement_keywords
        ):
            suggestions.append(
                "Add measurable achievements to your resume where possible, "
                "such as accuracy, performance improvements or project results."
            )

        # Use action verbs

        action_verbs = [
            "developed", "implemented", "designed",
            "created", "built", "analyzed", "deployed"
        ]

        if not any(
            verb in resume_lower
            for verb in action_verbs
        ):
            suggestions.append(
                "Use strong action verbs such as Developed, Implemented, "
                "Designed and Created to describe your work."
            )

        # Resume length

        if len(resume_text.split()) < 150:
            suggestions.append(
                "Your resume seems short. Add relevant details about "
                "your skills, education, projects and experience."
            )

        # Experience and project sections

        if not any(
            heading in resume_lower
            for heading in ["experience", "work", "project"]
        ):
            suggestions.append(
                "Consider adding a clearly labelled Experience or "
                "Projects section."
            )

        # Standard resume headings

        standard_headings = [
            "education", "skills", "projects",
            "experience", "certifications"
        ]

        missing_headings = [
            heading for heading in standard_headings
            if heading not in resume_lower
        ]

        if len(missing_headings) >= 3:
            suggestions.append(
                "Improve resume organization by adding clear standard "
                "headings such as Education, Skills, Projects and Certifications."
            )

        # Resume Improvement Scorecard

        achievement_score = 20 if any(
            keyword in resume_lower
            for keyword in [
                "%", "increased", "reduced", "improved",
                "achieved", "saved", "accuracy"
            ]
        ) else 0

        action_verb_score = 15 if any(
            verb in resume_lower
            for verb in [
                "developed", "implemented", "designed",
                "created", "built", "analyzed", "deployed"
            ]
        ) else 0

        project_scorecard = 15 if (
            project_analysis and any(
                len(project.get("description", "").split()) >= 25
                for project in project_analysis
            )
        ) else 0

        length_score = 10 if len(resume_text.split()) >= 150 else 0

        section_score = round(section_completeness * 0.40)

        resume_improvement_score = (
            section_score
            + achievement_score
            + action_verb_score
            + project_scorecard
            + length_score
        )

        resume_scorecard = {
            "sections": section_score,
            "achievements": achievement_score,
            "action_verbs": action_verb_score,
            "projects": project_scorecard,
            "length": length_score,
            "total": resume_improvement_score
        }

        # ATS Compatibility Checker
        # Rule-based estimate, not a guarantee of ATS parsing

        ats_checks = {
            "Contact details": bool(
                re.search(
                    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                    resume_text
                )
            ) and bool(
                re.search(
                    r"(?:\+?\d[\d\s().-]{7,}\d)",
                    resume_text
                )
            ),

            "Standard section headings": sum(
                1 for heading in [
                    "education", "skills", "projects", "experience"
                ]
                if re.search(
                    r"\b" + re.escape(heading) + r"\b",
                    resume_lower
                )
            ) >= 3,

            "Readable text extraction": len(resume_text.split()) >= 100,

            "Job keyword coverage": bool(jd_skills) and (
                len(matched_skills) / max(len(jd_skills), 1)
            ) >= 0.5,

            "Supported document format": (
                os.path.splitext(filename)[1].lower()
                in {".pdf", ".docx"}
            )
        }

        ats_score = round(
            sum(ats_checks.values()) / len(ats_checks) * 100,
            2
        )

        # ATS Keyword Match Percentage

        total_jd_keywords = len(matched_skills) + len(missing_skills)

        keyword_match_percentage = (
            round(
                (len(matched_skills) / total_jd_keywords) * 100,
                2
            )
            if total_jd_keywords > 0
            else 0
        )

        ats_recommendations = []

        if not ats_checks["Contact details"]:
            ats_recommendations.append(
                "Include a clearly written email address and phone number in your resume."
            )

        if not ats_checks["Standard section headings"]:
            ats_recommendations.append(
                "Use standard headings such as Education, Skills, Projects and Experience."
            )

        if not ats_checks["Readable text extraction"]:
            ats_recommendations.append(
                "Use selectable text and avoid image-only resume pages."
            )

        if not ats_checks["Job keyword coverage"]:
            ats_recommendations.append(
                "Where accurate, include relevant skills and terms from the job description."
            )

        if not ats_recommendations:
            ats_recommendations.append(
                "Your resume passed all checks in this basic ATS screening. "
                "Review formatting in the target application as well."
            )

        # Generate downloadable PDF report

        report_data = {
            "match_score": match_score,
            "skill_score": skill_score,
            "semantic_score": semantic_score,
            "education_score": education_score,
            "project_score": project_score,
            "resume_scorecard": resume_scorecard,
            "ats_score": ats_score,
            "ats_checks": ats_checks,
            "ats_recommendations": ats_recommendations,
            "experience_score": experience_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_gap_recommendations": skill_gap_recommendations,
            "section_completeness": section_completeness,
            "resume_sections": resume_sections,
            "project_analysis": project_analysis,
            "keyword_match_percentage": keyword_match_percentage,
            "resume_certifications": resume_certifications,
            "jd_certifications": jd_certifications,
            "matched_certifications": matched_certifications,
            "missing_certifications": missing_certifications,
            "suggestions": suggestions
        }

        report_filename = f"{uuid.uuid4().hex}_report.pdf"

        report_folder = os.path.join(
            app.instance_path,
            "reports"
        )

        os.makedirs(report_folder, exist_ok=True)

        report_path = os.path.join(
            report_folder,
            report_filename
        )

        generate_report(report_data, report_path)

        # Remove expired reports after generating a new report

        cleanup_old_reports(report_folder)

        print("PDF GENERATED:", report_path)
        print("FILE EXISTS:", os.path.exists(report_path))

        # 10. Display results

        return render_template(
            'result.html',
            match_score=match_score,
            skill_score=skill_score,
            semantic_score=semantic_score,
            education_score=education_score,
            project_score=project_score,
            experience_score=experience_score,
            report_filename=report_filename,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            resume_certifications=resume_certifications,
            jd_certifications=jd_certifications,
            matched_certifications=matched_certifications,
            missing_certifications=missing_certifications,
            project_analysis=project_analysis,
            resume_text=resume_text,
            job_desc=job_desc,
            resume_sections=resume_sections,
            resume_scorecard=resume_scorecard,
            ats_score=ats_score,
            keyword_match_percentage=keyword_match_percentage,
            ats_checks=ats_checks,
            ats_recommendations=ats_recommendations,
            completed_sections=completed_sections,
            total_sections=total_sections,
            section_completeness=section_completeness,
            skill_gap_recommendations=skill_gap_recommendations,
            suggestions=suggestions
        )

    except Exception:

        app.logger.exception("Resume analysis failed")

        return (
            "Unable to analyze this resume. Please check the uploaded file.",
            500
        )

    finally:
        # Always delete the temporary uploaded resume

        if os.path.isfile(save_path):
            os.remove(save_path)


# =========================================================
# 7. PDF REPORT CLEANUP
# =========================================================

def cleanup_old_reports(report_folder, max_age=3600):

    if not os.path.exists(report_folder):
        return

    current_time = time.time()

    for filename in os.listdir(report_folder):

        file_path = os.path.join(report_folder, filename)

        if os.path.isfile(file_path):

            file_age = current_time - os.path.getmtime(file_path)

            if file_age > max_age:
                os.remove(file_path)


def scheduled_report_cleanup():
    """Delete generated PDF reports older than one hour."""

    report_folder = os.path.join(
        app.instance_path,
        "reports"
    )

    cleanup_old_reports(report_folder)


# =========================================================
# 8. DOWNLOAD PDF REPORT
# =========================================================

@app.route('/download-report/<filename>')
def download_report(filename):

    from werkzeug.utils import safe_join

    report_folder = os.path.join(
        app.instance_path,
        "reports"
    )

    cleanup_old_reports(report_folder)

    report_path = safe_join(report_folder, filename)

    if not report_path or not os.path.isfile(report_path):
        return "Report not found or expired.", 404

    if not filename.endswith("_report.pdf"):
        return "Invalid report file.", 400

    return send_file(
        report_path,
        as_attachment=True,
        download_name="Resume_Analysis_Report.pdf"
    )


# =========================================================
# 9. COMPANY-BASED MOCK INTERVIEW
# =========================================================

@app.route('/start-interview', methods=['POST'])
@limiter.limit("3 per minute")
def start_interview():

    resume_text = request.form.get('resume_text', '').strip()
    job_desc = request.form.get('job_description', '').strip()

    if not resume_text or not job_desc:
        return "Resume and job description are required.", 400

    questions = generate_interview_questions(
        job_desc,
        resume_text
    )

    return render_template(
        'interview.html',
        questions=questions,
        total_questions=len(questions),
        resume_text=resume_text,
        job_desc=job_desc
    )


# =========================================================
# 10. MOCK INTERVIEW EVALUATION
# =========================================================

@app.route('/evaluate-interview', methods=['POST'])
@limiter.limit("3 per minute")
def evaluate_interview():

    resume_text = request.form.get('resume_text', '').strip()
    job_desc = request.form.get('job_description', '').strip()

    answers = json.loads(request.form.get('answers', '[]'))
    questions = json.loads(request.form.get('questions', '[]'))

    if len(answers) != 20 or len(questions) != 20:
        return "Invalid interview submission.", 400

    results = []
    total_score = 0

    for index, item in enumerate(questions):

        answer = answers[index].strip()

        evaluation = evaluate_answer(
            item["question"],
            answer,
            job_desc,
            resume_text
        )

        score = evaluation["score"]
        total_score += score

        results.append({
            "question": item["question"],
            "category": item["category"],
            "answer": answer,
            "score": score,
            "feedback": evaluation["feedback"],
            "breakdown": evaluation["breakdown"],
            "grammar_feedback": evaluation.get("grammar_feedback", []),
            "suggested_answer": evaluation.get("suggested_answer", "")
        })

    overall_score = round(total_score / 20, 2)

    return render_template(
        'interview_result.html',
        results=results,
        overall_score=overall_score,
        total_questions=20,
        resume_text=resume_text,
        job_desc=job_desc
    )


# =========================================================
# 11. RUN APPLICATION AND BACKGROUND SCHEDULER
# =========================================================

if __name__ == '__main__':

    # Run one cleanup immediately when the application starts

    scheduled_report_cleanup()

    # Run report cleanup every 10 minutes while the app is running

    scheduler = BackgroundScheduler(daemon=True)

    scheduler.add_job(
        func=scheduled_report_cleanup,
        trigger="interval",
        minutes=10,
        id="report_cleanup",
        replace_existing=True
    )

    scheduler.start()

    print("Background report cleanup started!")

    try:
        app.run(
            debug=False,
            use_reloader=False
        )

    finally:
        scheduler.shutdown(wait=False)
