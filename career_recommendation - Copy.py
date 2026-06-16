import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import pdfplumber
import os
from openai import OpenAI  # pip install openai

# ---------------- CONFIG & API SETUP ----------------
# Groq API Key-ai inge enter pannunga (Get it from console.groq.com)
GROQ_API_KEY = ""

TESSERACT_PATH = r"C:\Users\bowsi\OneDrive\Desktop\new code\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ---------------- AI COACH LOGIC ----------------
def get_ai_career_advice(extracted_text):
    """
    LLM use panni resume text-ai analyze panni advice tharum.
    """
    try:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY
        )

        prompt = f"""
        You are a Professional Career Coach. Analyze the following resume text:
        ---
        {extracted_text[:3000]}
        ---
        Please provide:
        1. Top 3 Career Path Recommendations.
        2. Skill Gap Analysis (What skills are missing?).
        3. A 'Golden Tip' to improve their profile.
        
        Keep the response professional and encouraging.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Coach error: {str(e)}"

# ---------------- MAIN FUNCTION ----------------
def show_recommendation():
    st.title("🤖 AI Career Recommendation & Coach")
    st.caption("Advanced Career Analysis using Data & LLM")

    @st.cache_data
    def load_data():
        df = pd.read_csv("Job_Market_India_with_Skills.csv")
        df.columns = df.columns.str.lower().str.strip()
        return df

    df = load_data()

    st.subheader("📤 Step 1: Upload Profile")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["png", "jpg", "jpeg", "pdf"])

    if not uploaded_file:
        st.info("Awaiting file upload...")
        st.stop()
        

    extracted_text = ""

    # ---------- EXTRACTION ----------
    with st.status("Extracting text from file...") as status:
        if uploaded_file.type != "application/pdf":
            img = Image.open(uploaded_file)
            st.image(img, caption="Detected Profile", width=300)
            extracted_text = pytesseract.image_to_string(img)
        else:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extracted_text += page.extract_text() + "\n"
        status.update(label="Extraction Complete!", state="complete")

    if not extracted_text.strip():
        st.error("Could not extract text. Please try a clearer file.")
        st.stop()

    # ---------- SIMPLE SKILL DETECTION ----------
    all_skills = ["python", "java", "sql", "machine learning", "javascript", "react", "html", "css", "communication"]
    detected_skills = [s for s in all_skills if s in extracted_text.lower()]
    
    # Simple Role Detection
    possible_roles = ["software engineer", "data analyst", "frontend developer", "product manager", "data scientist"]
    detected_role = ""
    for role in possible_roles:
        if role in extracted_text.lower():
            detected_role = role
            break

    # ---------- STEP 2: DATA-BASED JOBS ----------
    st.divider()
    st.subheader("💼 Top Matches from Job Market Data")
    
    recommendations = recommend_logic(detected_skills, detected_role, df)
    
    if recommendations:
        for rec in recommendations[:3]:
            with st.expander(f"📌 {rec['job_role']} - Match: {rec['match_percent']}%"):
                col1, col2 = st.columns(2)
                col1.metric("Est. Salary", f"₹{rec['salary']:,}")
                col2.write(f"📍 Location: {rec['city']}")
    else:
        st.warning("No direct matches found in our local database.")

    # ---------- STEP 3: AI CAREER COACH ----------
    st.divider()
    st.subheader("🤖 AI Career Coach Advice")
    st.info("Analyzing your profile beyond keywords...")

    if st.button("Get AI Personal Advice"):
        with st.spinner("AI is thinking..."):
            advice = get_ai_career_advice(extracted_text)
            st.markdown("### 💡 AI Recommendations")
            st.write(advice)

# ---------------- SMART LOGIC ----------------
def recommend_logic(user_skills, detected_role, df):
    results = []
    user_skills_set = set(user_skills)

    for _, row in df.iterrows():
        job_role = str(row['job_role']).lower()
        job_skills = set(s.strip().lower() for s in str(row['skills_required']).split(","))

        # Skill Score
        skill_match = len(user_skills_set.intersection(job_skills))
        skill_score = (skill_match / len(job_skills)) * 60 if job_skills else 0

        # Role Score
        role_score = 40 if detected_role and (detected_role in job_role or job_role in detected_role) else 0

        final_score = skill_score + role_score

        if final_score >= 20:
            results.append({
                "job_role": row['job_role'],
                "match_percent": round(final_score, 2),
                "salary": row['salary_inr'],
                "city": row['city']
            })
    
    return sorted(results, key=lambda x: x['match_percent'], reverse=True)