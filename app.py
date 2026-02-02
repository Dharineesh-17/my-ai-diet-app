import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. PREMIUM UI & STATE ENGINE ---
st.set_page_config(page_title="AI Based Diet Plan Genertor", layout="wide")

# Initialize Session State values
for key, val in {'w': 0.0, 'h': 0.0, 'a': 0, 'res_text': "", 'raw_text': ""}.items():
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
        border-radius: 10px 10px 0 0 !important;
        margin-right: 5px !important;
    }
    button[data-baseweb="tab"] p {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. EXTRACTION ENGINE ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def sync_dashboard_from_file(file):
    """Extracts text and applies safety bounds to prevent crashes"""
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = " ".join([p.extract_text() for p in reader.pages])
    else:
        reader = load_ocr()
        text = " ".join([res[1] for res in reader.readtext(np.array(Image.open(file)))])
    
    st.session_state.raw_text = text
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sync_prompt = f"Extract weight(kg), height(cm), age from text: '{text}'. Return ONLY JSON: {{\"w\":num, \"h\":num, \"a\":num}}"
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": sync_prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        vitals = json.loads(resp.choices[0].message.content) #
        
        # --- SAFETY CLAMPING: Prevents StreamlitValueBelowMinError ---
        # We ensure the extracted value is never below the 'min_value' of your number_input
        st.session_state.w = max(30.0, min(200.0, float(vitals.get('w', st.session_state.w))))
        st.session_state.h = max(100.0, min(250.0, float(vitals.get('h', st.session_state.h))))
        st.session_state.a = max(1, min(120, int(vitals.get('a', st.session_state.a))))
        
    except Exception as e:
        st.warning(f"Note: Some vitals couldn't be auto-filled. ({e})")

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📂 1. Clinical Input")
    uploaded_file = st.file_uploader("Upload Lab Report/Screenshot", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file and st.button("🔍 Sync Dashboard from File"):
        with st.status("🧬 Analyzing Data...") as s:
            sync_dashboard_from_file(uploaded_file)
            s.update(label="✅ Dashboard Updated!", state="complete")
    
    st.divider()
    model_choice = st.selectbox("LLM Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

# --- 4. DASHBOARD ---
st.title("🥗 AI Based Diet Plan Generator")

with st.container():
    st.markdown("### 🩺 2. Verify Patient Vitals")
    v1, v2, v3, v4 = st.columns(4)
    
    # These use the session_state keys to reflect the AI extraction
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
        if not st.session_state.raw_text and not uploaded_file:
            st.error("Please upload a report or sync data first.")
        else:
            with st.status("🔍 Generating Plan...") as status:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Dietitian: Analyze this lab data: {st.session_state.raw_text}. Create {goal} plan for {age}y, {weight}kg ({culture})."
                chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
                st.session_state.res_text = chat.choices[0].message.content
                status.update(label="✅ Analysis Complete!", state="complete")

# --- 5. OUTPUT EXPERIENCE ---
if st.session_state.res_text:
    st.divider()
    st.markdown("### 📋 AI Nutrition Prescription")
    t1, t2 = st.tabs(["🍏 Meal Plan", "📈 Health Insights"])
    with t1: st.markdown(st.session_state.res_text)
    with t2: st.info("💡 Clinical Tip: Ensure 3.5L water intake to support metabolism.")
    st.download_button("📥 Download Plan", st.session_state.res_text, file_name="Diet_Plan.txt")
