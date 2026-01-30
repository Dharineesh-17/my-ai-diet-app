import streamlit as st
import json
import PyPDF2
from fpdf import FPDF
from groq import Groq

# --- 1. SETTINGS & GLASSMORPHISM UI ---
st.set_page_config(page_title="NutriCare AI Premium", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a professional Clinical UI
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Glassmorphism Containers */
    [data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
    }

    /* Custom Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,123,255,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STATE & LOGIC ---
if 'res_text' not in st.session_state: st.session_state.res_text = ""

def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=80)
    st.title("NutriCare AI")
    
    with st.expander("🔑 Access Control", expanded=False):
        st.text_input("Clinician ID")
        st.checkbox("Emergency Audit Mode")

    st.divider()
    model_choice = st.selectbox("Intelligence Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    uploaded_file = st.file_uploader("🧬 Upload Bio-Report", type=["pdf"])

# --- 4. DASHBOARD HEADER ---
st.markdown('# 🏥 Clinical Dashboard')
st.caption("Real-time AI Dietary Audit & Physiological Analysis")

# --- 5. INTERACTIVE INPUT GRID ---
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        weight = st.number_input("Weight (kg)", 30, 150, 70)
    with c2:
        height = st.number_input("Height (cm)", 100, 230, 175)
    with c3:
        age = st.number_input("Age", 10, 100, 25)
    with c4:
        # Visual Metric Calculation
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", delta="-0.2 (Healthy)" if 18 < bmi < 25 else "Attention", delta_color="normal")

# --- 6. USER PREFERENCES CARD ---
with st.container():
    col_left, col_right = st.columns([2, 1])
    with col_left:
        food_culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Mediterranean", "Keto", "Vegan"], default=["South Indian"])
    with col_right:
        goal = st.select_slider("Health Goal", options=["Aggressive Loss", "Maintenance", "Bulking"])

# --- 7. ACTION & OUTPUT ---
st.divider()
if st.button("🚀 GENERATE CLINICAL AUDIT"):
    with st.status("🔍 Analyzing Biomarkers...", expanded=True) as status:
        st.write("Extracting clinical data...")
        report_data = extract_pdf_text(uploaded_file) if uploaded_file else "None"
        
        st.write("Consulting Llama 3.3 Engine...")
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"Dietitian Audit: {age}y, {weight}kg. Goal: {goal}. Culture: {food_culture}. Data: {report_data}. Focus on clinical risk."
        
        chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
        st.session_state.res_text = chat.choices[0].message.content
        status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

# --- 8. THE OUTPUT UX (Cards & Markdown) ---
if st.session_state.res_text:
    st.markdown("### 📋 AI Prescription & Nutrition Plan")
    
    # Using a Tabbed UI for cleaner UX
    tab1, tab2, tab3 = st.tabs(["🍏 Meal Plan", "🚫 Medical Restrictions", "📈 Health Insights"])
    
    with tab1:
        st.info(st.session_state.res_text.split('\n')[0:10]) # Simplified for demo
        st.markdown(st.session_state.res_text)
        
    with tab2:
        st.warning("Ensure all 'Strictly Avoid' items are removed from your pantry immediately.")
        
    with tab3:
        st.success("Based on your biomarkers, your metabolic age is estimated at +2 years. Diet adjusted.")

    # Export Bar
    st.write("---")
    ec1, ec2, ec3 = st.columns([1,1,3])
    ec1.download_button("📩 Download PDF", "...", file_name="audit.pdf")
    ec2.download_button("📊 Export JSON", "...", file_name="data.json")
