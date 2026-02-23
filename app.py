import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image
import base64

# --- 1. EXTRAORDINARY UI & THEME ENGINE ---
st.set_page_config(page_title="NEURO-DIET | Clinical AI", layout="wide", page_icon="🧪")

# Custom CSS for Glassmorphism & Premium Medical Look
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #0e1525, #000000);
    }
    
    /* Glassmorphism Cards */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Professional Button Styling */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        color: black;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 20px rgba(79, 172, 254, 0.4);
    }

    /* Custom Chat Styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': "", 'messages': []}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. CORE ENGINES (OCR & AI) ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def process_file(file):
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
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        v = json.loads(resp.choices[0].message.content)
        st.session_state.update({'w': float(v.get('w', 70)), 'h': float(v.get('h', 175)), 'a': int(v.get('a', 25))})
    except: st.toast("Manual check required for vitals.")

# --- 3. SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063067.png", width=80)
    st.title("NEURO-DIET v2.0")
    st.caption("Advanced Clinical Intelligence")
    
    upload = st.file_uploader("Upload Lab Diagnostics", type=["pdf", "png", "jpg"])
    if upload and st.button("🧬 INGEST DATA"):
        with st.status("Parsing Bio-Markers..."):
            process_file(upload)
    
    st.divider()
    m_choice = st.selectbox("Intelligence Core", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if st.button("🔄 Reset Environment"):
        st.session_state.update({'messages': [], 'res_text': ""})
        st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🧪 Clinical Intelligence Dashboard")

# Glassmorphism Vitals Row
c1, c2, c3, c4 = st.columns(4)
w = c1.number_input("Weight (kg)", 30.0, 200.0, key="w")
h = c2.number_input("Height (cm)", 100.0, 250.0, key="h")
age = c3.number_input("Age", 1, 120, key="a")
bmi = w / ((h/100)**2)
c4.metric("Live BMI", f"{bmi:.1f}", "Healthy" if 18.5 <= bmi <= 25 else "Warning")

# Layout Split
tab1, tab2 = st.tabs(["📊 Diagnostic Report", "💬 Neural Consultation"])

with tab1:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto", "Paleo"], default=["South Indian"])
    with col_b:
        goal = st.select_slider("Metabolic Goal", options=["Loss", "Maintain", "Muscle"])
    
    if st.button("🚀 SYNTHESIZE NUTRITION PLAN", use_container_width=True):
        with st.spinner("Aligning Clinical Parameters..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            p = f"Analyze: {st.session_state.raw_text}. Create {goal} plan for {age}y, {w}kg ({culture}). Format: Professional Medical Report."
            resp = client.chat.completions.create(messages=[{"role": "user", "content": p}], model=m_choice)
            st.session_state.res_text = resp.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": "Report Synthesized Successfully."})

    if st.session_state.res_text:
        st.markdown("### 📋 Bio-Aligned Prescription")
        st.info(st.session_state.res_text)
        
        # Download Action
        st.download_button("📥 EXPORT MEDICAL REPORT", st.session_state.res_text, f"Report_{age}.txt", "text/plain")

with tab2:
    if not st.session_state.res_text:
        st.warning("Awaiting Diagnostic Report Synthesis...")
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask about specific markers..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                ctx = f"Context: {st.session_state.res_text}. Patient: {age}y, {w}kg. Be clinical."
                resp = client.chat.completions.create(
                    messages=[{"role": "system", "content": ctx}, *st.session_state.messages],
                    model=m_choice
                )
                st.markdown(resp.choices[0].message.content)
                st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})
