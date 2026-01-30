import streamlit as st
from groq import Groq
import PyPDF2
from PIL import Image
import easyocr
import numpy as np

# --- 1. PREMIUM UI & VISIBILITY ENGINE ---
st.set_page_config(page_title="NutriCare AI Premium", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important; }
    
    /* Input Container Styling */
    [data-testid="stVerticalBlock"] > div:has(div.stNumberInput) {
        background-color: #0e1117 !important;
        border-radius: 20px;
        padding: 30px !important;
    }

    /* Results Visibility Fix */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border-radius: 15px;
        padding: 25px !important;
    }
    .stTabs [data-baseweb="tab-panel"] * { color: #1a1a1a !important; }
    
    label, p, [data-testid="stMetricLabel"] { color: #ffffff !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-FILE EXTRACTION (No Tesseract Required) ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def extract_data(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([p.extract_text() for p in reader.pages])
    else:
        # OCR for Screenshots
        reader = load_ocr()
        image = Image.open(uploaded_file)
        results = reader.readtext(np.array(image))
        return " ".join([res[1] for res in results])

# --- 3. DASHBOARD ---
st.title("🏥 NutriCare AI: Clinical Audit")

with st.sidebar:
    uploaded_file = st.file_uploader("Upload Report/Screenshot", type=["pdf", "png", "jpg"])
    # Using Llama 3.3 to avoid decommission error
    model_choice = "llama-3.3-70b-versatile" 

with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1: weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    with c2: height = st.number_input("Height (cm)", 100.0, 250.0, 175.0)
    with c3: age = st.number_input("Age", 1, 100, 25)
    with c4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "At Risk" if bmi > 25 else "Healthy")

    if st.button("🚀 GENERATE CLINICAL AUDIT", use_container_width=True):
        with st.status("🧬 Analyzing file data...") as status:
            report_text = extract_data(uploaded_file) if uploaded_file else "None"
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # Prioritize Report Data
            prompt = f"""
            You are a Senior Dietitian. 
            EXTRACTED REPORT: {report_text}
            DASHBOARD DATA: {age}y, {weight}kg, {height}cm.
            
            TASK: Search the EXTRACTED REPORT first for weight/height/vitals. If found, use those instead of Dashboard data. 
            Create a clinical nutrition plan.
            """
            
            chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
            st.session_state.res_text = chat.choices[0].message.content
            status.update(label="✅ Analysis Complete!", state="complete")

# --- 4. OUTPUT ---
if 'res_text' in st.session_state:
    st.divider()
    t1, t2 = st.tabs(["🍏 Meal Plan", "📈 Report Insights"])
    with t1: st.markdown(st.session_state.res_text)
