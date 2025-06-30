import streamlit as st
import os, io, re, requests, numpy as np, time
import spacy, fitz, easyocr
from pdfminer.high_level import extract_text
from PIL import Image
import pandas as pd
from agno.models.groq import Groq
from agno.agent import Agent
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now you can access your variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def getAgent():
    return Agent(model=Groq(id="gemma2-9b-it"), markdown=True)

agent = getAgent()

st.set_page_config(page_title="📄 Resume Matcher + LLM Judge", layout="wide")

@st.cache_resource
def load_models():
    return spacy.load("en_core_web_sm"), easyocr.Reader(['en'], gpu=False)

nlp, ocr = load_models()

TECH_SKILLS = {
    "python", "java", "c++", "c#", "javascript", "html", "css", "sql", "mongodb", "mysql",
    "postgresql", "tensorflow", "keras", "pytorch", "machine learning", "deep learning",
    "nlp", "flask", "django", "fastapi", "react", "angular", "node.js", "git", "github",
    "linux", "aws", "azure", "gcp", "docker", "kubernetes", "pandas", "numpy", "matplotlib",
    "seaborn", "scikit-learn", "power bi", "tableau", "rest api", "graphql", "excel",
    "powerpoint", "snowflake", "airflow"
}

def call_ollama(prompt, model="llama3.2:1b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama error: {response.text}")

def safe_groq_score(jd, resume):
    prompt = (
        "Rate the resume's match to the job description from 0 to 100. "
        "Only return a number. No explanation.\n\n"
        f"Job Description:\n{jd}\n\nResume:\n{resume}"
    )
    reply = agent.run(prompt).content
    numbers = re.findall(r"\d{1,3}", reply)
    score = int(numbers[0]) if numbers else 0
    return min(score, 100)

def safe_groq_judge(jd, resume):
    prompt = (
        "You are a recruiter. Is this resume a good match for the job description?\n"
        "Reply YES - or NO - followed by a brief reason.\n\n"
        f"Job Description:\n{jd}\n\nResume:\n{resume}"
    )
    reply = agent.run(prompt).content
    match = reply.strip().upper().startswith("YES")
    reason = reply.partition("-")[2].strip() if "-" in reply else reply
    return match, reason[:250]

def extract_text_from_pdf(pdf_file):
    try:
        text = extract_text(pdf_file)
        if text.strip(): return text
    except: pass

    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    content = "".join(page.get_text("text") for page in doc).strip()
    if content: return content

    full_text = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        lines = ocr.readtext(np.array(img), detail=0)
        full_text.extend(lines)
    return "\n".join(full_text)

def extract_details(text):
    name = next((ln.strip() for ln in text.splitlines() if 2 < len(ln.strip()) < 50), "Unknown")
    email = (re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text) or ["None"])[0]
    doc = nlp(text.lower())
    found = {t.text for t in doc if t.text in TECH_SKILLS}
    found |= {ch.text.strip().lower() for ch in doc.noun_chunks if ch.text.strip().lower() in TECH_SKILLS}
    return name, email, sorted(found)

def categorize_score(score):
    if score <= 50: return "Low "
    elif 51 <= score <= 75: return "Medium "
    elif score > 75: return "High"
    return "Other"

def send_match_email(to_email, name, category):
    if category == "Top":
        subject = "You're shortlisted!"
        body = f"""Hi {name},

Congratulations! Your resume has been shortlisted for the next round of interviews.

If you're interested, please reply to this email and confirm your availability.

Best regards,
HR Team"""
    elif category == "Average":
        subject = "Resume Under Manual Review"
        body = f"""Hi {name},

Your profile is under manual screening by our recruitment team.

We will get back to you if there's a suitable fit.

Best regards,
HR Team"""
    else:
        subject = "Application Status"
        body = f"""Hi {name},

Thank you for your application.

At this time, your profile has not been shortlisted.

Best wishes for your future opportunities,
HR Team"""

    msg = MIMEText(body)
    msg['Subject'], msg['From'], msg['To'] = subject, EMAIL_ADDRESS, to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email to {name}: {e}")
        return False

# UI
st.title("📄 Resume Matcher + LLM Judge + ✉️ Email Notifier")

jd_file = st.file_uploader("📌 Upload Job Description (.txt)", type="txt")
resumes = st.file_uploader("📎 Upload Resumes (.pdf)", type="pdf", accept_multiple_files=True)

if st.button("🚀 Match & Analyze") and jd_file and resumes:
    jd = jd_file.read().decode()
    results = []

    with st.spinner("🔍 Analyzing resumes..."):
        for pdf in resumes:
            text = extract_text_from_pdf(pdf)
            if not text.strip():
                continue
            name, email, skills = extract_details(text)

            # ✅ Groq scoring with delay
            try:
                score = safe_groq_score(jd, text)
                time.sleep(6.5)
            except Exception as e:
                st.warning(f"⚠️ Groq rate limit on scoring. Retrying...")
                time.sleep(10)
                score = safe_groq_score(jd, text)

            try:
                judge_match, judge_reason = safe_groq_judge(jd, text)
                time.sleep(6.5)
            except Exception as e:
                st.warning(f"⚠️ Groq rate limit on judging. Retrying...")
                time.sleep(10)
                judge_match, judge_reason = safe_groq_judge(jd, text)

            category = categorize_score(score)
            results.append({
                "Name": name,
                "Email": email,
                "Skills": ", ".join(skills[:5]),
                "Score": score,
                "Category": category,
                "Judge": "YES" if judge_match else "NO",
                "Reason": judge_reason
            })

            if email and email != "None":
                send_match_email(email, name, category)

    df = pd.DataFrame(results).sort_values("Score", ascending=False)

    st.subheader("📊 All Candidates")
    st.dataframe(df[["Name", "Email", "Skills", "Score", "Category", "Judge"]])

    for category in ["Top", "Average", "Regret"]:
        sub_df = df[df["Category"] == category]
        if not sub_df.empty:
            st.subheader(f"🔸 {category} Matches")
            st.dataframe(sub_df[["Name", "Email", "Skills", "Score"]])

    acc = (df["Judge"] == df["Category"].apply(lambda c: "YES" if c in ["Top", "Average"] else "NO")).mean()
    st.metric("✅ Match Accuracy vs Judge", f"{acc:.0%}")

    if not df[df["Category"] == "Top"].empty:
        st.subheader("🧠 Judge Justification for Top Matches")
        for _, row in df[df["Category"] == "Top"].iterrows():
            st.markdown(f"**{row['Name']}** — {row['Reason']}")