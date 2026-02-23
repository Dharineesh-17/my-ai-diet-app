import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. TITAN UI: NEURO-FLUX ARCHITECTURE ---
st.set_page_config(page_title="NEURO-DIET TITAN", layout="wide", page_icon="🛡️")

# High-End CSS Injection for a "Live Application" Feel
st.markdown("""
    <style>
    /* Ultra-Dark Modern Aesthetic */
    .stApp {
        background: #02040a;
        color: #e6edf3;
    }

    /* Floating Head-Up Display (HUD) Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(to bottom, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* Glassmorphism Panels */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-6q9sum {
        background: rgba(13, 17, 23, 0.7) !important;
        border: 1px solid rgba(0, 242, 254, 0.2) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(12px);
    }

    /* Neural Chat Bubble Styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        margin-bottom: 1rem !important;
    }

    /* Custom Scrollbar for Sci-Fi Feel */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #02040a; }
    ::-webkit-scrollbar-thumb { background: #00f2fe; border-radius: 10px; }

    /* Floating Sidebar Hack */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(0, 242, 254, 0.3);
        background: rgba(1, 4, 9, 0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Persistent State Management
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': "", 'messages': []}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. CORE INTELLIGENCE ---
@st.cache_resource
def load_ocr_engine(): return easyocr.Reader(['en'])

def neural_ingest(file):
    with st.status("🧬 Ingesting Biological Data...", expanded=True) as status:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            text = " ".join([p.extract_text() for p in reader.pages])
        else:
            reader = load_ocr_engine()
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
            status.update(label="✅ Neural Sync Complete", state="complete")
        except: status.update(label="⚠️ Parsing Variance Detected", state="error")

# --- 3. THE NEURO-FLUX LIVE EDITOR (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h1 style='color:#00f2fe; text-align:center;'>🛡️ TITAN CORE</h1>", unsafe_allow_html=True)
    st.divider()
    
    with st.container(border=True):
        st.subheader("📡 Input Stream")
        src_file = st.file_uploader("Drop Lab Diagnostics", type=["pdf", "png", "jpg"])
        if src_file and st.button("🔥 TRIGGER SYNC", use_container_width=True):
            neural_ingest(src_file)

    st.markdown("### 🎚️ Live Parameter Tuning")
    # Live sliders trigger immediate re-calc of the main HUD
    st.session_state.w = st.slider("Biological Mass (kg)", 30.0, 200.0, float(st.session_state.w))
    st.session_state.h = st.slider("Height Index (cm)", 100.0, 250.0, float(st.session_state.h))
    st.session_state.a = st.number_input("Biological Age", 1, 120, int(st.session_state.a))
    
    st.divider()
    if st.button("🔴 PURGE SESSION", use_container_width=True):
        st.session_state.update({'messages': [], 'res_text': "", 'raw_text': ""})
        st.rerun()

# --- 4. THE TITAN COMMAND CONSOLE ---
st.markdown("<h4 style='color:#8b949e; letter-spacing: 2px;'>SYSTEM STATUS: OPERATIONAL</h4>", unsafe_allow_html=True)

# Floating HUD Row
hud1, hud2, hud3, hud4 = st.columns(4)
hud1.metric("CURRENT MASS", f"{st.session_state.w} KG")
hud2.metric("HEIGHT INDEX", f"{st.session_state.h} CM")
calc_bmi = st.session_state.w / ((st.session_state.h/100)**2)
hud3.metric("NEURAL BMI", f"{calc_bmi:.1f}")
hud4.metric("SYSTEM LOAD", "MODERATE", delta="Optimal AI", delta_color="normal")



[Image of the human digestive system]


st.divider()

# Dual-Pane Architecture
col_report, col_chat = st.columns([1.2, 1], gap="large")

with col_report:
    st.markdown("### 📋 Clinical Synthesis")
    t1, t2 = st.columns(2)
    with t1: culture = st.selectbox("Dietary Context", ["South Indian", "North Indian", "Keto", "Mediterranean"])
    with t2: goal = st.select_slider("Metabolic Vector", options=["Loss", "Maintain", "Muscle"])
    
    if st.button("🚀 EXECUTE AI SYNTHESIS", use_container_width=True):
        with st.spinner("Accessing Groq Neural Core..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Data: {st.session_state.raw_text}. Goal: {goal}, Age: {st.session_state.a}, Mass: {st.session_state.w}kg, Culture: {culture}."
            resp = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
            st.session_state.res_text = resp.choices[0].message.content
            st.toast("Report Synthesized", icon="⚡")

    if st.session_state.res_text:
        st.markdown(f"""<div style='background:rgba(0,242,254,0.05); padding:20px; border-radius:15px; border: 1px solid rgba(0,242,254,0.2);'>
            {st.session_state.res_text}</div>""", unsafe_allow_html=True)
        st.download_button("📥 ARCHIVE REPORT", st.session_state.res_text, file_name="Bio_Synthesis.txt", use_container_width=True)

with col_chat:
    st.markdown("### 🧠 Neural Consultation")
    
    # Static container for chat with specific height
    chat_box = st.container(height=550, border=True)
    
    if not st.session_state.res_text:
        chat_box.info("Awaiting Diagnostic Report for Consultation...")
    else:
        with chat_box:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])

    if chat_input := st.chat_input("Query the Neural Core..."):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        with chat_box:
            with st.chat_message("user"): st.markdown(chat_input)
            with st.chat_message("assistant"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                system_p = f"Act as Clinical Nutritionist. Reference Report: {st.session_state.res_text}. Subject: {st.session_state.a}y, {st.session_state.w}kg."
                resp = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_p}, *st.session_state.messages],
                    model="llama-3.3-70b-versatile"
                )
                full_resp = resp.choices[0].message.content
                st.markdown(full_resp)
                st.session_state.messages.append({"role": "assistant", "content": full_resp})
