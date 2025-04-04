import re, fitz
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def extract_skills(text):
    keywords = ['python', 'ml', 'flask', 'django', 'sql', 'aws', 'excel', 'react', 'css']
    return [skill for skill in keywords if skill in text.lower()]

def extract_name(text):
    match = re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+', text)
    return match.group(0) if match else "Name not found"

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r"\+?\d[\d\s\-]{8,}\d", text)
    return match.group(0) if match else ""

def extract_experience(text):
    exp_match = re.search(r"(\d+)\+?\s+years", text.lower())
    return exp_match.group(0) if exp_match else "0 years"

def extract_education(text):
    education_keywords = ['Bachelor', 'B.Tech', 'B.E', 'Master', 'M.Tech', 'MBA', 'PhD', 'B.Sc', 'M.Sc', 'Diploma']
    lines = text.split('\n')
    education = []

    for line in lines:
        if any(keyword in line for keyword in education_keywords):
            education.append(line.strip())

    return education if education else ["Not Found"]


def parse_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def parse_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def parse_resume(file):
    content = parse_pdf(file) if file.filename.endswith(".pdf") else parse_docx(file)
    return {
        "name": extract_name(content),
        "email": extract_email(content),
        "phone": extract_phone(content),
        "skills": extract_skills(content),
        "experience": extract_experience(content),
        "education": extract_education(content),
        "raw": content[:2000]
    }

def match_resume_with_jd(parsed, jd_text):
    tfidf = TfidfVectorizer().fit_transform([parsed['raw'], jd_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return {"match_percent": round(score * 100, 2)}

def predict_salary(parsed):
    try:
        years = int(re.findall(r"\d+", parsed['experience'])[0])
    except:
        years = 0
    base = 3 + years * 1.5 + len(parsed["skills"]) * 0.5
    return {"estimated_salary": round(base, 2)}

def analyze_linkedin_profile(url):
    return {"url": url, "valid": url.startswith("https://www.linkedin.com/")}

def generate_dashboard(parsed, jd_text):
    jd_keywords = set(jd_text.lower().split())
    skills = set(parsed["skills"])
    matched = list(skills & jd_keywords)
    missing = list(jd_keywords - skills)
    return {
        "skills_matched": matched,
        "skills_missing": missing,
        "match_percent": round((len(matched)/(len(jd_keywords)+1e-5))*100, 2)
    }

def generate_pdf_report(parsed, match, salary, dashboard, filepath):
    c = canvas.Canvas(filepath, pagesize=A4)
    text = c.beginText(40, 800)
    text.setFont("Helvetica", 12)
    text.textLine("Resume Scanner AI Report")
    text.textLine("-------------------------")
    text.textLine(f"Name: {parsed['name']}")
    text.textLine(f"Email: {parsed['email']}")
    text.textLine(f"Phone: {parsed['phone']}")
    text.textLine(f"Experience: {parsed['experience']}")
    text.textLine(f"Skills: {', '.join(parsed['skills'])}")
    text.textLine(f"Matched Skills: {', '.join(dashboard['skills_matched'])}")
    text.textLine(f"Missing Skills: {', '.join(dashboard['skills_missing'])}")
    text.textLine(f"Job Match Score: {match['match_percent']}%")
    text.textLine(f"Estimated Salary (LPA): {salary['estimated_salary']}")
    c.drawText(text)
    c.showPage()
    c.save()
def generate_badge(match_percent):
    if match_percent >= 85:
        return "Gold"
    elif match_percent >= 70:
        return "Silver"
    else:
        return "Bronze"

def generate_ai_recommendations(missing_skills):
    if not missing_skills:
        return {
            "skills_to_learn": [],
            "certifications": [],
            "projects": [],
            "tips": ["Your skillset already matches well! Just refine your resume."]
        }

    return {
        "skills_to_learn": missing_skills[:3],
        "certifications": [f"Certification in {skill.title()}" for skill in missing_skills[:2]],
        "projects": [f"Build a project using {skill}" for skill in missing_skills[:2]],
        "tips": [f"Consider strengthening your knowledge in {missing_skills[0]}."]
    }
