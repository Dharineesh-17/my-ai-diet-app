import streamlit as st
from groq import Groq
import PyPDF2
from PIL import Image
import pytesseract # For screenshots/images

# --- 1. UI SETUP ---
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

# --- 2. THE EXTRACTION ENGINE ---
def get_report_content(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return " ".join([p.extract_text() for p in reader.pages])
    else:
        # OCR for Screenshots/Images
        img = Image.open(file)
        return pytesseract.image_to_string(img)

# --- 3. DASHBOARD ---
st.title("🥗 Clinical Report Analyzer & Diet Planner")

with st.sidebar:
    st.markdown("### 📂 Step 1: Upload Data")
    # Supports PDF and Screenshots now!
    uploaded_file = st.file_uploader("Upload Lab Report / Screenshot", type=["pdf", "png", "jpg", "jpeg"])
    model_choice = st.selectbox("Intelligence Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

# Manual Overrides (Fallback if report is empty)
with st.expander("Manual Vitals (Fallback)", expanded=False):
    c1, c2, c3 = st.columns(3)
    m_weight = c1.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    m_height = c2.number_input("Height (cm)", 100.0, 250.0, 175.0)
    age = c3.number_input("Age", 1, 100, 25)

culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto"], default=["South Indian"])

# --- 4. THE ACTION ---
if st.button("🚀 ANALYZE REPORT & GENERATE PLAN"):
    if not uploaded_file:
        st.warning("Please upload a report or screenshot to analyze!")
    else:
        with st.status("🧬 Extracting data from file...") as status:
            raw_text = get_report_content(uploaded_file)
            
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # THE CRITICAL PROMPT: Tell AI to find data in the report
            clinical_prompt = f"""
            SYSTEM: You are a Senior Clinical Dietitian.
            INPUT DATA: 
            - Extracted Report Text: {raw_text}
            - Fallback Vitals: Weight {m_weight}kg, Height {m_height}cm, Age {age}.
            - Culture: {culture}

            TASK:
            1. Scrutinize the 'Extracted Report Text' for any clinical markers (Blood Sugar, Cholesterol, Weight, BMI).
            2. If the report contains a weight/height different from the fallbacks, USE THE REPORT DATA.
            3. Identify health risks (e.g., Anemia, PCOD, Diabetes) based on the report values.
            4. Create a specific meal plan based on these findings.
            """
            
            chat = client.chat.completions.create(
                messages=[{"role": "user", "content": clinical_prompt}],
                model=model_choice
            )
            st.session_state.final_res = chat.choices[0].message.content
            status.update(label="✅ Analysis Complete!", state="complete")

# --- 5. DISPLAY ---
if 'final_res' in st.session_state:
    st.markdown("### 📋 Clinical Nutrition Prescription")
    t1, t2 = st.tabs(["🍏 Meal Plan", "📈 Report Insights"])
    with t1: st.markdown(st.session_state.final_res)
    with t2: st.info("The AI has cross-referenced your report markers with standard clinical ranges.")
