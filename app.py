import streamlit as st
import google.generativeai as genai
import time
from fpdf import FPDF

st.set_page_config(page_title="NutriCare Hub")

# Clean PDF function - fixed encoding for latin-1
def create_pdf(text):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, txt=clean_text)
        return pdf.output(dest="S").encode("latin-1")
    except:
        return None

# AI Setup - Using latest stable model string to avoid 404
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except:
    st.error("Check your Streamlit Secrets for the API Key.")

st.title("🥗 AI-NutriCare Hub")

weight = st.number_input("Weight (kg)", 30, 150, 70)
goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])

if st.button("🚀 Generate Plan", use_container_width=True):
    with st.spinner("🏥 Consulting AI..."):
        try:
            prompt = f"Dietitian: Create a {goal} plan for a {weight}kg user."
            res = model.generate_content(prompt)
            
            st.markdown(res.text)
            
            # Download Button appears right after text
            pdf_bytes = create_pdf(res.text)
            if pdf_bytes:
                st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name="plan.pdf", mime="application/pdf")
        
        except Exception as e:
            if "ResourceExhausted" in str(e):
                st.warning("Limit Reached! Wait 60s.")
            else:
                st.error(f"Error: {e}")
