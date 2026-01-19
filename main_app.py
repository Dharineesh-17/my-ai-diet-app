import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
# Add this at the very top of your code after imports
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1E1E1E;
        font-weight: 700;
        font-size: 32px;
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

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
