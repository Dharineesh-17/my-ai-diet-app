import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. QUANTUM UI: ARCHITECTURAL SUPREMACY ---
st.set_page_config(page_title="🥗DIET PLAN GENERATOR", layout="wide", page_icon="🔮")

# PROVING UI SUPREMACY: High-End CSS Injection
st.markdown("""
    <style>
    /* Kinetic Dark Engine Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0d1117 0%, #010409 100%);
        color: #c9d1d9;
    }

    /* Floating Glass Modules */
    div[data-testid="stColumn"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 25px;
        padding: 25px !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    div[data-testid="stColumn"]:hover {
        border: 1px solid #00f2fe;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.2);
        transform: scale(1.02);
    }

    /* Neon Pulsing Buttons */
    .stButton>button {
        background: transparent !important;
        border: 2px solid #00f2fe !important;
        color: #00f2fe !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: 0.4s !important;
    }
    .stButton>button:hover {
        background: #00f2fe !important;
        color: #000 !important;
        box-shadow: 0 0 40px #00f2fe;
    }

    /* Floating Sidebar Bio-Panel */
    [data-testid="stSidebar"] {
        background-color: rgba(1, 4, 9, 0.95) !important;
        border-right: 2px solid #00f2fe !important;
        box-shadow: 10px 0 30px rgba(0, 242, 254, 0.1);
    }

    /* Animated Header */
    .h1-title {
        background: linear-gradient(90deg, #00f2fe, #4facfe, #00f2fe);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        font-weight: 900;
        text-align: center;
    }
    @keyframes shine { to { background-position: 200% center; } }
    </style>
    """, unsafe_allow_html=True)

# State Engine Initialization
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': "", 'messages': []}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. THE NEURAL CORE ---
@st.cache_resource
def get_ocr(): return easyocr.Reader(['en'])

def neural_sync(file):
    with st.status("🚀 Syncing with Neural Core...", state="running") as status:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            text = " ".join([p.extract_text() for p in reader.pages])
        else:
            text = " ".join([res[1] for res in get_ocr().readtext(np.array(Image.open(file)))])
        st.session_state.raw_text = text
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Extract weight, height, age: '{text}'. JSON: {{\"w\":num, \"h\":num, \"a\":num}}"}],
                model="llama-3.1-8b-instant", response_format={"type": "json_object"}
            )
            v = json.loads(resp.choices[0].message.content)
            st.session_state.update({'w': float(v.get('w', 70)), 'h': float(v.get('h', 175)), 'a': int(v.get('a', 25))})
            status.update(label="🧬 Bio-Data Harmonized!", state="complete")
        except: status.update(label="⚠️ Manual Recalibration Required", state="error")

# --- 3. LIVE BIO-COMMAND SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 class='h1-title'>BIO-CONTROL</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3843/3843183.png", width=100)
    
    with st.expander("📡 DATA UPLINK", expanded=True):
        up = st.file_uploader("", type=["pdf", "png", "jpg"])
        if up and st.button("INITIALIZE SYNC"): neural_sync(up)

    st.markdown("### 🎚️ PARAMETER TUNING")
    # Immediate State Binding
    st.session_state.w = st.slider("MASS (KG)", 30.0, 200.0, float(st.session_state.w))
    st.session_state.h = st.slider("ALTITUDE (CM)", 100.0, 250.0, float(st.session_state.h))
    st.session_state.a = st.number_input("AGE CYCLE", 1, 120, int(st.session_state.a))
    
    if st.button("🔴 RESET ALL"):
        st.session_state.update({'messages': [], 'res_text': ""})
        st.rerun()

# --- 4. QUANTUM DASHBOARD (LIVE MODULES) ---
st.markdown("<h1 class='h1-title' style='font-size: 3rem;'>🥗AI-BASED DIET PLAN GENERATOR</h1>", unsafe_allow_html=True)

# LIVE TELEMETRY HUD
hud_1, hud_2, hud_3 = st.columns(3)
with hud_1:
    st.metric("BIOMASS INDEX", f"{st.session_state.w} kg", delta="Live Sync")
with hud_2:
    st.metric("HEIGHT STATS", f"{st.session_state.h} cm")
with hud_3:
    bmi = st.session_state.w / ((st.session_state.h/100)**2)
    st.metric("NEURAL BMI", f"{bmi:.1f}", delta="Optimal" if 18.5<=bmi<=25 else "Variance", delta_color="inverse")


st.markdown("---")

# LIVE MODULAR INTERFACE
left_mod, right_mod = st.columns([1.2, 1], gap="medium")

with left_mod:
    st.markdown("### 🧬 SYNTHESIS ENGINE")
    c1, c2 = st.columns(2)
    culture = c1.selectbox("Culture Mode", ["South Indian", "North Indian", "Keto", "Paleo"])
    goal = c2.select_slider("Metabolic Vector", options=["Loss", "Maintain", "Muscle"])
    
    if st.button("🔥 SYNTHESIZE BIO-PLAN", use_container_width=True):
        with st.spinner("Accessing Llama-3 Neural Stream..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            p = f"Lab Data: {st.session_state.raw_text}. Goal: {goal}, Age: {st.session_state.a}, Mass: {st.session_state.w}kg, Culture: {culture}."
            resp = client.chat.completions.create(messages=[{"role": "user", "content": p}], model="llama-3.3-70b-versatile")
            st.session_state.res_text = resp.choices[0].message.content

    if st.session_state.res_text:
        st.markdown(f"<div style='background:rgba(0, 242, 254, 0.05); border-left: 5px solid #00f2fe; padding:20px; border-radius:15px;'>{st.session_state.res_text}</div>", unsafe_allow_html=True)
        st.download_button("📥 ARCHIVE DATA", st.session_state.res_text, file_name="BioReport.txt")

with right_mod:
    st.markdown("### 🧠 NEURAL UPLINK (CHAT)")
    chat_box = st.container(height=500, border=True)
    
    with chat_box:
        if not st.session_state.res_text:
            st.info("Awaiting Synthesis...")
        else:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])

    if query := st.chat_input("Query the Neural Core..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with chat_box:
            with st.chat_message("user"): st.markdown(query)
            with st.chat_message("assistant"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                ctx = f"System: Clinical AI. Report: {st.session_state.res_text}. Patient: {st.session_state.a}y, {st.session_state.w}kg."
                resp = client.chat.completions.create(messages=[{"role": "system", "content": ctx}, *st.session_state.messages], model="llama-3.3-70b-versatile")
                ans = resp.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
