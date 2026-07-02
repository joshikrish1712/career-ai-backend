import pdfplumber
import re
import io

SKILL_KEYWORDS = [
    "python","java","javascript","typescript","react","angular","vue","node","django",
    "fastapi","flask","spring","sql","postgresql","mysql","mongodb","redis","docker",
    "kubernetes","aws","azure","gcp","git","ci/cd","linux","machine learning",
    "deep learning","tensorflow","pytorch","nlp","data analysis","pandas","numpy",
    "scikit-learn","html","css","tailwind","graphql","rest","microservices","agile","scrum","figma",
]

CAREER_MAP = {
    ("python","machine learning","tensorflow"): "AI/ML Engineer",
    ("react","javascript","typescript","css"): "Frontend Developer",
    ("python","fastapi","postgresql","docker"): "Backend Engineer",
    ("react","node","postgresql","docker"): "Full Stack Developer",
    ("aws","kubernetes","docker","linux"): "DevOps / Cloud Engineer",
    ("pandas","numpy","sql","data analysis"): "Data Analyst / Scientist",
    ("figma","css","html"): "UI/UX Designer",
}

def extract_text(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text

def detect_skills(text: str):
    lower = text.lower()
    return [s for s in SKILL_KEYWORDS if re.search(r'\b' + re.escape(s) + r'\b', lower)]

def suggest_career(skills: list) -> str:
    skill_set = set(skills)
    best, best_score = "Software Developer", 0
    for keywords, career in CAREER_MAP.items():
        score = len(skill_set.intersection(keywords))
        if score > best_score:
            best, best_score = career, score
    return best

def compute_ats_score(text: str, skills: list) -> dict:
    lower = text.lower()
    has_contact  = bool(re.search(r'[\w.+-]+@[\w-]+\.\w+', text))
    has_linkedin = "linkedin" in lower
    has_phone    = bool(re.search(r'\+?\d[\d\s\-]{8,}', text))
    contact_pct  = int((has_contact + has_linkedin + has_phone) / 3 * 100)
    has_exp      = any(w in lower for w in ["experience","work history","employment"])
    has_edu      = any(w in lower for w in ["education","degree","university","college","b.tech","mba"])
    has_summary  = any(w in lower for w in ["summary","objective","profile","about"])
    structure_pct = int((has_exp + has_edu + has_summary) / 3 * 100)
    skill_pct      = min(100, len(skills) * 9)
    keyword_pct    = min(100, len(skills) * 7 + 20)
    formatting_pct = 65 if len(text) > 300 else 35
    overall = int(keyword_pct*0.30 + skill_pct*0.20 + structure_pct*0.20 + contact_pct*0.15 + formatting_pct*0.15)
    def status(p): return "good" if p >= 75 else "warn" if p >= 50 else "bad"
    tips = []
    if keyword_pct < 70:  tips.append("Add more industry-relevant keywords from the job description.")
    if skill_pct < 60:    tips.append("Expand your Skills section with specific tools and technologies.")
    if not has_contact:   tips.append("Ensure your email address is clearly visible at the top.")
    if not has_linkedin:  tips.append("Add your LinkedIn profile URL.")
    if not has_summary:   tips.append("Add a professional Summary or Objective section.")
    if len(text) < 400:   tips.append("Your resume may be too short. Add more detail to each role.")
    return {
        "score": overall,
        "sections": [
            {"label": "Keyword match",   "pct": keyword_pct,    "status": status(keyword_pct)},
            {"label": "Work experience", "pct": structure_pct,  "status": status(structure_pct)},
            {"label": "Skills section",  "pct": skill_pct,      "status": status(skill_pct)},
            {"label": "Formatting",      "pct": formatting_pct, "status": status(formatting_pct)},
            {"label": "Contact info",    "pct": contact_pct,    "status": status(contact_pct)},
        ],
        "tips": tips,
    }
