import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. PREMIUM UI & STATE ENGINE ---
st.set_page_config(page_title="NutriCare AI Pro", layout="wide")

# Initialize Session State values
# These keys ('w', 'h', 'a') allow the AI to update the dashboard automatically
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': ""}.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.markdown("""
    <style>
    /* Force Results Area to be High Contrast */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 0 0 20px 20px !important;
        padding: 25px !important;
        border: 1px solid #e0e0e0 !important;
    }
    /* Ensure Markdown text inside tabs is pure black */
    .stTabs [data-baseweb="tab-panel"] div, 
    .stTabs [data-baseweb="tab-panel"] p, 
    .stTabs [data-baseweb="tab-panel"] li {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    /* Tab Headers visibility */
    button[data-baseweb="tab"] {
        background-color: #f8fafc !important;
        border-radius: 15px 15px 0 0 !important;
        margin-right: 5px !important;
    }
    button[data-baseweb="tab"] p {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
# --- 2. EXTRACTION ENGINE (Replacing Tesseract) ---
@st.cache_resource
def load_ocr():
    # EasyOCR is used to avoid TesseractNotFoundError on Streamlit Cloud
    return easyocr.Reader(['en'])

def sync_dashboard_from_file(file):
    """Extracts text and uses AI to update session state numbers"""
    # 1. Extract raw text from PDF or Image
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = " ".join([p.extract_text() for p in reader.pages])
    else:
        reader = load_ocr()
        text = " ".join([res[1] for res in reader.readtext(np.array(Image.open(file)))])
    
    st.session_state.raw_text = text
    
    # 2. Use a fast AI model to find the specific numbers for the dashboard
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # We ask for JSON to ensure we get clean numbers
        sync_prompt = f"Extract weight(kg), height(cm), age from text: '{text}'. Return ONLY JSON: {{\"w\":num, \"h\":num, \"a\":num}}"
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": sync_prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        vitals = json.loads(resp.choices[0].message.content)
        
        # This is where the magic happens: the dashboard updates
        st.session_state.w = float(vitals.get('w', st.session_state.w))
        st.session_state.h = float(vitals.get('h', st.session_state.h))
        st.session_state.a = int(vitals.get('a', st.session_state.a))
    except:
        st.warning("Could not find all vitals in the report. Please check the boxes manually.")

# --- 3. SIDEBAR ---
from fpdf import FPDF

def create_sample_report():
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="METRO CARE DIAGNOSTICS", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Official Clinical Laboratory Report", ln=True, align='C')
    pdf.ln(10)
    
    # Vitals Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="PATIENT VITALS:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="- Weight: 92.5 kg", ln=True)
    pdf.cell(200, 10, txt="- Height: 180 cm", ln=True)
    pdf.cell(200, 10, txt="- Age: 45 years", ln=True)
    pdf.ln(5)
    
    # Lab Results
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="LABORATORY RESULTS:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="Blood Glucose: 115 mg/dL (Elevated)\nLDL Cholesterol: 155 mg/dL (High)\nTriglycerides: 170 mg/dL")
    
    # Save the file
    pdf.output("sample_clinical_report.pdf")
    print("Success: sample_clinical_report.pdf has been created!")

create_sample_report()

with st.sidebar:
    st.markdown("### 📂 1. Clinical Input")
    uploaded_file = st.file_uploader("Upload Lab Report/Screenshot", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file and st.button("🔍 Sync Dashboard from File"):
        with st.status("🧬 Reading Report...") as s:
            sync_dashboard_from_file(uploaded_file)
            s.update(label="✅ Dashboard Updated!", state="complete")
    
    st.divider()
    model_choice = st.selectbox("LLM Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

# --- 4. DASHBOARD ---
st.title("🥗 AI Based Diet Plan Generator")

with st.container():
    st.markdown("### 🩺 2. Verify Patient Vitals")
    v1, v2, v3, v4 = st.columns(4)
    
    # We link these inputs to session_state using the 'key' parameter
    weight = v1.number_input("Weight (kg)", 30.0, 200.0, key="w")
    height = v2.number_input("Height (cm)", 100.0, 250.0, key="h")
    age = v3.number_input("Age", 1, 120, key="a")
    
    with v4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "Healthy" if 18.5 <= bmi <= 25 else "Attention Required")

    # Dietary Context
    p1, p2 = st.columns([2, 1])
    with p1: culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto", "Mediterranean"], default=["South Indian"])
    with p2: goal = st.select_slider("Clinical Goal", options=["Loss", "Maintain", "Muscle"])

    if st.button("🚀 GENERATE CLINICAL AUDIT", use_container_width=True):
        with st.status("🔍 Generating Plan...") as status:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Dietitian: Analyze this lab data: {st.session_state.raw_text}. Create {goal} plan for {age}y, {weight}kg ({culture})."
            chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
            st.session_state.res_text = chat.choices[0].message.content
            status.update(label="✅ Analysis Complete!", state="complete")

# --- 5. OUTPUT ---
if st.session_state.res_text:
    st.divider()
    t1, t2 = st.tabs(["🍏 Meal Plan", "📈 Extracted Lab Data"])
    with t1: st.markdown(st.session_state.res_text)
    with t2: st.code(st.session_state.raw_text)
