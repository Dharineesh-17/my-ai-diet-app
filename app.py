import streamlit as st
import json
from groq import Groq
import PyPDF2
from PIL import Image
import easyocr 
import numpy as np

# --- 1. CLINICAL THEME ENGINE ---
st.set_page_config(page_title="AI Clinical Dietitian", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important; }
    
    /* Input Container Styling */
    [data-testid="stVerticalBlock"] > div:has(div.stNumberInput) {
        background-color: #0e1117 !important;
        border-radius: 20px;
        padding: 30px !important;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Force Label Visibility */
    label, p, [data-testid="stMetricLabel"] { color: #ffffff !important; font-weight: 700 !important; }

    /* Results Visibility Fix */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border-radius: 15px;
        padding: 25px !important;
    }
    .stTabs [data-baseweb="tab-panel"] * { color: #1a1a1a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-FILE EXTRACTION ENGINE ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def extract_data(uploaded_file):
    """Parses PDFs and Screenshots for clinical data"""
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([p.extract_text() for p in reader.pages])
    else:
        # OCR for Screenshots/Images
        reader = load_ocr()
        image = Image.open(uploaded_file)
        results = reader.readtext(np.array(image))
        return " ".join([res[1] for res in results])

if 'res_text' not in st.session_state: st.session_state.res_text = ""

# --- 3. DASHBOARD ---
st.title("🏥 NutriCare AI: Clinical Audit")

with st.sidebar:
    st.markdown("### 📂 Data Ingestion")
    # Supports PDF, PNG, JPG
    uploaded_file = st.file_uploader("Upload Lab Report / Screenshot", type=["pdf", "png", "jpg", "jpeg"])
    st.divider()
    model_choice = st.selectbox("LLM Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1: weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    with c2: height = st.number_input("Height (cm)", 100.0, 250.0, 175.0)
    with c3: age = st.number_input("Age", 1, 100, 25)
    with c4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "Healthy" if 18.5 <= bmi <= 25 else "At Risk")

    p1, p2 = st.columns([2, 1])
    with p1: culture = st.multiselect("Dietary Preference", ["South Indian", "North Indian", "Keto"], default=["South Indian"])
    with p2: goal = st.select_slider("Goal", options=["Loss", "Maintain", "Muscle"])

    if st.button("🚀 GENERATE REPORT-BASED AUDIT", use_container_width=True):
        with st.status("🧬 Analyzing file data...") as status:
            report_text = extract_data(uploaded_file) if uploaded_file else "No report provided."
            
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                # THE PROMPT: Commands AI to prioritize report data over manual inputs
                prompt = f"""
                You are a Senior Dietitian. 
                PRIMARY DATA SOURCE: {report_text}
                MANUAL FALLBACKS: {age}y, {weight}kg, {height}cm.
                CULTURE: {culture} | GOAL: {goal}

                TASK:
                1. First, search the PRIMARY DATA SOURCE for Weight, Height, and clinical markers (Sugar, BMI, etc.).
                2. If the report has data, IGNORE the Manual Fallbacks for those values.
                3. Create a nutrition plan based on these clinical findings.
                """
                chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
                st.session_state.res_text = chat.choices[0].message.content
                status.update(label="✅ Analysis Complete!", state="complete")
            except Exception as e:
                st.error(f"Error: {e}")

# --- 4. OUTPUT ---
if st.session_state.res_text:
    st.markdown("### 📋 AI Nutrition Prescription")
    t1, t2 = st.tabs(["🍏 Meal Plan", "📈 Report Insights"])
    with t1: st.markdown(st.session_state.res_text)
    with t2: st.info("💡 Tip: AI prioritized clinical markers found in your upload.")
