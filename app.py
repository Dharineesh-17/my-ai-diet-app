import streamlit as st
import json
from groq import Groq
import PyPDF2
from PIL import Image
import pytesseract  # You will need to install 'pytesseract' and the Tesseract OCR engine

# --- 1. PREMIUM UI ENGINE ---
st.set_page_config(page_title="AI Base Diet Plan Generator", layout="wide")
# Add this to your existing CSS block

st.markdown("""

    <style>

    /* Force Results Area to be High Contrast */

    .stTabs [data-baseweb="tab-panel"] {

        background-color: #ffffff !important;

        color: #000000 !important;

        border-radius: 0 0 30px 30px !important;

        padding: 25px !important;

        border: 1px solid #e0e0e0 !important;

    }

    

    /* Ensure Markdown text inside tabs is pure black */

    .stTabs [data-baseweb="tab-panel"] div, 

    .stTabs [data-baseweb="tab-panel"] p, 

    .stTabs [data-baseweb="tab-panel"] li {

        color: #1a1a1a !important;

        font-weight: 500 !important;

    }



    /* Tab Headers visibility */

    button[data-baseweb="tab"] {

        background-color: #f8fafc !important;

        border-radius: 10px 10px 0 0 !important;

        margin-right: 5px !important;

    }

    

    button[data-baseweb="tab"] p {

        color: #000000 !important;

    }

    </style>

    """, unsafe_allow_html=True)

# --- 2. MULTI-FILE EXTRACTION LOGIC ---
def extract_text_from_file(uploaded_file):
    """Handles PDF, PNG, JPG, and JPEG"""
    if uploaded_file.type == "application/pdf":
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            return "".join([p.extract_text() for p in reader.pages])
        except: return "PDF extraction failed."
    else:
        # Handle Screenshots/Images via OCR
        try:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)
            return text if text.strip() else "No readable text found in image."
        except Exception as e:
            return f"Image OCR failed: {e}"

if 'res_text' not in st.session_state: st.session_state.res_text = ""

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=60)
    st.markdown("### 🧬 Clinical Ingestion")
    # UPDATED: Added image formats
    uploaded_file = st.file_uploader("Upload Lab Report or Screenshot", type=["pdf", "png", "jpg", "jpeg"])
    st.divider()
    model_choice = st.selectbox("LLM Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

# --- 4. DASHBOARD WORKSPACE ---
st.title("🥗 AI Based Diet plan Generator")

with st.container():
    v1, v2, v3, v4 = st.columns(4)
    with v1: weight = st.number_input("Weight (kg)", 30.0, 150.0, 70.0)
    with v2: height = st.number_input("Height (cm)", 100.0, 230.0, 175.0)
    with v3: age = st.number_input("Age", 10, 100, 25)
    with v4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "Healthy" if 18.5 <= bmi <= 25 else "Attention Required")

    p1, p2 = st.columns([2, 1])
    with p1: culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto", "Mediterranean"], default=["South Indian"])
    with p2: goal = st.select_slider("Clinical Goal", options=["Loss", "Maintain", "Muscle"])

    if st.button("🚀 GENERATE CLINICAL AUDIT"):
        with st.status("🔍 Analyzing Biomarkers...") as status:
            # New extraction engine
            report_data = extract_text_from_file(uploaded_file) if uploaded_file else "None"
            
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Dietitian: Analyze this data: {report_data}. Create {goal} plan for {age}y, {weight}kg ({culture})."
                chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
                st.session_state.res_text = chat.choices[0].message.content
                status.update(label="✅ Analysis Complete!", state="complete")
            except Exception as e:
                st.error(f"Inference Error: {e}")

# --- 5. OUTPUT EXPERIENCE ---
if st.session_state.res_text:
    st.divider()
    st.markdown("### 📋 AI Nutrition Prescription")
    t1, t2 = st.tabs(["🍏 Meal Plan", "📈 Health Insights"])
    with t1: st.markdown(st.session_state.res_text)
    with t2: st.info("💡 Clinical Tip: Ensure 3.5L water intake to support metabolism.")
    st.download_button("📥 Download Plan", st.session_state.res_text, file_name="Diet_Plan.txt")
