import streamlit as st
import google.generativeai as genai
import json
import time
from fpdf import FPDF
from google.api_core import exceptions

# --- 1. PREMIUM CSS ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, 
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
    .big-brand { font-family: 'Helvetica Neue'; font-weight: 800; font-size: 55px; }
    .stApp { background-color: #f8f9fa !important; }
    [data-testid="stSidebar"] { background-color: #1a1c23 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stButton > button:first-child {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPERS ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Using 2.0 Flash to avoid 404 error
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
except Exception as e:
    st.error(f"API Setup Error: {e}")

# --- 3. SIDEBAR ---
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

# --- 4. MAIN UI ---
st.markdown('<h1 class="big-brand">🥗 AI-NutriCare Hub</h1>', unsafe_allow_html=True)

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
        region_type = st.selectbox("Location", ["Rural Village", "Suburban", "Urban City"])

duration = st.slider("Plan Duration (Days)", 1, 7, 3)

# --- 5. AI GENERATION & COUNTDOWN ---
if st.button("🚀 Analyze & Generate AI-NutriCare Plan", use_container_width=True):
    with st.spinner("🏥 Analyzing..."):
        try:
            prompt = f"Diet for {goal} in {region_type} area."
            if uploaded_file:
                res = model.generate_content([prompt, {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}])
            else:
                res = model.generate_content(prompt)
            st.markdown(res.text)

        except exceptions.ResourceExhausted:
            st.warning("⚠️ Rate Limit Reached. Please wait for the cooldown.")
            # --- START COUNTDOWN RUN ---
            count_placeholder = st.empty()
            progress_bar = st.progress(0)
            for seconds_left in range(60, 0, -1):
                count_placeholder.metric("Cooldown Timer", f"{seconds_left}s")
                progress_bar.progress((60 - seconds_left) / 60)
                time.sleep(1)
            count_placeholder.empty()
            progress_bar.empty()
            st.success("✅ Ready! You can now click the button again.")
            
        except Exception as e:
            st.error(f"Error: {e}")
