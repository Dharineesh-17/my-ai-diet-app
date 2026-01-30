import streamlit as st
from groq import Groq
import PyPDF2
from PIL import Image
import easyocr
import numpy as np
import re

# --- 1. UI SETUP ---
st.set_page_config(page_title="AI Diet Plan Generator", layout="wide")
# Add this to your existing CSS block
st.markdown("""
    <style>
    /* Force Results Area to be High Contrast */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 0 0 15px 15px !important;
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

# Initialize session state for vitals
if 'weight' not in st.session_state: st.session_state.weight = 70.0
if 'height' not in st.session_state: st.session_state.height = 175.0
if 'age' not in st.session_state: st.session_state.age = 25
if 'res_text' not in st.session_state: st.session_state.res_text = ""

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important; }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 15px; padding: 25px !important;
    }
    .stTabs [data-baseweb="tab-panel"] * { color: #1a1a1a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. EXTRACTION ENGINE ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def extract_data(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([p.extract_text() for p in reader.pages])
    else:
        reader = load_ocr()
        image = Image.open(uploaded_file)
        results = reader.readtext(np.array(image))
        return " ".join([res[1] for res in results])

# --- 3. THE AUTO-FILL LOGIC (The Missing Piece) ---
def auto_fill_vitals(text):
    """Uses a quick AI call to grab just the numbers for the dashboard"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    parser_prompt = f"Extract Weight(kg), Height(cm), and Age from this text: '{text}'. Return ONLY JSON like {{\"w\": 70, \"h\": 175, \"a\": 25}}. If not found, use current values: {st.session_state.weight}, {st.session_state.height}, {st.session_state.age}"
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": parser_prompt}],
        model="llama-3.1-8b-instant", # Fast model for extraction
        response_format={"type": "json_object"}
    )
    data = json.loads(response.choices[0].message.content)
    st.session_state.weight = float(data.get('w', st.session_state.weight))
    st.session_state.height = float(data.get('h', st.session_state.height))
    st.session_state.age = int(data.get('a', st.session_state.age))

# --- 4. INPUT SECTION ---
st.title("🏥 NutriCare AI: Clinical Audit")

with st.sidebar:
    st.markdown("### 📂 1. Upload Report")
    uploaded_file = st.file_uploader("Drop PDF or Screenshot here", type=["pdf", "png", "jpg", "jpeg"])
    
    if st.button("🔍 PRE-SCAN FILE"):
        if uploaded_file:
            with st.spinner("Scanning for vitals..."):
                text = extract_data(uploaded_file)
                auto_fill_vitals(text)
                st.success("Vitals Updated from File!")
        else:
            st.error("Upload a file first!")

with st.container():
    st.markdown("### ⚖️ 2. Verify Vitals")
    c1, c2, c3, c4 = st.columns(4)
    # Use session_state to allow the AI to 'fill in' the boxes
    weight = c1.number_input("Weight (kg)", 30.0, 200.0, key="weight")
    height = c2.number_input("Height (cm)", 100.0, 250.0, key="height")
    age = c3.number_input("Age", 1, 100, key="age")
    with c4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "At Risk" if bmi > 25 else "Healthy")

    if st.button("🚀 GENERATE FINAL PLAN", use_container_width=True):
        if not uploaded_file:
            st.error("Upload a file first!")
        else:
            with st.status("🧬 Finalizing Analysis...") as status:
                extracted_text = extract_data(uploaded_file)
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Dietitian: Create plan using these REAL vitals: {weight}kg, {height}cm, {age}y. Lab Data: {extracted_text}"
                chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.res_text = chat.choices[0].message.content
                status.update(label="✅ Plan Ready!", state="complete")

# --- 5. OUTPUT ---
if st.session_state.res_text:
    st.divider()
    t1, t2 = st.tabs(["🍏 Clinical Plan", "🔍 Insights"])
    with t1: st.markdown(st.session_state.res_text)
