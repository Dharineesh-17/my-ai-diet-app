import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- 1. APP CONFIG ---
st.set_page_config(page_title="AI Health Hub", page_icon="🥗", layout="wide")

# Connect to Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. PDF HELPER ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Clean text for PDF safety
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

# --- 3. UI LAYOUT ---
st.title("🥗 Personal AI Diet & Health Hub")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📋 Your Stats")
    with st.container(border=True):
        weight = st.number_input("Weight (kg)", 30, 150, 70)
        height = st.number_input("Height (cm)", 100, 230, 175)
        age = st.number_input("Age", 10, 100, 25)
        goal = st.selectbox("Your Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
        generate_btn = st.button("Generate My Plan", use_container_width=True)

with col2:
    if generate_btn:
        # This code ONLY runs AFTER you click the button
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        
        with st.spinner("AI is crafting your plan..."):
            # A. Generate Plan
            prompt = f"Create a meal plan for a {goal} goal with {calories:.0f} calories."
            response = model.generate_content(prompt)
            plan_text = response.text
            st.markdown("### 📝 Your Plan")
            st.write(plan_text)
            
            # B. PDF Download (Indented so it waits for the plan!)
            st.divider()
            pdf_data = create_pdf(plan_text)
            st.download_button(
                label="📥 Download Plan as PDF",
                data=pdf_data,
                file_name="my_plan.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Fill in your stats and click 'Generate' to see your plan and download the PDF.")
