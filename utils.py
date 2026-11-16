import re
CERTIFICATION_DICTIONARY = {

    # =====================================
    # AMAZON WEB SERVICES (AWS)
    # =====================================

    "aws cloud practitioner": [
        "aws certified cloud practitioner",
        "aws cloud practitioner",
        "clf-c02"
    ],
    "aws ai practitioner": [
        "aws certified ai practitioner",
        "aws ai practitioner",
        "aif-c01"
    ],
    "aws solutions architect associate": [
        "aws solutions architect associate",
        "aws certified solutions architect associate",
        "saa-c03"
    ],
    "aws solutions architect professional": [
        "aws solutions architect professional",
        "aws certified solutions architect professional",
        "sap-c02"
    ],
    "aws developer associate": [
        "aws certified developer associate",
        "aws developer associate",
        "dva-c02"
    ],
    "aws data engineer associate": [
        "aws certified data engineer associate",
        "aws data engineer associate",
        "dea-c01"
    ],
    "aws machine learning engineer associate": [
        "aws certified machine learning engineer associate",
        "aws machine learning engineer associate",
        "mla-c01"
    ],
    "aws cloudops engineer associate": [
        "aws certified cloudops engineer associate",
        "aws cloudops engineer associate",
        "soa-c03"
    ],
    "aws devops engineer professional": [
        "aws certified devops engineer professional",
        "aws devops engineer professional",
        "dop-c02"
    ],
    "aws security specialty": [
        "aws certified security specialty",
        "aws security specialty",
        "scs-c02"
    ],
    "aws advanced networking specialty": [
        "aws certified advanced networking specialty",
        "aws advanced networking specialty"
    ],

    # =====================================
    # MICROSOFT AND AZURE
    # =====================================

    "microsoft azure fundamentals": [
        "microsoft certified azure fundamentals",
        "azure fundamentals",
        "az-900"
    ],
    "microsoft azure ai fundamentals": [
        "azure ai fundamentals",
        "microsoft certified azure ai fundamentals",
        "ai-900",
        "ai-901"
    ],
    "microsoft azure data fundamentals": [
        "azure data fundamentals",
        "dp-900"
    ],
    "microsoft azure administrator associate": [
        "azure administrator associate",
        "az-104"
    ],
    "microsoft azure developer associate": [
        "azure developer associate",
        "az-204"
    ],
    "microsoft azure solutions architect expert": [
        "azure solutions architect expert",
        "az-305"
    ],
    "microsoft devops engineer expert": [
        "devops engineer expert",
        "az-400"
    ],
    "microsoft power bi data analyst": [
        "power bi data analyst associate",
        "pl-300",
        "microsoft certified power bi data analyst"
    ],
    "microsoft fabric analytics engineer": [
        "fabric analytics engineer associate",
        "dp-600"
    ],
    "microsoft fabric data engineer": [
        "fabric data engineer associate",
        "dp-700"
    ],
    "microsoft azure database administrator": [
        "azure database administrator associate",
        "dp-300"
    ],
    "microsoft security fundamentals": [
        "security compliance and identity fundamentals",
        "sc-900"
    ],
    "microsoft security operations analyst": [
        "security operations analyst associate",
        "sc-200"
    ],
    "microsoft azure ai engineer": [
        "azure ai engineer associate",
        "ai-102"
    ],
    "microsoft github foundations": [
        "github foundations",
        "gh-900"
    ],
    "microsoft github actions": [
        "github actions certification",
        "gh-200"
    ],

    # =====================================
    # GOOGLE CLOUD
    # =====================================

    "google cloud digital leader": [
        "google cloud digital leader",
        "cloud digital leader"
    ],
    "google associate cloud engineer": [
        "associate cloud engineer",
        "google associate cloud engineer"
    ],
    "google professional cloud architect": [
        "professional cloud architect",
        "google professional cloud architect"
    ],
    "google professional data engineer": [
        "professional data engineer",
        "google professional data engineer"
    ],
    "google professional cloud developer": [
        "professional cloud developer"
    ],
    "google professional cloud devops engineer": [
        "professional cloud devops engineer"
    ],
    "google professional cloud security engineer": [
        "professional cloud security engineer"
    ],
    "google professional machine learning engineer": [
        "professional machine learning engineer"
    ],
    "google professional cloud database engineer": [
        "professional cloud database engineer"
    ],
    "google data analytics certificate": [
        "google data analytics professional certificate",
        "google data analytics certificate"
    ],
    "google cybersecurity certificate": [
        "google cybersecurity certificate"
    ],

    # =====================================
    # CISCO
    # =====================================

    "cisco ccna": [
        "ccna",
        "cisco certified network associate",
        "200-301"
    ],
    "cisco ccnp enterprise": [
        "ccnp enterprise",
        "cisco certified network professional enterprise"
    ],
    "cisco ccnp security": [
        "ccnp security"
    ],
    "cisco ccie enterprise": [
        "ccie enterprise infrastructure",
        "ccie enterprise"
    ],
    "cisco cybersecurity associate": [
        "ccna cybersecurity",
        "cisco certified cybersecurity associate"
    ],
    "cisco ccst networking": [
        "ccst networking",
        "cisco certified support technician networking"
    ],
    "cisco ccst cybersecurity": [
        "ccst cybersecurity"
    ],
    "cisco python essentials 1": [
        "python essentials 1",
        "cisco python essentials 1"
    ],
    "cisco data analytics essentials": [
        "data analytics essentials",
        "cisco data analytics essentials"
    ],

    # =====================================
    # COMPTIA
    # =====================================

    "comptia a+": [
        "comptia a+",
        "comptia a plus"
    ],
    "comptia network+": [
        "comptia network+",
        "comptia network plus"
    ],
    "comptia security+": [
        "comptia security+",
        "comptia security plus"
    ],
    "comptia linux+": [
        "comptia linux+",
        "comptia linux plus"
    ],
    "comptia cloud+": [
        "comptia cloud+",
        "comptia cloud plus"
    ],
    "comptia data+": [
        "comptia data+",
        "comptia data plus"
    ],
    "comptia cybersecurity analyst": [
        "comptia cysa+",
        "comptia cybersecurity analyst"
    ],
    "comptia pentest+": [
        "comptia pentest+",
        "comptia pentest plus"
    ],
    "comptia securityx": [
        "comptia securityx"
    ],
    "comptia project+": [
        "comptia project+"
    ],

    # =====================================
    # ISC2 CYBERSECURITY
    # =====================================

    "isc2 certified in cybersecurity": [
        "isc2 certified in cybersecurity",
        "isc2 cc"
    ],
    "isc2 cissp": [
        "cissp",
        "certified information systems security professional"
    ],
    "isc2 ccsp": [
        "ccsp",
        "certified cloud security professional"
    ],
    "isc2 sscp": [
        "sscp",
        "systems security certified practitioner"
    ],
    "isc2 cgrc": [
        "cgrc",
        "certified in governance risk and compliance"
    ],

    # =====================================
    # ORACLE
    # =====================================

    "oracle java programmer": [
        "oracle certified professional java programmer",
        "oracle java se programmer"
    ],
    "oracle java associate": [
        "oracle certified associate java",
        "oca java"
    ],
    "oracle database sql": [
        "oracle database sql certified associate",
        "oracle sql certification"
    ],
    "oracle cloud infrastructure architect": [
        "oracle cloud infrastructure architect",
        "oci architect"
    ],
    "oracle cloud infrastructure foundations": [
        "oracle cloud infrastructure foundations",
        "oci foundations"
    ],
    "oracle cloud generative ai": [
        "oracle cloud infrastructure generative ai professional",
        "oci generative ai"
    ],

    # =====================================
    # IBM
    # =====================================

    "ibm data science professional certificate": [
        "ibm data science professional certificate",
        "ibm data science"
    ],
    "ibm ai engineering professional certificate": [
        "ibm ai engineering professional certificate",
        "ibm ai engineering"
    ],
    "ibm data analyst professional certificate": [
        "ibm data analyst professional certificate",
        "ibm data analyst"
    ],
    "ibm cybersecurity analyst": [
        "ibm cybersecurity analyst professional certificate"
    ],
    "ibm machine learning": [
        "ibm machine learning professional certificate"
    ],
    "ibm full stack software developer": [
        "ibm full stack software developer professional certificate"
    ],
    "ibm devops and software engineering": [
        "ibm devops and software engineering professional certificate"
    ],

    # =====================================
    # DATACAMP / DATA AND ANALYTICS
    # =====================================

    "databricks data engineer associate": [
        "databricks certified data engineer associate"
    ],
    "databricks machine learning associate": [
        "databricks certified machine learning associate"
    ],
    "databricks generative ai engineer associate": [
        "databricks certified generative ai engineer associate"
    ],
    "snowflake snowpro core": [
        "snowpro core certification",
        "snowflake snowpro core"
    ],
    "snowflake snowpro advanced data engineer": [
        "snowpro advanced data engineer",
        "snowflake data engineer"
    ],
    "tableau desktop specialist": [
        "tableau desktop specialist"
    ],
    "tableau certified data analyst": [
        "tableau certified data analyst"
    ],

    # =====================================
    # RED HAT AND LINUX
    # =====================================

    "red hat certified system administrator": [
        "red hat certified system administrator",
        "rhcsa"
    ],
    "red hat certified engineer": [
        "red hat certified engineer",
        "rhce"
    ],
    "linux foundation certified system administrator": [
        "linux foundation certified system administrator",
        "lfcs"
    ],
    "linux foundation certified it associate": [
        "linux foundation certified it associate",
        "lfca"
    ],

    # =====================================
    # KUBERNETES AND DEVOPS
    # =====================================

    "certified kubernetes administrator": [
        "certified kubernetes administrator",
        "cka"
    ],
    "certified kubernetes application developer": [
        "certified kubernetes application developer",
        "ckad"
    ],
    "certified kubernetes security specialist": [
        "certified kubernetes security specialist",
        "cks"
    ],
    "hashicorp terraform associate": [
        "hashicorp certified terraform associate",
        "terraform associate"
    ],
    "hashicorp vault associate": [
        "hashicorp certified vault associate",
        "vault associate"
    ],

    # =====================================
    # PROJECT MANAGEMENT AND AGILE
    # =====================================

    "pmi project management professional": [
        "project management professional",
        "pmp"
    ],
    "pmi certified associate in project management": [
        "certified associate in project management",
        "capm"
    ],
    "pmi agile certified practitioner": [
        "pmi agile certified practitioner",
        "pmi-acp"
    ],
    "scrum master certified": [
        "certified scrum master",
        "csm"
    ],
    "professional scrum master": [
        "professional scrum master",
        "psm i",
        "psm ii",
        "psm iii"
    ],
    "certified scrum product owner": [
        "certified scrum product owner",
        "cspo"
    ],
    "itil foundation": [
        "itil foundation",
        "itil 4 foundation"
    ],

    # =====================================
    # ISTQB SOFTWARE TESTING
    # =====================================

    "istqb certified tester foundation": [
        "istqb certified tester foundation level",
        "istqb ctfl"
    ],
    "istqb advanced test analyst": [
        "istqb advanced level test analyst"
    ],

    # =====================================
    # SECURITY AND AUDIT
    # =====================================

    "certified ethical hacker": [
        "certified ethical hacker",
        "ceh"
    ],
    "certified information systems auditor": [
        "certified information systems auditor",
        "cisa"
    ],
    "certified information security manager": [
        "certified information security manager",
        "cism"
    ],
    "certified in risk and information systems control": [
        "certified in risk and information systems control",
        "crisc"
    ],

    # =====================================
    # GENERAL AI AND DATA CERTIFICATES
    # =====================================
    "nptel certification": [
        "nptel online certification",
        "nptel course certificate"
    ],
    "simplilearn certification": [
        "simplilearn certificate",
        "simplilearn certification"
    ],
    "coursera professional certificate": [
        "coursera professional certificate"
    ],
    "udacity nanodegree": [
        "udacity nanodegree"
    ]
}

# ==========================================
# SKILL DICTIONARY
# ==========================================

SKILL_DICTIONARY = {

    # Programming Languages
    "python": ["python", "python programming"],
    "java": ["java", "java programming"],
    "c": ["c programming", "c language"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "c sharp"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript"],
    "kotlin": ["kotlin"],
    "php": ["php"],
    "ruby": ["ruby"],
    "go": ["golang", "go programming"],
    "r": ["r programming", "r language"],
    "scala": ["scala"],
    "swift": ["swift programming"],

    # Web Development
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular", "angular.js"],
    "vue": ["vue", "vue.js"],
    "node.js": ["node.js", "nodejs"],
    "express.js": ["express.js", "expressjs"],
    "flask": ["flask"],
    "django": ["django"],
    "spring boot": ["spring boot"],
    "rest api": ["rest api", "restful api", "restful services"],

    # Databases
    "sql": ["sql", "structured query language"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo db"],
    "oracle database": ["oracle database", "oracle db"],
    "sqlite": ["sqlite"],
    "redis": ["redis"],
    "database management": ["database management", "dbms"],

    # Data Science and Machine Learning
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "artificial intelligence": ["artificial intelligence", "ai"],
    "natural language processing": ["natural language processing", "nlp"],
    "computer vision": ["computer vision"],
    "data science": ["data science"],
    "data analytics": ["data analytics", "data analysis"],
    "data visualization": ["data visualization"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "keras": ["keras"],
    "opencv": ["opencv"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "generative ai": ["generative ai", "gen ai"],
    "large language models": ["large language models", "llm", "llms"],

    # Business Intelligence
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "microsoft excel"],
    "data cleaning": ["data cleaning", "data preprocessing"],
    "data mining": ["data mining"],

    # Cloud and DevOps
    "aws": ["aws", "amazon web services"],
    "microsoft azure": ["microsoft azure", "azure"],
    "google cloud": ["google cloud", "gcp"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git"],
    "github": ["github"],
    "jenkins": ["jenkins"],
    "linux": ["linux"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],

    # Core Computer Science
    "data structures": ["data structures", "dsa"],
    "algorithms": ["algorithms"],
    "operating systems": ["operating systems", "os"],
    "computer networks": ["computer networks", "networking"],
    "object oriented programming": ["object oriented programming", "oop"],
    "software engineering": ["software engineering"],
    "compiler design": ["compiler design"],
    "cybersecurity": ["cybersecurity", "cyber security"],
    "network security": ["network security"],

    # Testing and Development Tools
    "software testing": ["software testing", "manual testing"],
    "automation testing": ["automation testing"],
    "selenium": ["selenium"],
    "postman": ["postman"],
    "jupyter notebook": ["jupyter notebook", "jupyter"],
    "vs code": ["vs code", "visual studio code"],
    "android development": ["android development"],
    "android studio": ["android studio"],

    # Other Professional Skills
    "problem solving": ["problem solving", "problem-solving"],
    "communication": ["communication skills", "communication"],
    "teamwork": ["teamwork", "team work"],
    "agile": ["agile methodology", "agile"],
    "scrum": ["scrum"],
    "project management": ["project management"],
    "technical documentation": ["technical documentation"]
}


# ==========================================
# CERTIFICATION EXTRACTION FUNCTION
# ==========================================

def extract_certifications(text):

    text = text.lower()

    found_certifications = set()

    for standard_name, aliases in CERTIFICATION_DICTIONARY.items():

        for alias in aliases:

            pattern = (
                r"(?<!\w)"
                + re.escape(alias.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, text):

                found_certifications.add(standard_name)
                break

    return sorted(found_certifications)
# ==========================================
# SKILL EXTRACTION FUNCTION
# ==========================================

def extract_skills(text):

    text = text.lower()

    found_skills = set()

    for standard_name, aliases in SKILL_DICTIONARY.items():

        for alias in aliases:

            pattern = (
                r"(?<!\w)"
                + re.escape(alias.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, text):

                found_skills.add(standard_name)
                break

    return sorted(found_skills)