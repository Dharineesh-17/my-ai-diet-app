import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. PREMIUM UI CONFIGURATION ---
st.set_page_config(page_title="NutriCare AI Pro", layout="wide")

# Persistent State Management
# This allows the AI to "fill in" the numbers for you
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res': "", 'raw': ""}.items():
    if key not in st.session_state: st.session_state[key] = val

st.markdown("""
    <style>
    /* Background Gradient */
    .stApp { 
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important; 
    }
    
    /* Input Dashboard Card */
    [data-testid="stVerticalBlock"] > div:has(div.stNumberInput) {
        background: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(10px);
        border-radius: 24px !important;
        padding: 40px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4) !important;
    }

    /* Input Label Contrast */
    label, p, [data-testid="stMetricLabel"] { 
        color: #f8fafc !important; 
        font-weight: 600 !important;
    }

    /* Results Visibility (Medical Paper Style) */
    .stTabs [data-baseweb="tab-panel"] {
        background: #ffffff !important;
        color: #0f172a !important;
        border-radius: 0 0 20px 20px !important;
        padding: 35px !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stTabs [data-baseweb="tab-panel"] * { color: #0f172a !important; }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. EXTRACTION ENGINE ---
@st.cache_resource
def load_ocr(): 
    return easyocr.Reader(['en'])

def extract_and_sync(file):
    """Pulls text and auto-updates dashboard numbers"""
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = " ".join([p.extract_text() for p in reader.pages])
    else:
        # EasyOCR avoids the Tesseract error
        reader = load_ocr()
        text = " ".join([res[1] for res in reader.readtext(np.array(Image.open(file)))])
    
    # AI Pass 1: Extract ONLY the numbers to update the UI
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Extract weight(kg), height(cm), age from: {text}. Return ONLY JSON: {{\"w\":num, \"h\":num, \"a\":num}}"}],
            model="llama-3.1-8b-instant", response_format={"type": "json_object"}
        )
        vitals = json.loads(resp.choices[0].message.content)
        st.session_state.w = float(vitals.get('w', st.session_state.w))
        st.session_state.h = float(vitals.get('h', st.session_state.h))
        st.session_state.a = int(vitals.get('a', st.session_state.a))
    except:
        pass # Fallback to existing session values
    
    return text

# --- 3. MAIN DASHBOARD ---
st.title("🏥 NutriCare AI: Clinical Audit")

with st.sidebar:
    st.markdown("### 📂 Data Ingestion")
    up = st.file_uploader("Upload Report/Screenshot", type=["pdf", "png", "jpg", "jpeg"])
    if up and st.button("🔍 Sync Dashboard from File", use_container_width=True):
        with st.status("🧬 Analyzing file...") as s:
            st.session_state.raw = extract_and_sync(up)
            s.update(label="✅ Dashboard Updated!", state="complete")

# Workspace Container
with st.container():
    st.markdown("### 🩺 Confirmed Vitals")
    c1, c2, c3, c4 = st.columns(4)
    # Using 'key' connects these directly to our AI extraction
    w = c1.number_input("Weight (kg)", 30.0, 250.0, key="w")
    h = c2.number_input("Height (cm)", 100.0, 250.0, key="h")
    a = c3.number_input("Age", 1, 120, key="a")
    bmi = w / ((h/100)**2)
    # Visual health marker
    status = "Healthy" if 18.5 <= bmi <= 25 else "Attention Required"
    c4.metric("Live BMI", f"{bmi:.1f}", status)

    st.divider()
    if st.button("🚀 GENERATE FINAL CLINICAL AUDIT", use_container_width=True):
        with st.status("🧠 Consulting Llama 3.3...") as s:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Dietitian: Analyze this lab data: {st.session_state.raw}. Using Weight: {w}kg, Height: {h}cm, Age: {a}y. Create diet plan."
            chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
            st.session_state.res = chat.choices[0].message.content
            s.update(label="✅ Analysis Complete!", state="complete")

# Output Section
if st.session_state.res:
    t1, t2 = st.tabs(["📋 AI Prescription", "🔬 Raw Lab Data"])
    with t1: st.markdown(st.session_state.res)
    with t2: st.code(st.session_state.raw)
