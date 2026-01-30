import streamlit as st
import json
import time
import PyPDF2 # Required for clinical report extraction
from fpdf import FPDF
from groq import Groq 

# --- 1. SETUP & STATE INITIALIZATION ---
st.set_page_config(page_title="AI-NutriCare Hub", layout="wide")

# Initialize medical values to prevent NameError
if 'res_text' not in st.session_state: st.session_state.res_text = ""

# --- 2. SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Model Settings")
    # Updated to active 2026 models
    selected_model_name = st.selectbox("Select Llama Model", 
                                     ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile'])
    
    st.divider()
    st.markdown("### 📄 Clinical Analysis")
    uploaded_file = st.file_uploader("Upload Report", type=["pdf"])

# --- 3. CORE AI SETUP ---
try:
    # Set your key in Streamlit Secrets as "GROQ_API_KEY"
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API Key missing! Add GROQ_API_KEY to Secrets.")

# --- 4. BIOMETRICS ---
st.markdown("### 📊 Biometrics")
with st.container(border=True):
    col_a, col_b = st.columns(2)
    with col_a:
        weight = st.number_input("Weight (kg)", 30, 150, 70)
        goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain"])
    with col_b:
        age = st.number_input("Age", 10, 100, 25)
        food_culture = st.text_input("Local Cuisine", "South Indian")

# --- 5. CLINICAL GENERATION ---
# Fix: Define 'submit' clearly
submit = st.button("🚀 Analyze & Generate AI Plan", use_container_width=True)

if submit:
    with st.spinner(f"🏥 Consulting {selected_model_name}..."):
        try:
            file_context = ""
            if uploaded_file:
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages: 
                    file_context += page.extract_text()
            
            prompt = f"Dietitian: Create a {goal} plan for {age}y, {weight}kg. Cuisine: {food_culture}. Context: {file_context}"
            
            # Use Llama 3.1 via Groq
            completion = client.chat.completions.create(
                model=selected_model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.res_text = completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error: {e}")

# --- 6. DISPLAY RESULTS ---
if st.session_state.res_text:
    with st.container(border=True):
        st.markdown("### 📋 Nutrition Report")
        st.markdown(st.session_state.res_text)
        
        # Download logic here...

# --- 8. CLINICAL GENERATION ---
if st.button("🚀 Analyze & Generate AI-NutriCare Plan", use_container_width=True):
    with st.spinner(f"🏥 Consulting {selected_model_name}..."):
        try:
            # Handle File Text Extraction if present
            file_context = ""
            if uploaded_file:
                import PyPDF2
                if uploaded_file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages: file_context += page.extract_text()
            
            prompt = f"Clinical Dietitian: Create a {goal} plan for {age}y {gender}, {weight}kg. Cuisine: {food_culture}. Duration: {duration} days. Context from report: {file_context}"
            
            # Groq API Call
            completion = client.chat.completions.create(
                model=selected_model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048
            )
            
            res_text = completion.choices[0].message.content

            with st.container(border=True):
                st.markdown("### 📋 Nutrition Report")
                st.markdown(res_text)
                
                st.divider()
                st.subheader("📥 Export")
                c1, c2, _ = st.columns(3)
                with c1:
                    pdf_data = create_pdf(res_text)
                    if pdf_data:
                        st.download_button("💾 PDF", data=pdf_data, file_name="report.pdf", use_container_width=True)
                with c2:
                    st.download_button("📄 JSON", data=json.dumps({"analysis": res_text[:500]}), file_name="report.json", use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
