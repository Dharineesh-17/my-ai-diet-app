import streamlit as st
import google.generativeai as genai
import json
from fpdf import FPDF
st.markdown("""
    <style>
    /* 1. BOOSTED MAIN HEADER */
    .big-brand {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1a1c23 !important;
        font-weight: 800 !important;
        font-size: 55px !important; /* Huge size */
        letter-spacing: -1.5px !important; /* Modern tight spacing */
        margin-bottom: 0px !important;
        padding-top: 20px !important;
        line-height: 1.1 !important;
    }

    /* 2. SUBTITLE STYLING */
    .brand-subtext {
        color: #555e6d !important;
        font-size: 20px !important;
        margin-top: -10px !important;
        padding-bottom: 30px !important;
    }

    /* 3. CARD ENHANCEMENT */
    /* This makes your input boxes look even cleaner against the big title */
    .stNumberInput, .stSelectbox {
        border: 1px solid #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APPLY THE NEW LARGE TITLE ---
st.markdown('<h1 class="big-brand">🥗 AI Nutrition & Health Hub</h1>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtext">Precision health insights powered by Gemini AI</p>', unsafe_allow_html=True)
# --- 2. PREMIUM CSS ---
st.markdown("""
    <style>
    /* 1. MAIN BACKGROUND - Clean Off-White */
    .stApp {
        background-color: #f0f2f6 !important;
    }

    /* 2. TEXT COLOR - High Contrast Charcoal */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #1a1c23 !important;
    }

    /* 3. METRIC CARDS - Bold and Clear */
    [data-testid="stMetricLabel"] {
        color: #555e6d !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #1a1c23 !important;
        font-size: 32px !important;
        font-weight: 800 !important;
    }

    /* 4. SIDEBAR - Dark Professional look to contrast with Main Page */
    [data-testid="stSidebar"] {
        background-color: #1a1c23 !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important; /* Force sidebar text to be pure white */
    }
    [data-testid="stSidebar"] .stTextInput input {
        color: #1a1c23 !important; /* Keep input text dark so you can see what you type */
    }

    /* 5. PREMIUM BUTTON - Vibrant Health Blue */
    div.stButton > button:first-child {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
    }
    
    /* 6. INPUT BOXES - White with subtle shadow */
    .stNumberInput, .stSelectbox, .stSlider {
        background-color: white !important;
        border-radius: 10px !important;
        padding: 5px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)
# --- 3. PDF & AI HELPERS ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-3-flash-preview')
except:
    st.error("API Key missing in Secrets!")

# --- 4. SIDEBAR (Login & Settings Only) ---
with st.sidebar:
    st.markdown("## 👤 User Account")
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Login"):
            st.session_state.logged_in = True
            st.rerun()
    else:
        st.success("Welcome, Dharineesh!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()
    st.markdown("## ⚙️ App Settings")
    st.selectbox("Theme", ["Light Mode", "Dark Mode"])
    st.toggle("Enable AI Notifications", value=True)
    #new addings for medical report 
    st.markdown("### 📄 Medical Report Analysis")
    uploaded_file = st.file_uploader("Upload your medical report (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success("Report uploaded successfully! AI is analyzing your health markers...")

# Input Section in Main Page
st.markdown("### 📊 Your Daily Biometrics")
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
        duration = st.slider("Plan Duration (Days)", 1, 7, 3)

# 6. CALCULATIONS
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

target_cal = bmr + 500 if goal == "Muscle Gain" else bmr - 500 if goal == "Weight Loss" else bmr

# 7. DASHBOARD METRICS
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Basal Metabolic Rate", f"{int(bmr)} kcal")
m2.metric("Daily Target", f"{int(target_cal)} kcal", delta=goal)
m3.metric("Water Goal", "3.5 L", delta="Optimal")

# 8. GENERATION
generate_btn = st.button("🚀 Generate AI-NutriCare Plan", use_container_width=True)

if generate_btn:
    with st.spinner("AI-NutriCare is analyzing your medical profile..."):
        try:
            # 1. Build the Medical Context
            if uploaded_file is not None:
                # Prepare the image/PDF for Gemini
                file_content = uploaded_file.getvalue()
                user_context = [
                    f"""Act as a Clinical Nutritionist. Analyze this report for Blood Sugar, Cholesterol, and BMI. 
                    Then generate a {duration}-day {goal} diet plan for a {age}yo {gender} weighing {weight}kg.
                    Adjust the plan if you detect any medical abnormalities in the report.""",
                    {"mime_type": uploaded_file.type, "data": file_content}
                ]
            else:
                user_context = f"Act as a Clinical Nutritionist. Create a {duration}-day {goal} plan for {target_cal:.0f} calories for a {age}yo {gender}."

            # 2. Call Gemini
            response = model.generate_content(user_context)
            
            # 3. Display Results
            with st.container(border=True):
                st.markdown("### 📝 Your Personalized Medical Nutrition Report")
                st.markdown(response.text)
                
                # 4. Export Options (PDF and JSON)
                st.divider()
                col_pdf, col_json = st.columns(2)
                
                with col_pdf:
                    pdf_data = create_pdf(response.text)
                    st.download_button("📥 Download PDF Report", data=pdf_data, file_name="Health_Plan.pdf", use_container_width=True)
                
                with col_json:
                    # Create structured JSON data for the mentor's requirement
                    report_json = {
                        "patient_biometrics": {"weight": weight, "height": height, "age": age, "gender": gender},
                        "plan_details": {"goal": goal, "duration": duration, "target_calories": target_cal},
                        "ai_recommendation": response.text[:1000] # Snippet for JSON
                    }
                    json_string = json.dumps(report_json, indent=4)
                    st.download_button("📥 Download JSON Data", data=json_string, file_name="health_data.json", mime="application/json", use_container_width=True)

        except Exception as e:
            st.error(f"AI Error: {e}")
