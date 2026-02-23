import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. WORLD-CLASS UI ARCHITECTURE ---
st.set_page_config(page_title="NEURO-DIET | Clinical AI", layout="wide", page_icon="🧬")

# Extraordinary CSS Injection
st.markdown("""
    <style>
    /* Global Aesthetic */
    .stApp {
        background: radial-gradient(circle at 20% 10%, #050a18 0%, #000000 100%);
        color: #e0e6ed;
    }
    
    /* Neon Glassmorphism Containers */
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-family: 'Courier New', monospace; }
    
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(0, 242, 254, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Cyberpunk Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #000;
        font-weight: 800;
        letter-spacing: 1px;
        border: none;
        padding: 15px;
        transition: all 0.4s ease;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 242, 254, 0.4);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 10px 30px;
        color: #8892b0;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 242, 254, 0.1) !important;
        border: 1px solid #00f2fe !important;
        color: #00f2fe !important;
    }
    </style>
    """, unsafe_allow_html=True)

# State Engine
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': "", 'messages': []}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. HIGH-PRECISION LOGIC ---
@st.cache_resource
def load_ocr(): return easyocr.Reader(['en'])

def ingest_clinical_data(file):
    with st.spinner("🧬 High-Speed Neural Parsing..."):
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            text = " ".join([p.extract_text() for p in reader.pages])
        else:
            reader = load_ocr()
            text = " ".join([res[1] for res in reader.readtext(np.array(Image.open(file)))])
        st.session_state.raw_text = text
        
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Extract weight, height, age from: '{text}'. Return JSON: {{\"w\":num, \"h\":num, \"a\":num}}"}],
                model="llama-3.1-8b-instant", response_format={"type": "json_object"}
            )
            v = json.loads(resp.choices[0].message.content)
            st.session_state.update({'w': float(v.get('w', 70)), 'h': float(v.get('h', 175)), 'a': int(v.get('a', 25))})
            st.toast("Bio-data Synced Successfully!", icon="✅")
        except: st.toast("Manual calibration required.", icon="⚠️")

# --- 3. SIDEBAR (Clinical Input) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2fe;'>🔬 NEURO-DIET</h2>", unsafe_allow_html=True)
    st.caption("v2.5 Professional Edition")
    
    with st.container(border=True):
        upload = st.file_uploader("Upload Lab Diagnostics", type=["pdf", "png", "jpg"])
        if upload and st.button("EXECUTE DATA INGESTION"): ingest_clinical_data(upload)
    
    st.divider()
    m_choice = st.selectbox("Intelligence Core", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if st.button("RESET SESSION"):
        st.session_state.update({'messages': [], 'res_text': "", 'raw_text': ""})
        st.rerun()

# --- 4. MAIN DASHBOARD ---
st.markdown("<h1 style='text-align: center; color: #fff;'>Clinical Intelligence Center</h1>", unsafe_allow_html=True)

# Vitals Command Center
v_col1, v_col2, v_col3, v_col4 = st.columns(4)
with v_col1: w = st.number_input("Mass (kg)", 30.0, 200.0, key="w")
with v_col2: h = st.number_input("Height (cm)", 100.0, 250.0, key="h")
with v_col3: age = st.number_input("Age (Years)", 1, 120, key="a")
with v_col4:
    bmi = w / ((h/100)**2)
    st.metric("PULSE BMI", f"{bmi:.1f}", "OPTIMAL" if 18.5 <= bmi <= 25 else "VARIANCED")

# Tabs for Separation of Concerns
tab_rep, tab_chat = st.tabs(["📑 DIAGNOSTIC REPORT", "🧠 NEURAL CONSULTATION"])

with tab_rep:
    col_x, col_y = st.columns([3, 2])
    with col_x: culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto", "Mediterranean"], default=["South Indian"])
    with col_y: goal = st.select_slider("Clinical Goal", options=["Loss", "Maintain", "Muscle"])
    
    if st.button("SYNTHESIZE CLINICAL DIET PLAN"):
        with st.status("Aligning Bio-Markers with Nutritional Science..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            p = f"Analyze: {st.session_state.raw_text}. Create {goal} plan for {age}y, {w}kg ({culture}). Format: Professional Medical Document."
            resp = client.chat.completions.create(messages=[{"role": "user", "content": p}], model=m_choice)
            st.session_state.res_text = resp.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": "Report ready. Diagnostics complete."})

    if st.session_state.res_text:
        st.markdown("### 📋 AI Generated Prescription")
        st.markdown(f"<div style='background:rgba(0,242,254,0.05); padding:20px; border-radius:15px; border-left: 5px solid #00f2fe;'>{st.session_state.res_text}</div>", unsafe_allow_html=True)
        st.download_button("📥 DOWNLOAD ENCRYPTED REPORT", st.session_state.res_text, f"Clinical_Report_{age}.txt")

with tab_chat:
    if not st.session_state.res_text:
        st.info("System Standby: Awaiting Diagnostic Data.")
    else:
        # Chat History with Premium Styling
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Query the clinical engine..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                ctx = f"System: Clinical Nutritionist. Basis: {st.session_state.res_text}. Patient: {age}y, {w}kg. Context-aware strictly."
                resp = client.chat.completions.create(
                    messages=[{"role": "system", "content": ctx}, *st.session_state.messages],
                    model=m_choice
                )
                st.markdown(resp.choices[0].message.content)
                st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})
