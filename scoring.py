
import re


# 1. Experience Matching Score


def calculate_experience_score(resume_text, job_desc):

    resume = resume_text.lower()
    job = job_desc.lower()

    # Detect fresher-friendly job requirements
    fresher_keywords = [
        "fresher", "freshers", "entry level",
        "entry-level", "no experience required",
        "0-1 year", "0-2 years"
    ]

    accepts_freshers = any(
        keyword in job for keyword in fresher_keywords
    )

    # Detect required years
    experience_match = re.search(
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)',
        job
    )

    required_years = (
        float(experience_match.group(1))
        if experience_match else 0
    )

    # Detect internships
    internship_keywords = [
        "internship", "intern", "trainee", "interned"
    ]

    has_internship = any(
        keyword in resume for keyword in internship_keywords
    )

    # Detect professional employment
    employment_keywords = [
        "professional experience",
        "employment history",
        "full-time",
        "full time",
        "worked as",
        "work history"
    ]

    has_employment = any(
        keyword in resume for keyword in employment_keywords
    )

    # Fresher-friendly positions
    if accepts_freshers and required_years <= 2:

        if has_employment:
            return 100.0

        if has_internship:
            return 95.0

        return 85.0

    # Jobs with explicit experience requirements
    if required_years > 0:

        if has_employment:
            return 80.0

        if has_internship:
            return 50.0

        return 0.0

    # No explicit experience requirement
    if has_employment:
        return 100.0

    if has_internship:
        return 85.0

    return 60.0



# 2. Skill Matching Score

def calculate_skill_score(resume_skills, job_skills):

    resume_skills = set(resume_skills)
    job_skills = set(job_skills)

    if not job_skills:
        return 0.0

    matched_skills = resume_skills.intersection(job_skills)

    score = (
        len(matched_skills) / len(job_skills)
    ) * 100

    return round(score, 2)


# 3. Weighted Final Score

def calculate_weighted_score(
    skill_score,
    semantic_score,
    education_score,
    project_score,
    experience_score
):

    final_score = (
        skill_score * 0.40
        + semantic_score * 0.25
        + education_score * 0.10
        + project_score * 0.15
        + experience_score * 0.10
    )

    return round(final_score, 2)


# 4. Education Matching Score


def calculate_education_score(resume_text, job_desc):

    resume = resume_text.lower()
    job = job_desc.lower()

    # Degree categories
    degree_patterns = {
        "engineering_bachelor": [
            r"\bb\.?e\.?\b",
            r"\bb\.?tech\b",
            r"\bbachelor of engineering\b",
            r"\bbachelor of technology\b",
            r"\bengineering graduate\b"
        ],
        "general_bachelor": [
            r"\bbachelor(?:'s)? degree\b",
            r"\bb\.?sc\b",
            r"\bbca\b",
            r"\bbba\b"
        ],
        "master": [
            r"\bmaster(?:'s)? degree\b",
            r"\bm\.?tech\b",
            r"\bm\.?e\.?\b",
            r"\bmca\b",
            r"\bm\.?sc\b",
            r"\bmba\b"
        ],
        "diploma": [
            r"\bdiploma\b"
        ]
    }

    # Detect required degree category
    required_category = None

    if any(re.search(p, job) for p in degree_patterns["engineering_bachelor"]):
        required_category = "engineering_bachelor"

    elif any(re.search(p, job) for p in degree_patterns["master"]):
        required_category = "master"

    elif any(re.search(p, job) for p in degree_patterns["general_bachelor"]):
        required_category = "general_bachelor"

    elif any(re.search(p, job) for p in degree_patterns["diploma"]):
        required_category = "diploma"

    # No clear education requirement
    if required_category is None:
        return 100.0

    # Check candidate degree
    candidate_has_degree = any(
        re.search(pattern, resume)
        for pattern in degree_patterns[required_category]
    )

    # Also accept engineering bachelor's degrees
    # for a general bachelor's requirement
    if required_category == "general_bachelor":
        candidate_has_degree = candidate_has_degree or any(
            re.search(pattern, resume)
            for pattern in degree_patterns["engineering_bachelor"]
        )

    if not candidate_has_degree:
        return 0.0

    # Branch matching only when explicitly specified
    branches = {
        "computer science": [
            r"\bcomputer science\b",
            r"\bcse\b"
        ],
        "information technology": [
            r"\binformation technology\b"
        ],
        "electronics": [
            r"\belectronics and communication\b",
            r"\bece\b"
        ],
        "electrical": [
            r"\belectrical and electronics\b",
            r"\beee\b"
        ],
        "mechanical": [
            r"\bmechanical engineering\b"
        ],
        "civil": [
            r"\bcivil engineering\b"
        ],
        "artificial intelligence": [
            r"\bartificial intelligence\b",
            r"\bai and ml\b",
            r"\baiml\b"
        ]
    }

    required_branches = [
        name for name, patterns in branches.items()
        if any(re.search(pattern, job) for pattern in patterns)
    ]

    # If no specialization is required, degree match is sufficient
    if not required_branches:
        return 100.0

    candidate_branches = [
        name for name, patterns in branches.items()
        if any(re.search(pattern, resume) for pattern in patterns)
    ]

    # Full match if any required branch is present
    if any(branch in candidate_branches for branch in required_branches):
        return 100.0

    # Degree matches, but specialization does not
    return 60.0


    if not bachelors_required:
        return 100.0

    degree_keywords = [
        "b.e.",
        "b.e ",
        "b.tech",
        "be ",
        "bachelor of engineering",
        "bachelor of technology",
        "bachelor's degree",
        "bachelors degree"
    ]

    if any(keyword in resume for keyword in degree_keywords):
        return 100.0

    return 0.0


# 5. Project Relevance Score


# ==========================================
# PROJECT RELEVANCE SCORE
# ==========================================


def calculate_project_score(resume_text, job_desc):

    resume = resume_text.lower()
    job = job_desc.lower()

    # Identify project section
    project_headings = [
        "projects",
        "academic projects",
        "personal projects",
        "technical projects",
        "project experience"
    ]

    project_text = ""

    for heading in project_headings:
        if heading in resume:
            project_text += resume.split(heading, 1)[1]

    if not project_text.strip():
        project_text = resume

    # Technology matching
    technology_keywords = [
        "python", "java", "c++", "kotlin",
        "javascript", "typescript", "sql",
        "mysql", "mongodb", "html", "css",
        "react", "flask", "django", "fastapi",
        "rest api", "machine learning",
        "deep learning", "artificial intelligence",
        "data science", "data analytics",
        "pandas", "numpy", "scikit-learn",
        "tensorflow", "keras", "opencv",
        "power bi", "tableau", "aws", "azure",
        "docker", "git", "jetpack compose",
        "mvvm", "android development"
    ]

    job_technologies = [
        tech for tech in technology_keywords
        if tech in job
    ]

    matched_technologies = [
        tech for tech in job_technologies
        if tech in project_text
    ]

    if job_technologies:
        technology_score = (
            len(matched_technologies) /
            len(job_technologies)
        ) * 100
    else:
        technology_score = 50

    # Development evidence
    development_keywords = [
        "developed", "designed", "implemented",
        "created", "built", "deployed",
        "automated", "analyzed", "predicted",
        "visualized", "integrated"
    ]

    development_score = min(
        sum(keyword in project_text for keyword in development_keywords) * 10,
        100
    )

    # Project functionality
    functionality_keywords = [
        "application", "system", "dashboard",
        "model", "api", "database",
        "frontend", "backend", "prediction",
        "classification", "clustering",
        "visualization", "integration"
    ]

    functionality_score = min(
        sum(keyword in project_text for keyword in functionality_keywords) * 10,
        100
    )

    # Final score
    final_score = (
        technology_score * 0.50
        + development_score * 0.25
        + functionality_score * 0.25
    )

    return round(final_score, 2)


# ==========================================
# PROJECT-LEVEL ANALYSIS ENGINE
# ==========================================

import re


# 1. Technology Database

TECHNOLOGIES = [
    "python", "java", "c++", "javascript", "typescript",
    "sql", "mysql", "mongodb", "html", "css", "react",
    "flask", "django", "node.js", "machine learning",
    "deep learning", "artificial intelligence",
    "data science", "data analytics", "data visualization",
    "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "opencv", "power bi", "tableau", "excel",
    "aws", "azure", "google cloud", "linux", "docker",
    "kubernetes", "git", "github", "k-means",
    "random forest", "logistic regression", "decision tree",
    "rest api", "computer networks", "network security",
    "database management",     "kotlin",
    "jetpack compose",
    "android development",
    "android studio",
    "mvvm",
    "nominatim",
    "osrm",
    "sharedpreferences",
    "haversine formula",
    "mobile app development",
    "keras",
    "mobilenetv2",
    "fastapi",
    "transfer learning",
    "deepfake detection",
    "image processing",
    "api integration"
]


# 2. Technology Aliases

ALIASES = {
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "powerbi": "power bi",
    "nodejs": "node.js",
    "jetpackcompose": "jetpack compose",
    "shared preferences": "sharedpreferences",
    "mobile development": "mobile app development"
}


# 3. Resume Section Headings

PROJECT_HEADINGS = {
    "projects",
    "academic projects",
    "personal projects",
    "technical projects",
    "project experience"
}


OTHER_HEADINGS = {
    "education",
    "skills",
    "technical skills",
    "experience",
    "work experience",
    "internships",
    "certifications",
    "achievements",
    "awards",
    "summary",
    "objective",
    "languages",
    "interests",
    "publications",
    "references"
}


# 4. Development Keywords

DEV_KEYWORDS = [
    "developed",
    "designed",
    "implemented",
    "created",
    "built",
    "deployed",
    "automated",
    "analyzed",
    "predicted",
    "visualized"
]


# 5. Technology Extraction

def _find_techs(text):

    text = text.lower()

    found = set()

    for tech in TECHNOLOGIES + list(ALIASES):

        pattern = (
            r"(?<![\w+#])"
            + re.escape(tech)
            + r"(?![\w+#])"
        )

        if re.search(pattern, text):

            found.add(ALIASES.get(tech, tech))

    return found


# 6. Extract Project Section

def _extract_project_section(resume_text):

    lines = resume_text.splitlines()

    start = None

    for i, line in enumerate(lines):

        heading = line.strip().strip(":").lower()

        if heading in PROJECT_HEADINGS:

            start = i + 1
            break

    if start is None:
        return []

    section = []

    for line in lines[start:]:

        heading = line.strip().strip(":").lower()

        if heading in OTHER_HEADINGS:
            break

        section.append(line)

    return section


# 7. Identify Project Titles

def _is_title(line, prev_line):

    words = line.split()

    return (
        0 < len(words) <= 8
        and not re.match(r"^[-•*▪●]", line)
        and not line.endswith((".", ",", ";"))
        and line[0].isupper()
        and (
            prev_line is None
            or prev_line.endswith((".", ":"))
        )
    )


# 8. Separate Individual Projects

def _split_projects(section_lines):

    blocks = []
    current = []

    # First try separating projects using blank lines

    for line in section_lines:

        if line.strip():

            current.append(line.strip())

        elif current:

            blocks.append(current)
            current = []

    if current:
        blocks.append(current)

    # Fallback: detect titles if blank lines are unavailable

    if len(blocks) <= 1:

        lines = [
            line.strip()
            for line in section_lines
            if line.strip()
        ]

        blocks = []
        current = []
        prev = None

        for line in lines:

            if current and _is_title(line, prev):

                blocks.append(current)
                current = []

            current.append(line)

            prev = line

        if current:
            blocks.append(current)

    projects = []

    for block in blocks:

        title = block[0]

        description = " ".join(block[1:])

        if len(title) + len(description) > 20:

            projects.append((title, description))

    return projects


# 9. Analyze Individual Projects

def analyze_projects(resume_text, job_desc):

    job_technologies = sorted(
        _find_techs(job_desc)
    )

    project_entries = _split_projects(
        _extract_project_section(resume_text)
    )

    results = []

    for title, description in project_entries[:10]:

        full_text = f"{title} {description}"

        # Extract all project technologies

        project_technologies = _find_techs(full_text)

        # Identify technologies matching the job

        matched = sorted(
            project_technologies & set(job_technologies)
        )

        # Identify additional technologies

        extra = sorted(
            project_technologies - set(job_technologies)
        )

        # Technology relevance score

        if job_technologies:

            technology_score = (
                len(matched) / len(job_technologies)
            ) * 100

        else:

            technology_score = 0.0

        # Development evidence score

        development_matches = [
            keyword
            for keyword in DEV_KEYWORDS
            if keyword in full_text.lower()
        ]

        development_score = min(
            len(development_matches) * 20,
            100
        )

        # Technology breadth score

        breadth_score = min(
            len(project_technologies) * 10,
            100
        )
        
        # Final project relevance score

        relevance_score = (
            technology_score * 0.65
            + development_score * 0.20
            + breadth_score * 0.15
        )

        results.append({

            "project_name": title[:100],

            "description": description,

            "technologies": matched,

            "all_technologies": sorted(
                project_technologies
            ),

            "extra_technologies": extra,

            "technology_score": round(
                technology_score, 2
            ),

            "development_score": round(
    development_score, 2
),

"breadth_score": round(
    breadth_score, 2
),

"relevance_score": round(
    relevance_score, 2
)

        })

    # Rank projects by relevance

    return sorted(
        results,
        key=lambda project: -project["relevance_score"]
    )
