import re
from pypdf import PdfReader



def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text
SKILLS = [
    "python",
    "sql",
    "mysql",
    "django",
    "html",
    "css",
    "git",
    "machine learning",
    "data science",
    "java",
    "c",
    "c++",
    "javascript",
    "springboot",
    "numpy",
    "pandas",
    "oracle sql",
    "bootstrap",
    "jquery",
    "php",
    "react",
    "nodejs",
    "excel"
]

def extract_skills(text):

    text = text.lower()

    found_skills = set()

    for skill in SKILLS:

        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        if re.search(pattern, text):
            found_skills.add(skill)

    return list(found_skills)

def calculate_match_score(resume_skills, jd_skills):
    matched = []

    for skill in jd_skills:
        if skill in resume_skills:
            matched.append(skill)

    if len(jd_skills) == 0:
        return 0

    return int((len(matched) / len(jd_skills)) * 100)