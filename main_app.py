import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import streamlit as st

# 1. PREMIUM CSS (The "White Mode" Look)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Make Title and Subtitles visible */
    h1, h2, h3, .main-header {
        color: #1E1E1E !important; /* Force deep dark color */
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Sidebar text color fix */
    [data-testid="stSidebar"] section {
        color: #333333 !important;
    }

    /* Style for the main title class we created */
    .main-header {
        font-weight: 700;
        font-size: 40px;
        padding-top: 10px;
        padding-bottom: 5px;
    }
    
    /* Style for normal text to ensure it's not white */
    .stMarkdown p {
        color: #444444;
    }
    </style>
    """, unsafe_allow_html=True)
# 2. HEADER
st.markdown('<div class="main-header">🥗 AI Nutrition & Health Hub</div>', unsafe_allow_html=True)
st.write("Optimize your health with AI-driven insights.")

# 3. SIDEBAR INPUTS
with st.sidebar:
    st.header("👤 Your Stats")
    weight = st.number_input("Weight (kg)", value=70)
    height = st.number_input("Height (cm)", value=175)
    age = st.number_input("Age", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    goal = st.selectbox("Your Goal", ["Weight Loss", "Maintain", "Muscle Gain"])
    generate_btn = st.button("Generate My Plan")

# 4. CALCULATION & DASHBOARD (Fixes the NameError)
# We calculate BMR immediately so the variable 'bmr' exists for the metrics below
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

# DISPLAY METRICS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Basal Metabolic Rate", value=f"{int(bmr)} kcal", delta="Daily Base")
with col2:
    target = bmr + 500 if goal == "Muscle Gain" else bmr - 500 if goal == "Weight Loss" else bmr
    st.metric(label="Target Intake", value=f"{int(target)} kcal", delta=goal)
with col3:
    st.metric(label="Water Goal", value="3.5 L", delta="Hydration")

# 5. AI REPORT SECTION
if generate_btn:
    with st.spinner("AI is crafting your plan..."):
        # Placeholder for your Gemini API call
        st.success("Plan Generated!")
        with st.container(border=True):
            st.subheader("📋 Personalized Nutrition Report")
            st.write("Your AI-generated meal plan would appear here...")

# --- 1. APP CONFIG ---
st.set_page_config(page_title="AI Health Hub", page_icon="🥗", layout="wide")

# --- 2. PDF HELPER ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

# --- 3. AI CONFIGURATION (Using Secrets) ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("API Key missing! Please add it to Streamlit Secrets.")

# --- 4. UI LAYOUT ---
st.title("🥗 Personal AI Diet & Health Hub")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📋 Your Stats")
    with st.container(border=True):
        weight = st.number_input("Weight (kg)", 30, 150, 70)
        height = st.number_input("Height (cm)", 100, 230, 175)
        age = st.number_input("Age", 10, 100, 25)
        duration = st.slider("Plan Duration (Days)", 1, 7, 3)
        goal = st.selectbox("Your Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
        generate_btn = st.button("Generate My Plan", use_container_width=True)

with col2:
    if generate_btn:
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        with st.spinner("AI is crafting your plan..."):
            try:
                prompt = f"Create a {duration}-day {goal} plan for {calories:.0f} calories."
                response = model.generate_content(prompt)
                st.markdown("### 📝 Your Personalized Meal Plan")
                st.markdown(response.text)
                
                st.divider()
                pdf_data = create_pdf(response.text)
                st.download_button(label="📥 Download Plan", data=pdf_data, file_name="plan.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Enter stats and click 'Generate'!")
