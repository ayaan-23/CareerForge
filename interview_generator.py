
import random
import re

def generate_interview_questions(
    job_desc,
    resume_text,
    project_analysis=None
):
    job_desc = job_desc.lower()
    resume_text = resume_text.lower()

    project_analysis = project_analysis or []

    questions = {
        "Technical": [],
        "Project": [],
        "Scenario": [],
        "HR": []
    }

    # Technical question bank
    technical_bank = {
        "python": [
            "Explain the difference between a list and a tuple in Python.",
            "What are Python decorators and where would you use them?",
            "Explain exception handling in Python."
        ],
        "sql": [
            "Explain the difference between WHERE and HAVING.",
            "What are SQL joins? Explain their different types.",
            "How would you find duplicate records in a SQL table?"
        ],
        "java": [
            "Explain the four main principles of OOP.",
            "What is the difference between an interface and an abstract class?",
            "Explain exception handling in Java."
        ],
        "machine learning": [
            "Explain the difference between supervised and unsupervised learning.",
            "What is overfitting and how can you prevent it?",
            "Explain how you would evaluate a machine learning model."
        ],
        "flask": [
            "What is Flask and how does its routing system work?",
            "How would you handle file uploads in Flask?",
            "How do you connect a Flask application to a database?"
        ],
        "react": [
            "What are React components and props?",
            "Explain the purpose of React hooks.",
            "What is the difference between state and props?"
        ],
        "django": [
            "Explain Django's MVT architecture.",
            "What is Django ORM?",
            "How does Django handle URL routing?"
        ],
        "c++": [
            "Explain pointers and references in C++.",
            "What is inheritance in C++?",
            "Explain the difference between a stack and a heap."
        ],
        "javascript": [
            "Explain the difference between let, const and var.",
            "What are promises in JavaScript?",
            "Explain event handling in JavaScript."
        ],
        "power bi": [
            "What is the difference between a measure and a calculated column?",
            "What is DAX in Power BI?",
            "How would you design an effective business dashboard?"
        ]
    }

    # Identify technologies actually mentioned in the JD
    for technology, bank in technical_bank.items():
        if technology in job_desc:
            questions["Technical"].extend(bank)

    # General technical questions if few technologies are detected
    general_technical = [
        "How do you approach debugging a technical problem?",
        "How do you choose the right technology for a project?",
        "How do you ensure code quality and maintainability?"
    ]

    # Project questions based on detected resume projects
    for project in project_analysis[:5]:

        project_name = project.get(
            "project_name", "your project"
        )

        questions["Project"].extend([
            f"Explain the architecture and purpose of {project_name}.",
            f"What was your individual contribution to {project_name}?",
            f"What technical challenges did you face while developing {project_name}?"
        ])

    if not questions["Project"]:
        questions["Project"] = [
            "Explain the most important project in your resume.",
            "What technologies did you use in your project?",
            "What challenges did you face while developing your project?"
        ]

    # Scenario questions based on job responsibilities
    questions["Scenario"] = [
        "How would you handle an urgent task with a strict deadline?",
        "What would you do if you discovered a major error in your work?",
        "How would you handle a technical problem you could not solve immediately?",
        "How would you prioritize multiple tasks assigned by your manager?",
        "How would you handle a disagreement with a teammate?"
    ]

    # HR questions
    questions["HR"] = [
        "Tell me about yourself and your professional background.",
        "Why do you want to join this company?",
        "What are your greatest strengths and weaknesses?",
        "Where do you see yourself in the next five years?"
    ]

    # Select questions without duplication
    
    # Professional question bank: 50 questions

    technical_fallback = [
        "Explain the four principles of object-oriented programming.",
        "What is the difference between a compiler and an interpreter?",
        "Explain the difference between a stack and a queue.",
        "What is the difference between process and thread?",
        "Explain database normalization.",
        "What are primary keys and foreign keys?",
        "Explain the difference between TCP and UDP.",
        "What is the difference between HTTP and HTTPS?",
        "How does exception handling work?",
        "What is the difference between an array and a linked list?",
        "Explain time complexity and Big O notation.",
        "What is the difference between supervised and unsupervised learning.",
        "What is overfitting in machine learning?",
        "How do you debug an application?",
        "Explain the software development life cycle.",
        "What is version control and why is Git useful?",
        "What is an API and how does it work?",
        "Explain the difference between frontend and backend development.",
        "How do you ensure code quality?",
        "How do you approach learning a new technology?"
    ]

    project_fallback = [
        "What was your individual contribution to your project?",
        "What was the biggest challenge in your project?",
        "How did you test your project?",
        "Why did you choose the technologies used in your project?",
        "How did you divide the work during development?",
        "What improvements would you make to your project?",
        "How did you handle errors during development?",
        "Explain your project architecture.",
        "What did you learn from completing your project?",
        "How would you explain your project to a non-technical person?"
    ]

    scenario_bank = [
        "How would you handle an urgent task with a strict deadline?",
        "What would you do if you discovered a major error in your work?",
        "How would you handle a technical problem you could not solve?",
        "How would you prioritize multiple tasks?",
        "How would you handle a disagreement with a teammate?",
        "What would you do if you received negative feedback?",
        "How would you respond to an unhappy customer?",
        "What would you do if your team member missed a deadline?",
        "How would you adapt to an unexpected change in requirements?",
        "How would you handle multiple responsibilities at the same time?"
    ]

    hr_bank = [
        "Tell me about yourself.",
        "Why do you want to join our company?",
        "What are your greatest strengths?",
        "What is one weakness you are working to improve?",
        "Where do you see yourself in five years?",
        "Why should we hire you?",
        "What motivates you professionally?",
        "How do you handle constructive criticism?",
        "Describe a situation where you demonstrated teamwork.",
        "What are your short-term career goals?"
    ]

    def unique_questions(items):
        result = []
        seen = set()

        for item in items:
            question = item.strip()
            key = question.casefold()

            if question and key not in seen:
                result.append(question)
                seen.add(key)

        return result

    technical_pool = unique_questions(
        questions["Technical"] + technical_fallback
    )

    project_pool = unique_questions(
        questions["Project"] + project_fallback
    )

    scenario_pool = unique_questions(
        questions["Scenario"] + scenario_bank
    )

    hr_pool = unique_questions(
        questions["HR"] + hr_bank
    )

    # Select 6 unique technical questions
    selected_technical = random.sample(technical_pool, 6)

    # Select 5 unique project questions
    selected_project = random.sample(project_pool, 5)

    # Select 5 unique scenario questions
    selected_scenario = random.sample(scenario_pool, 5)

    # Always ask this as the first question
    introduction_question = "Tell me about yourself."

    # Select 3 additional HR questions
    remaining_hr = [
        q for q in hr_pool
        if q.casefold() != introduction_question.casefold()
    ]

    selected_hr = random.sample(remaining_hr, 3)

    # Build exactly 20 questions
    final_questions = [
        {
            "category": "HR",
            "question": introduction_question
        }
    ]

    for category, selected_list in [
        ("Technical", selected_technical),
        ("Project", selected_project),
        ("Scenario", selected_scenario),
        ("HR", selected_hr)
    ]:
        for question in selected_list:
            final_questions.append({
                "category": category,
                "question": question
            })

    # Keep introduction first and shuffle the remaining questions
    remaining_questions = final_questions[1:]
    random.shuffle(remaining_questions)

    final_questions = [final_questions[0]] + remaining_questions

    return final_questions



def evaluate_answer(question, answer, job_desc, resume_text):
    """
    Rule-based interview evaluation.
    Returns a score, feedback, and score breakdown.
    """

    question_answer_bank = {
        "tell me about yourself":
            "I am pursuing a Bachelor of Engineering in Computer Science. "
            "I have knowledge of Python, Java, SQL and machine learning. "
            "I have worked on projects involving predictive modelling, "
            "customer segmentation and AI-based image detection. "
            "These projects improved my technical and problem-solving skills. "
            "I am looking for an opportunity to apply my knowledge and grow professionally.",

        "software development life cycle":
            "SDLC is a structured process used to develop software. Its phases include "
            "planning, requirement analysis, design, development, testing, deployment "
            "and maintenance. It helps teams develop reliable software systematically.",

        "how did you test your project":
            "I used manual and functional testing to verify my project's features. "
            "I tested valid and invalid inputs, empty fields, error handling and integration. "
            "In my AI Resume Analyzer, I tested PDF and DOCX uploads, text extraction, "
            "job matching, skill analysis, scoring and PDF report generation.",

        "team member missed a deadline":
            "I would communicate with the team member to understand the reason for the delay. "
            "I would assess its impact, discuss solutions, offer support if necessary "
            "and coordinate with the team to complete the pending work.",

        "what did you learn from completing your project":
            "I learned how to convert theoretical knowledge into a practical application. "
            "I improved my programming, debugging, testing and problem-solving skills. "
            "I also learned the importance of teamwork and time management.",

        "multiple responsibilities":
            "I would prioritize tasks according to their importance and deadlines. "
            "I would divide large tasks into smaller activities, maintain a schedule "
            "and communicate with my team when support is needed.",

        "frontend and backend":
            "Frontend handles the user-facing interface of an application using technologies "
            "such as HTML, CSS and JavaScript. Backend handles server-side logic, databases "
            "and authentication. For example, a frontend displays products while the backend "
            "processes orders.",

        "disagreement with a teammate":
            "I would listen to my teammate's perspective, explain my opinion respectfully "
            "and discuss possible solutions. I would focus on project requirements "
            "and choose the solution that benefits the team.",

        "why do you want to join our company":
            "I want to join your company because it offers an opportunity to apply my knowledge, "
            "learn from experienced professionals and gain practical experience. "
            "I would like to contribute to the team while developing my professional skills.",

        "why did you choose the technologies":
            "I selected technologies based on project requirements, functionality, compatibility "
            "and ease of development. I considered whether each technology could handle "
            "the required features and support future maintenance.",

        "where and having":
            "WHERE filters individual rows before grouping, whereas HAVING filters grouped "
            "results after GROUP BY. WHERE is generally used with normal conditions, "
            "while HAVING can filter aggregate results such as COUNT and SUM.",

        "django handle url routing":
            "Django handles URL routing through URL patterns defined in urls.py. "
            "Each pattern maps a URL to a view function or class. The view processes "
            "the request and returns a response.",

        "project architecture":
            "My AI Resume Analyzer uses Flask as its backend. Users upload resumes "
            "and provide job descriptions. Python libraries extract and process resume text, "
            "perform matching and calculate scores. HTML templates display the results, "
            "and ReportLab generates PDF reports.",

        "most important project in your resume":
            "One important project in my resume is the AI-Based Deepfake Image Detection System. "
            "It focuses on identifying AI-generated or manipulated images using machine learning. "
            "This project helped me understand image processing, model development and evaluation.",

        "major error in your work":
            "I would identify the error, understand its impact and investigate the root cause. "
            "After fixing it, I would test the solution carefully and inform relevant team members.",

        "let, const and var":
            "Var is function-scoped and can be redeclared. Let is block-scoped and can be reassigned. "
            "Const is block-scoped and cannot be reassigned. Modern JavaScript generally "
            "prefers let and const.",

        "technical problem you could not solve":
            "I would break the problem into smaller parts, review documentation, examine error messages "
            "and try possible solutions. If necessary, I would seek guidance from an experienced "
            "team member and learn from the process.",

        "one weakness":
            "One weakness I am working to improve is my confidence in professional communication. "
            "I am improving through regular interview practice, discussions and explaining "
            "my projects clearly.",

      
        "tcp and udp":
            "TCP is connection-oriented and provides reliable data delivery. UDP is connectionless "
            "and has lower overhead but does not guarantee delivery. TCP is used where reliability "
            "is important, while UDP is useful for real-time applications.",

        "debug an application":
            "I would reproduce the issue, inspect error messages and logs, identify the root cause, "
            "fix the problem and test the application again.",

        "technologies did you use":
            "I have used Python, Pandas, NumPy, Scikit-learn and Power BI in my projects. "
            "For my AI Resume Analyzer, I used Python, Flask, PyMuPDF and Sentence Transformers.",

        "greatest strengths and weaknesses":
            "My strengths are willingness to learn, problem-solving and adaptability. "
            "I am improving my confidence in professional communication through regular practice.",

        "individual contribution":
            "I contributed by understanding requirements, completing assigned development tasks, "
            "testing features and collaborating with my teammates.",

        "django's mvt architecture":
            "Django follows Model-View-Template architecture. Model manages data, View handles "
            "application logic and Template manages the presentation layer.",

        "exception handling in python":
            "Python exception handling uses try, except, else and finally. Try contains code "
            "that may cause an error, except handles errors, else executes when there is no error "
            "and finally always executes.",

        "motivates you professionally":
            "I am motivated by learning new technologies, solving problems and achieving meaningful "
            "results. Practical projects encourage me to improve my skills.",

        "http and https":
            "HTTP is used for communication between browsers and servers. HTTPS is its secure version "
            "and uses TLS encryption to protect data during transmission.",

        "urgent task with a strict deadline":
            "I would understand the requirements, prioritize important activities, divide the work "
            "into smaller tasks and communicate any challenges early.",

        "next five years":
            "I see myself becoming a skilled professional with strong technical knowledge, practical "
            "experience and the ability to take on greater responsibilities.",

        "flask and how does its routing":
            "Flask is a lightweight Python web framework. Its routing system connects URLs to "
            "Python functions using route decorators.",

        "challenges did you face":
            "I faced challenges in understanding how different components worked together. "
            "I addressed them by breaking tasks into smaller parts, checking documentation "
            "and testing features individually.",

        "supervised and unsupervised":
            "Supervised learning uses labelled data for tasks such as classification and regression. "
            "Unsupervised learning uses unlabelled data to discover patterns. K-Means clustering "
            "is an example of unsupervised learning."
    }

    # Handle skipped questions
    if not answer or not answer.strip():
        question_lower = question.lower()

        suggested_answer = next(
            (
                value for key, value in question_answer_bank.items()
                if key in question_lower
            ),
            "Please provide a relevant answer with a clear explanation and practical example."
        )

        return {
            "score": 0,
            "feedback": ["No answer provided."],
            "breakdown": {
                "relevance": 0,
                "concept_coverage": 0,
                "explanation": 0,
                "examples": 0
            },
            "grammar_feedback": ["No answer available to check."],
            "suggested_answer": suggested_answer
        }

    # Prepare keywords
    stop_words = {
        "the", "and", "for", "with", "that", "this", "what",
        "how", "why", "when", "where", "which", "would",
        "could", "should", "your", "have", "from", "into",
        "about", "their", "there", "them", "then", "than",
        "you", "are", "was", "were", "been", "being",
        "can", "will", "has", "had", "does", "did",
        "explain", "describe", "tell", "give", "using"
    }

    def get_keywords(text):
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text.lower())
        return {
            word for word in words
            if len(word) > 2 and word not in stop_words
        }

    answer_words = get_keywords(answer)
    question_words = get_keywords(question)
    job_words = get_keywords(job_desc)
    resume_words = get_keywords(resume_text)

    # 1. Relevance to the question
    relevant_words = question_words.intersection(answer_words)

    relevance = min(
        100,
        round((len(relevant_words) / max(len(question_words), 1)) * 100)
    )

    # 2. Coverage of job and resume concepts
    context_words = job_words.union(resume_words)
    expected_words = question_words.intersection(context_words)

    if expected_words:
        covered_words = expected_words.intersection(answer_words)
        concept_coverage = min(
            100,
            round((len(covered_words) / len(expected_words)) * 100)
        )
    else:
        concept_coverage = relevance

    # 3. Explanation quality
    word_count = len(answer.split())

    if word_count >= 60:
        explanation = 100
    elif word_count >= 35:
        explanation = 75
    elif word_count >= 20:
        explanation = 50
    else:
        explanation = 20

    # 4. Supporting examples
    example_terms = [
        "example", "experience", "developed", "implemented",
        "created", "designed", "built", "tested", "project",
        "result", "because"
    ]

    has_example = any(term in answer.lower() for term in example_terms)
    examples = 100 if has_example else 30

    # Final weighted score
    score = round(
        relevance * 0.35 +
        concept_coverage * 0.35 +
        explanation * 0.20 +
        examples * 0.10
    )

    # Question-specific suggested answers
    question_lower = question.lower()

    suggested_answer = next(
        (
            value for key, value in question_answer_bank.items()
            if key in question_lower
        ),
        "Answer directly, explain your approach clearly and include a relevant practical example."
    )

    feedback = []

    if relevance < 40:
        feedback.append("Your answer needs to address the question more directly.")
    else:
        feedback.append("Your answer is relevant to the question.")

    if concept_coverage < 40:
        feedback.append("Include more concepts related to the job requirements and your resume.")
    else:
        feedback.append("You covered relevant job and resume concepts.")

    if explanation < 60:
        feedback.append("Explain your answer in more detail.")
    else:
        feedback.append("Your explanation has reasonable detail.")

    if not has_example:
        feedback.append("Add a practical example or project experience.")

    return {
        "score": score,
        "feedback": feedback,
        "breakdown": {
            "relevance": relevance,
            "concept_coverage": concept_coverage,
            "explanation": explanation,
            "examples": examples
        },
        "grammar_feedback": [],
        "suggested_answer": suggested_answer
    }
