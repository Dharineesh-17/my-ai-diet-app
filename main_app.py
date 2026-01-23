import streamlit as st
import google.generativeai as genai
import json
from fpdf import FPDF
from google.api_core import exceptions

# --- 1. PREMIUM CSS ---
st.markdown("""
    <style>
    .big-brand {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1a1c23 !important;
        font-weight: 800 !important;
        font-size: 55px !important;
        line-height: 1.1 !important;
    }
    .brand-subtext {
        color: #555e6d !important;
        font-size: 20px !important;
        padding-bottom: 30px !important;
    }
    .stApp { background-color: #f0f2f6 !important; }
    [data-testid="stSidebar"] { background-color: #1a1c23 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stButton > button:first-child {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PDF & AI HELPERS ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

# Configure Gemini Model
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error(f"API Configuration Error: {e}")

# --- 3. SIDEBAR (Login & Report Upload) ---
with st.sidebar:
    st.markdown("## 👤 User Account")
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
    else:
        st.success("Welcome, Dharineesh!")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()
    st.markdown("### 📄 Clinical Analysis")
    uploaded_file = st.file_uploader("Upload Medical Report (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])

# --- 4. HEADER ---
st.markdown('<h1 class="big-brand">🥗 AI-NutriCare Hub</h1>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtext">Precision health insights powered by Gemini AI</p>', unsafe_allow_html=True)

# --- 5. BIOMETRICS & REGIONAL INPUTS ---
# Fixed: Variables defined BEFORE calculation to avoid NameError
st.markdown("### 📊 Your Daily Biometrics & Region")
with st.container(border=True):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        weight = st.number_input("Weight (kg)", 30, 150, 70)
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col_b:
        height = st.number_input("Height (cm)", 100, 230, 175)
        goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
    with col_c:
        age = st.number_input("Age", 10, 100, 25)
        # Integrated: Regional & Food Culture inputs
        region_type = st.selectbox("Location/Region", ["Rural Village", "Suburban", "Urban City"])
        food_culture = st.text_input("Local Cuisine", "South Indian")

duration = st.slider("Plan Duration (Days)", 1, 7, 3)

# --- 6. BMR CALCULATIONS ---
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

target_cal = bmr + 500 if goal == "Muscle Gain" else bmr - 500 if goal == "Weight Loss" else bmr

# --- 7. DASHBOARD METRICS ---
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Basal Metabolic Rate", f"{int(bmr)} kcal")
m2.metric("Daily Target", f"{int(target_cal)} kcal", delta=goal)
m3.metric("Water Goal", "3.5 L", delta="Optimal")

# --- 8. CLINICAL GENERATION LOGIC ---
generate_btn = st.button("🚀 Analyze & Generate AI-NutriCare Plan", use_container_width=True)

if generate_btn:
    with st.spinner("🏥 Analyzing report and sourcing regional ingredients..."):
        try:
            # Regional Intelligence Prompt logic
            clinical_instructions = f"""
            ACT AS A CLINICAL DIETITIAN. 
            1. Extract Blood Sugar, Cholesterol, and BMI from report.
            2. REGIONAL CONSTRAINT: User lives in {region_type} and prefers {food_culture}.
            3. SUSTAINABILITY: Strictly avoid expensive imported superfoods. 
               Use ONLY locally available, affordable staples (e.g., Ragi, Amla, Moringa).
            4. Generate a {duration}-day diet for {goal} ({target_cal} kcal).
            """
            
            if uploaded_file:
                file_content = uploaded_file.getvalue()
                response = model.generate_content([
                    clinical_instructions, 
                    {"mime_type": uploaded_file.type, "data": file_content}
                ])
            else:
                response = model.generate_content(clinical_instructions)

            # --- 9. DISPLAY & EXPORT ---
            with st.container(border=True):
                st.markdown("### 📋 Clinical Nutrition Report")
                st.markdown(response.text)
                
                st.divider()
                st.subheader("📥 Export Results")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.download_button("💾 PDF", data=create_pdf(response.text), file_name="report.pdf", use_container_width=True)
                with c2:
                    st.download_button("📄 JSON", data=json.dumps({"analysis": response.text[:500]}), file_name="report.json", use_container_width=True)
                with c3:
                    st.download_button("🌐 HTML", data=f"<html>{response.text}</html>", file_name="report.html", use_container_width=True)

        except exceptions.ResourceExhausted:
            st.error("⚠️ AI Rate Limit Reached. Please wait 48 seconds and try again.")
        except Exception as e:
            st.error(f"Error: {e}")
