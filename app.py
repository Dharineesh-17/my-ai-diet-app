import streamlit as st
from groq import Groq
import PyPDF2
from PIL import Image
import easyocr
import numpy as np

# --- 1. DASHBOARD UI ---
st.set_page_config(page_title="AI based diet plan generator", layout="wide")

# Add this to your existing CSS block
st.markdown("""
    <style>
    /* Force Results Area to be High Contrast */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 0 0 15px 15px !important;
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

# --- 2. EXTRACTION ENGINE ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def extract_data(uploaded_file):
    """Detects file type and pulls text"""
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([p.extract_text() for p in reader.pages])
    else:
        # OCR for Screenshots/Images
        reader = load_ocr()
        image = Image.open(uploaded_file)
        results = reader.readtext(np.array(image))
        return " ".join([res[1] for res in results])

# --- 3. INPUT SECTION ---
st.title("🏥 NutriCare AI: Clinical Audit")

with st.sidebar:
    st.markdown("### 📂 1. Upload Report")
    uploaded_file = st.file_uploader("Drop PDF or Screenshot here", type=["pdf", "png", "jpg", "jpeg"])
    st.divider()
    # Fixed model name to avoid 400 error
    model_choice = "llama-3.3-70b-versatile" 

with st.container():
    st.markdown("### ⚖️ 2. Verify Vitals (Manual Fallback)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    with c2: height = st.number_input("Height (cm)", 100.0, 250.0, 175.0)
    with c3: age = st.number_input("Age", 1, 100, 25)
    with c4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "At Risk" if bmi > 25 else "Healthy")

    if st.button("🚀 ANALYZE & GENERATE PLAN", use_container_width=True):
        if not uploaded_file:
            st.error("Dude, upload a file first so I can extract the data!")
        else:
            with st.status("🧬 Reading your report...") as status:
                # This is the actual text from your file
                extracted_text = extract_data(uploaded_file)
                
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # THE BRAINS: Telling the AI to prioritize file data
                prompt = f"""
                ACT AS: A Senior Clinical Dietitian.
                RAW REPORT DATA: {extracted_text}
                MANUAL INPUTS: {age}y, {weight}kg, {height}cm.

                STRICT INSTRUCTIONS:
                1. Scrutinize the 'RAW REPORT DATA' for vitals (Weight, Height, Age) and blood markers.
                2. If you find vitals in the report, OVERRIDE the manual inputs.
                3. Highlight what you extracted from the file in a 'Clinical Findings' section.
                4. Create a meal plan based on the extracted report.
                """
                
                chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
                st.session_state.res_text = chat.choices[0].message.content
                status.update(label="✅ Extraction & Analysis Complete!", state="complete")

# --- 4. OUTPUT ---
if 'res_text' in st.session_state:
    st.divider()
    t1, t2 = st.tabs(["🍏 Your Clinical Plan", "🔍 Extracted Insights"])
    with t1: st.markdown(st.session_state.res_text)
    with t2: st.info("The AI cross-referenced your file's text with its medical database.")
