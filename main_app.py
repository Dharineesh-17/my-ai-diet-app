import streamlit as st
import google.generativeai as genai
import json
import time
from fpdf import FPDF
from google.api_core import exceptions

# --- 1. THEME & VISIBILITY CSS ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, 
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    .big-brand { font-family: 'Helvetica Neue'; font-weight: 800; font-size: 55px; }
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
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPERS ---
def create_pdf(text):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, txt=clean_text)
        return pdf.output(dest="S").encode("latin-1")
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return b""

# --- 3. CORE AI SETUP ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Using 'latest' to avoid 404 errors
    model = genai.GenerativeModel('gemini-3.0-flash-exp') 
except Exception as e:
    st.error("API Key missing. Add GOOGLE_API_KEY to Streamlit Secrets.")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("## 👤 User Account")
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        if st.button("Login", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
    else:
        st.success("Dharineesh Logged In")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    st.divider()
    uploaded_file = st.file_uploader("Upload Medical Report", type=["pdf", "png", "jpg", "jpeg"])

# --- 5. MAIN PAGE ---
st.markdown('<h1 class="big-brand">🥗 AI-NutriCare Hub</h1>', unsafe_allow_html=True)

# --- 6. BIOMETRICS ---
with st.container(border=True):
    col_a, col_b, col_c = st.columns(3) 
    with col_a:
        weight = st.number_input("Weight (kg)", 30, 150, 70)
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col_b:
        height = st.number_input("Height (cm)", 100, 230, 175)
        goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain"])
    with col_c:
        age = st.number_input("Age", 10, 100, 25)
        region = st.selectbox("Location", ["Rural Village", "Suburban", "Urban City"])

# Calculations
bmr = (10*weight + 6.25*height - 5*age + 5) if gender=="Male" else (10*weight + 6.25*height - 5*age - 161)
target_cal = bmr + 500 if goal == "Muscle Gain" else bmr - 500

# Metrics
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("BMR", f"{int(bmr)} kcal")
m2.metric("Target", f"{int(target_cal)} kcal", delta=goal)
m3.metric("Water", "3.5 L")

# --- 7. GENERATION & COUNTDOWN ---
if st.button("🚀 Analyze & Generate AI-NutriCare Plan", use_container_width=True):
    with st.spinner("🏥 Analyzing..."):
        try:
            prompt = f"Diet for {goal} in {region} at {target_cal} kcal."
            if uploaded_file:
                res = model.generate_content([prompt, {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}])
            else:
                res = model.generate_content(prompt)
            
            st.markdown("### 📋 Clinical Nutrition Report")
            st.markdown(res.text)
            st.download_button("💾 PDF Report", data=create_pdf(res.text), file_name="report.pdf")

        except exceptions.ResourceExhausted:
            st.warning("⚠️ API Rate Limit Reached!")
            
            # --- LIVE 48s COUNTDOWN ---
            count_placeholder = st.empty()
            progress_bar = st.progress(0)
            for i in range(48, 0, -1):
                count_placeholder.metric("⏳ Cooldown Timer", f"{i}s")
                progress_bar.progress((48 - i) / 48)
                time.sleep(1)
            
            count_placeholder.empty()
            progress_bar.empty()
            st.success("✅ Ready! Click the button again.")
            
        except Exception as e:
            st.error(f"Error: {e}")
