import streamlit as st
import json
from groq import Groq
import PyPDF2

# --- 1. GLOBAL UI ENGINE (VISIBILITY MASTER FIX) ---
st.set_page_config(page_title="NutriCare AI Premium", layout="wide")

st.markdown("""
    <style>
    /* 1. Background Fix */
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important; }
    
    /* 2. FORCE BLACK TEXT ON ALL LABELS (The fix for your screenshot) */
    /* Target labels for number inputs, selects, and sliders specifically */
    .stWidget label, p, [data-testid="stMetricLabel"], .stMarkdown p {
        color: #000000 !important; 
        font-weight: 800 !important;
        opacity: 1 !important;
    }

    /* 3. Input Field Boxes - Keep them dark for contrast */
    [data-testid="stNumberInput"] div div input {
        background-color: #1a1c23 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    /* 4. Glassmorphism Card Fix */
    [data-testid="stVerticalBlock"] > div:has(div.stMetric), .stExpander {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
    }

    /* 5. Metrics styling */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 900 !important;
    }

    /* 6. Sidebar depth */
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPERS ---
def extract_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "".join([p.extract_text() for p in reader.pages])
    except: return ""

if 'res_text' not in st.session_state: st.session_state.res_text = ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("📂 Clinical Portal")
    uploaded_file = st.file_uploader("Upload Lab Report", type=["pdf"])
    st.divider()
    # Note: Use llama-3.3-70b-versatile for better clinical accuracy
    model_choice = st.selectbox("Intelligence Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

# --- 4. HEADER & BIOMETRICS ---
st.markdown('# 🏥 NutriCare AI: Clinical Audit')

with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1: weight = st.number_input("Weight (kg)", 30.0, 150.0, 70.0)
    with c2: height = st.number_input("Height (cm)", 100.0, 230.0, 175.0)
    with c3: age = st.number_input("Age", 10, 100, 25)
    with c4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", delta="Healthy" if 18.5 <= bmi <= 25 else "At Risk")

# --- 5. PREFERENCES ---
with st.container():
    cl, cr = st.columns([2, 1])
    with cl: culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto"], default=["South Indian"])
    with cr: goal = st.select_slider("Health Goal", options=["Weight Loss", "Maintenance", "Bulking"])

# --- 6. ACTION ---
st.divider()
if st.button("🚀 GENERATE CLINICAL AUDIT", use_container_width=True):
    with st.status("🔍 Analyzing Biomarkers...", expanded=True) as status:
        report_data = extract_pdf_text(uploaded_file) if uploaded_file else "No report."
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Dietitian: Create plan for {age}y, {weight}kg. Goal: {goal}. Culture: {culture}. Report: {report_data}."
            chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
            st.session_state.res_text = chat.choices[0].message.content
            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
        except Exception as e:
            st.error(f"Error: {e}")

# --- 7. OUTPUT ---
if st.session_state.res_text:
    tab1, tab2 = st.tabs(["🍏 Meal Plan", "📈 Insights"])
    with tab1: st.markdown(st.session_state.res_text)
    with tab2: st.info("💡 Tip: Increasing fiber intake will help stabilize blood sugar levels.")
