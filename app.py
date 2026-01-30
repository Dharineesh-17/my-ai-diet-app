import streamlit as st
import json
from groq import Groq
import PyPDF2

# --- 1. GLOBAL UI ENGINE (VISIBILITY FIX) ---
st.set_page_config(page_title="NutriCare AI Premium", layout="wide")

st.markdown("""
    <style>
    /* 1. Background Fix */
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important; }
    
    /* 2. Label Visibility Fix: Specifically targeting widget labels */
    .stMarkdown p, label, .stSelectbox label, .stNumberInput label, .stMultiSelect label {
        color: #000000 !important; 
        font-weight: 800 !important;
        font-size: 1.05rem !important;
    }

    /* 3. Input Text Fix: Ensures text inside boxes is visible */
    input { color: #000000 !important; font-weight: 600 !important; }

    /* 4. Metric Header Fix */
    [data-testid="stMetricLabel"] { color: #1a1a1a !important; font-weight: 700 !important; }

    /* 5. Glassmorphism Card Fix */
    [data-testid="stVerticalBlock"] > div:has(div.stMetric), .stExpander {
        background: rgba(255, 255, 255, 0.85) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }

    /* 6. Sidebar Text Fix */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
    }
    
    /* 7. Button Premium Look */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #1e40af, #3b82f6) !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC HELPERS ---
def extract_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "".join([p.extract_text() for p in reader.pages])
    except: return "Extraction failed."

if 'res_text' not in st.session_state: st.session_state.res_text = ""

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 Clinical Portal")
    uploaded_file = st.file_uploader("Upload Lab Report", type=["pdf"])
    st.divider()
    # Fixed model list
    model_choice = st.selectbox("Intelligence Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
# --- 4. HEADER & LIVE BIOMETRICS ---
st.title("🏥 NutriCare AI: Clinical Audit")

with st.container():
    # Consolidating inputs to one clear row
    c1, c2, c3, c4 = st.columns(4)
    with c1: weight = st.number_input("Weight (kg)", 30.0, 150.0, 70.0)
    with c2: height = st.number_input("Height (cm)", 100.0, 230.0, 175.0)
    with c3: age = st.number_input("Age", 10, 100, 25)
    with c4:
        bmi = weight / ((height/100)**2)
        # Dynamic color labeling based on BMI range
        bmi_status = "Healthy" if 18.5 <= bmi <= 24.9 else "At Risk"
        st.metric("Live BMI", f"{bmi:.1f}", delta=bmi_status, delta_color="normal")

# --- 5. PREFERENCES & GOALS ---
with st.container():
    col_left, col_right = st.columns([2, 1])
    with col_left:
        culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Mediterranean", "Keto"], default=["South Indian"])
    with col_right:
        goal = st.select_slider("Health Goal", options=["Weight Loss", "Maintenance", "Bulking"])

# --- 6. ACTION ENGINE ---
st.divider()
if st.button("🚀 GENERATE CLINICAL AUDIT", use_container_width=True):
    with st.status("🔍 Analyzing Biomarkers...", expanded=True) as status:
        report_data = extract_pdf_text(uploaded_file) if uploaded_file else "No report provided."
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Dietitian: Create plan for {age}y, {weight}kg. Goal: {goal}. Culture: {culture}. Report: {report_data}. Format with clear headers."
            chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
            st.session_state.res_text = chat.choices[0].message.content
            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
        except Exception as e:
            st.error(f"Inference Error: {e}")

# --- 7. OUTPUT EXPERIENCE ---
if st.session_state.res_text:
    st.markdown("### 📋 Clinical Nutrition Prescription")
    tab1, tab2, tab3 = st.tabs(["🍏 Meal Plan", "🚫 Restrictions", "📈 Health Insights"])
    
    with tab1:
        st.markdown(st.session_state.res_text)
        
    with tab2:
        with st.expander("⚠️ Critical Avoidance List", expanded=True):
            st.warning("Ensure all processed sugars are removed from the plan.")
        
    with tab3:
        # Re-introducing metrics for the final report
        m1, m2 = st.columns(2)
        m1.metric("Water Intake", "3.5 L", "Optimal")
        m2.metric("Target Calories", f"{int(weight * 22)} kcal")
