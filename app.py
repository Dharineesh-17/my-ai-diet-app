import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. THE ULTIMATE VISUAL ENGINE ---
st.set_page_config(page_title="NEURO-DIET | Live Engine", layout="wide", page_icon="🧬")

# "Movable" & Holographic Effect CSS
st.markdown("""
    <style>
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #050a18, #000000, #0a192f, #000000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }

    /* Floating Metric Panels */
    [data-testid="stMetricValue"] { color: #00f2fe !important; text-shadow: 0 0 10px #00f2fe; }
    
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(0, 242, 254, 0.3);
        transition: all 0.3s ease;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric):hover {
        transform: translateY(-5px);
        border: 1px solid #00f2fe;
        box-shadow: 0 10px 30px rgba(0, 242, 254, 0.2);
    }

    /* Live Editor Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 10, 24, 0.95) !important;
        border-right: 1px solid #00f2fe;
    }

    /* Tab Customization */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: rgba(255,255,255,0.02);
        border-radius: 10px 10px 0 0;
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)

# State Engine
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': "", 'messages': []}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. ENGINE LOGIC ---
@st.cache_resource
def load_ocr(): return easyocr.Reader(['en'])

def ingest_data(file):
    with st.spinner("🧬 Neural Extraction in Progress..."):
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
                messages=[{"role": "user", "content": f"Extract weight, height, age from: '{text}'. JSON: {{\"w\":num, \"h\":num, \"a\":num}}"}],
                model="llama-3.1-8b-instant", response_format={"type": "json_object"}
            )
            v = json.loads(resp.choices[0].message.content)
            st.session_state.update({'w': float(v.get('w', 70)), 'h': float(v.get('h', 175)), 'a': int(v.get('a', 25))})
        except: st.error("Neural Sync Failed. Please calibrate manually.")

# --- 3. LIVE UI EDITOR (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h1 style='color:#00f2fe; font-size: 25px;'>LIVE EDITOR</h1>", unsafe_allow_html=True)
    st.caption("Adjust parameters to update clinical logic.")
    
    with st.expander("📂 SOURCE DATA", expanded=True):
        upload = st.file_uploader("Drop Report Here", type=["pdf", "png", "jpg"])
        if upload and st.button("SYNCHRONIZE"): ingest_data(upload)
    
    st.divider()
    
    st.markdown("### 🎚️ BIO-TUNING")
    w = st.slider("Target Weight (kg)", 30.0, 200.0, key="w")
    h = st.slider("Height (cm)", 100.0, 250.0, key="h")
    age = st.number_input("Biological Age", 1, 120, key="a")
    
    st.divider()
    if st.button("🗑️ PURGE ALL DATA"):
        st.session_state.update({'messages': [], 'res_text': ""})
        st.rerun()

# --- 4. THE COMMAND CENTER (MAIN VIEW) ---
col_main, col_chat = st.columns([1.5, 1])

with col_main:
    st.markdown("<h2 style='color:#fff;'>NEURAL DASHBOARD</h2>", unsafe_allow_html=True)
    
    # Holographic Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("BIO-MASS", f"{w} kg")
    m2.metric("STATURE", f"{h} cm")
    bmi = w / ((h/100)**2)
    m3.metric("PULSE BMI", f"{bmi:.1f}", delta=f"{bmi-22:.1f} vs Avg")

    # Content Area
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: culture = st.multiselect("Culture", ["South Indian", "North Indian", "Keto", "Mediterranean"], default=["South Indian"])
    with c2: goal = st.select_slider("Metabolic Goal", options=["Loss", "Maintain", "Muscle"])
    
    if st.button("⚡ GENERATE LIVE REPORT", use_container_width=True):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        p = f"Analyze: {st.session_state.raw_text}. Goal: {goal}, {age}y, {w}kg, {culture}. Professional Medical Markdown."
        resp = client.chat.completions.create(messages=[{"role": "user", "content": p}], model="llama-3.3-70b-versatile")
        st.session_state.res_text = resp.choices[0].message.content

    if st.session_state.res_text:
        with st.container(border=True):
            st.markdown(st.session_state.res_text)
            st.download_button("📥 EXPORT TXT", st.session_state.res_text, "Clinical_Report.txt")

with col_chat:
    st.markdown("<h2 style='color:#fff;'>NEURAL CHAT</h2>", unsafe_allow_html=True)
    
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state.res_text:
            st.info("Neural Engine Standby...")
        else:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask about your metrics..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                ctx = f"You are a Clinical AI. Basis: {st.session_state.res_text}. Info: {age}y, {w}kg."
                resp = client.chat.completions.create(
                    messages=[{"role": "system", "content": ctx}, *st.session_state.messages],
                    model="llama-3.3-70b-versatile"
                )
                response = resp.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
