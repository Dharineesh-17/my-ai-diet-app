import streamlit as st
import google.generativeai as genai
import json
import time
from fpdf import FPDF
from google.api_core import exceptions

# --- 1. THEME & VISIBILITY CSS ---
st.set_page_config(page_title="AI-NutriCare Hub", layout="wide")

# Sanitized CSS - Removed all non-printable characters
st.markdown("""
<style>
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, 
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: #000000 !important;
}
.big-brand {
    font-family: 'Helvetica Neue', sans-serif;
    font-weight: 800;
    font-size: 55px;
    line-height: 1.1;
}
.stApp { background-color: #f8f9fa !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
    color: #ffffff !important;
}
[data-testid="stSidebar"] { background-color: #1a1c23 !important; }
div.stButton > button:first-child {
    background-color: #007bff !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. HELPERS ---
def create_pdf(text):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Sanitizing text to prevent encoding crashes
        clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, txt=clean_text)
        return pdf.output(dest="S").encode("latin-1")
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

# --- 3. SIDEBAR (Model Selection & Login) ---
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
        st.success("Dharineesh Logged In")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()
    st.markdown("### ⚙️ Model Settings")
    # Switch models to bypass individual quota limits
    selected_model_name = st.selectbox("Select Gemini Model", 
                                      ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-2.0-flash-exp'])

    st.divider()
    st.markdown("### 📄 Clinical Analysis")
    uploaded_file = st.file_uploader("Upload Report", type=["pdf", "png", "jpg", "jpeg"])

# --- 4. CORE AI SETUP ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Model is initialized inside the try block with proper indentation
    model = genai.GenerativeModel(selected_model_name)
except Exception as e:
    st.error("API Key error. Check Streamlit Secrets.")

# --- 5. MAIN PAGE ---
st.markdown('<h1 class="big-brand">🥗 AI-NutriCare Hub</h1>', unsafe_allow_html=True)
st.caption(f"Powered by {selected_model_name}")

# --- 6. BIOMETRICS ---
st.markdown("### 📊 Biometrics & Regional Context")
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
        region_type = st.selectbox("Location Type", ["Rural", "Suburban", "Urban"])
        food_culture = st.text_input("Local Cuisine", "South Indian")

duration = st.slider("Plan Duration (Days)", 1, 7, 3)

# Calculations
bmr = (10 * weight + 6.25 * height - 5 * age + 5) if gender == "Male" else (10 * weight + 6.25 * height - 5 * age - 161)
target_cal = bmr + 500 if goal == "Muscle Gain" else bmr - 500 if goal == "Weight Loss" else bmr

# --- 7. METRIC DASHBOARD ---
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("BMR", f"{int(bmr)} kcal")
m2.metric("Target", f"{int(target_cal)} kcal", delta=goal)
m3.metric("Water", "3.5 L", delta="Optimal")

# --- 8. CLINICAL GENERATION ---
if st.button("🚀 Analyze & Generate AI-NutriCare Plan", use_container_width=True):
    with st.spinner(f"🏥 Consulting {selected_model_name}..."):
        try:
            prompt = f"Clinical Dietitian: Create a {goal} plan for {age}y {gender}, {weight}kg. Cuisine: {food_culture}. Duration: {duration} days."
            
            if uploaded_file:
                res = model.generate_content([prompt, {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}])
            else:
                res = model.generate_content(prompt)

            with st.container(border=True):
                st.markdown("### 📋 Nutrition Report")
                st.markdown(res.text)
                
                st.divider()
                st.subheader("📥 Export")
                c1, c2, _ = st.columns(3)
                with c1:
                    pdf_data = create_pdf(res.text)
                    if pdf_data:
                        st.download_button("💾 PDF", data=pdf_data, file_name="report.pdf", use_container_width=True)
                with c2:
                    st.download_button("📄 JSON", data=json.dumps({"analysis": res.text[:500]}), file_name="report.json", use_container_width=True)

        except exceptions.ResourceExhausted:
            st.warning(f"⚠️ {selected_model_name} Limit Reached! Switching to Cooldown.")
            timer = st.empty()
            for i in range(48, 0, -1):
                timer.metric("⏳ Waiting...", f"{i}s")
                time.sleep(1)
            st.success("Ready! Try switching the model in the sidebar to skip the wait.")
        except Exception as e:
            st.error(f"Error: {e}")
