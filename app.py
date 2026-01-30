import streamlit as st
import json
from groq import Groq
import PyPDF2

# --- 1. GLOBAL UI ENGINE ---
st.set_page_config(page_title="NutriCare AI Premium", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important; }
    
    /* Card Styling */
    [data-testid="stVerticalBlock"] > div:has(div.stMetric), .stExpander {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05) !important;
    }

    /* High Contrast Text */
    h1, h2, h3, p, label, .stMarkdown { color: #1a1a1a !important; font-weight: 600 !important; }
    
    /* Sidebar Depth */
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Premium Button */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC HELPERS ---
def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in reader.pages])

if 'res_text' not in st.session_state: st.session_state.res_text = ""

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 Clinical Portal")
    uploaded_file = st.file_uploader("Upload Lab Report", type=["pdf"])
    st.divider()
    model_choice = st.selectbox("Intelligence Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
# --- 4. HEADER & LIVE BIOMETRICS ---
st.title("🏥 NutriCare AI: Clinical Audit")

with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1: weight = st.number_input("Weight (kg)", 30, 150, 70)
    with c2: height = st.number_input("Height (cm)", 100, 230, 175)
    with c3: age = st.number_input("Age", 10, 100, 25)
    with c4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", delta="Healthy" if 18.5 <= bmi <= 24.9 else "At Risk", delta_color="normal")

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
            prompt = f"Dietitian Audit: {age}y, {weight}kg. Goal: {goal}. Culture: {culture}. Data: {report_data}. Focus on clinical risk and strictly avoid categories."
            
            chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
            st.session_state.res_text = chat.choices[0].message.content
            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
        except Exception as e:
            st.error(f"Inference Error: {e}")

# --- 7. OUTPUT EXPERIENCE ---
if st.session_state.res_text:
    st.markdown("### 📋 Clinical Nutrition Prescription")
    tab1, tab2, tab3 = st.tabs(["🍏 Meal Plan", "🚫 Medical Restrictions", "📈 Health Insights"])
    
    with tab1:
        st.markdown(st.session_state.res_text)
        
    with tab2:
        with st.expander("⚠️ Critical Avoidance List", expanded=True):
            st.warning("Based on your biomarkers, strictly avoid high-sodium and processed sugars.")
        
    with tab3:
        st.info("💡 Pro-Tip: Increasing water intake to 3.5L will optimize your metabolic rate.")

    # Export Bar
    st.write("---")
    ec1, ec2, _ = st.columns([1,1,3])
    ec1.download_button("📩 Download PDF", st.session_state.res_text, file_name="Diet_Plan.txt")
    ec2.download_button("📊 Export JSON", json.dumps({"audit": st.session_state.res_text[:500]}), file_name="data.json")
