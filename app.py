import streamlit as st
import json
import time
import PyPDF2  # Better for clinical text extraction
from fpdf import FPDF
from groq import Groq # Blazing fast Llama 3.1 provider

# --- 1. THEME & CONFIG ---
st.set_page_config(page_title="AI-NutriCare Hub v2", layout="wide")

# Persistent State Initialization (Fixes NameError)
if 'res_text' not in st.session_state: st.session_state.res_text = ""
if 'clinical_data' not in st.session_state: st.session_state.clinical_data = {}

# --- 2. SIDEBAR ---
with st.sidebar:
    st.markdown("## 👤 User Account")
    # Login logic remains as you had it
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        u_email = st.text_input("Email")
        u_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            st.session_state.logged_in = True
            st.rerun()
    else:
        st.success("Dharineesh Logged In")
        if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

    st.divider()
    st.markdown("### ⚙️ Model Settings")
    # Using Llama 3.1 - 2026's most stable clinical model
    model_choice = st.selectbox("LLM Model", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"])

    st.divider()
    st.markdown("### 📄 Clinical Upload")
    uploaded_file = st.file_uploader("Upload Lab Report", type=["pdf"])

# --- 3. HELPER FUNCTIONS ---
def extract_pdf_text(file):
    """Safely extracts text from clinical PDF"""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return ""

def create_pdf(text):
    """Generates sanitized PDF report"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

# --- 4. CORE ENGINE (GROQ) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")

# --- 5. BIOMETRICS UI ---
st.markdown('<h1 class="big-brand">🥗 AI-NutriCare Hub</h1>', unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        weight = st.number_input("Weight (kg)", 30, 150, 70)
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col2:
        height = st.number_input("Height (cm)", 100, 230, 175)
        goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
    with col3:
        age = st.number_input("Age", 10, 100, 25)
        food_culture = st.text_input("Local Cuisine", "South Indian")

# --- 6. EXECUTION LOGIC ---
if st.button("🚀 Generate AI Clinical Diet Plan", use_container_width=True):
    with st.spinner("Llama 3.1 is analyzing clinical markers..."):
        report_text = extract_pdf_text(uploaded_file) if uploaded_file else "No report uploaded."
        
        # Comprehensive prompt for clinical dietetics
        prompt = f"""
        ACT AS: Senior Clinical Dietitian.
        PATIENT: {age}yo {gender}, {weight}kg. Goal: {goal}. Cuisine: {food_culture}.
        REPORT DATA: {report_text}
        
        TASK:
        1. Identify high-risk clinical markers (Sugar, Cholesterol, etc.).
        2. Create a specific meal plan.
        3. List 'Strictly Avoid' foods based on the report.
        Format in clean Markdown.
        """
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_choice,
                temperature=0.5
            )
            st.session_state.res_text = chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Inference Error: {e}")

# --- 7. RESULTS DISPLAY ---
if st.session_state.res_text:
    with st.container(border=True):
        st.markdown("### 📋 AI Nutrition Analysis")
        st.markdown(st.session_state.res_text)
        
        st.divider()
        c1, c2, _ = st.columns([1,1,2])
        with c1:
            pdf_bytes = create_pdf(st.session_state.res_text)
            st.download_button("📥 Download PDF", data=pdf_bytes, file_name="Diet_Plan.pdf")
        with c2:
            st.download_button("📄 Download JSON", data=json.dumps({"report": st.session_state.res_text[:1000]}), file_name="Diet_Data.json")
