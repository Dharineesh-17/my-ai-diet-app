import streamlit as st
import google.generativeai as genai
import time
from fpdf import FPDF

# --- 1. THEME & VISIBILITY ---
st.set_page_config(page_title="AI-NutriCare Hub", layout="wide")

st.markdown("""
    <style>
    /* Force high-contrast black for readability */
    h1, h2, h3, p, label, .stMetricValue, .stMarkdown {
        color: #000000 !important;
    }
    .stApp { background-color: #f8f9fa !important; }
    /* Dark sidebar with white text */
    [data-testid="stSidebar"] { background-color: #1a1c23 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE PDF GENERATOR (STABLE VERSION) ---
def generate_pdf_report(content):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Clean special characters that cause crashes
        clean_text = content.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, txt=clean_text)
        return pdf.output(dest="S").encode("latin-1")
    except Exception as e:
        st.error(f"PDF logic error: {e}")
        return None

# --- 3. AI CONFIGURATION ---
try:
    # Use the specific secret key you added to Streamlit
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # CRITICAL: Using 'gemini-1.5-flash' - the most stable free-tier model
    # Avoids the 404 errors from using non-existent 3.0 or experimental versions
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ API Key Error: Check your Streamlit Secrets for 'GOOGLE_API_KEY'.")

# --- 4. APP INTERFACE ---
st.markdown('# 🥗 AI-NutriCare Hub')
st.caption("Powered by Gemini 1.5 Flash (Optimized for Stability)")

with st.sidebar:
    st.header("👤 Account")
    st.success("Dharineesh Logged In")
    st.divider()
    st.header("📄 Medical Report")
    uploaded_file = st.file_uploader("Upload Report (PDF/JPG)", type=["pdf", "jpg", "jpeg", "png"])

# --- 5. BIOMETRICS SECTION ---
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        weight = st.number_input("Weight (kg)", 30, 200, 70)
        gender = st.selectbox("Gender", ["Male", "Female"])
    with c2:
        height = st.number_input("Height (cm)", 100, 250, 170)
        goal = st.selectbox("Your Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
    with c3:
        age = st.number_input("Age", 5, 100, 25)
        cuisine = st.text_input("Local Cuisine", "South Indian")

# --- 6. CORE LOGIC & LIMIT HANDLING ---
if st.button("🚀 Analyze & Generate AI-NutriCare Plan", use_container_width=True):
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("No API Key found. Add it to Advanced Settings.")
    else:
        with st.spinner("🏥 Consultng AI Dietitian..."):
            try:
                # Structured prompt for consistent output
                prompt = f"Dietitian mode: Generate a {goal} diet for a {age}yr {gender}, {weight}kg, {height}cm. Cuisine: {cuisine}. Use local staples."
                
                if uploaded_file:
                    file_data = uploaded_file.getvalue()
                    response = model.generate_content([prompt, {"mime_type": uploaded_file.type, "data": file_data}])
                else:
                    response = model.generate_content(prompt)

                # Display Results
                st.subheader("📋 Your Clinical Nutrition Plan")
                st.markdown(response.text)
                
                # Export Button
                pdf_data = generate_pdf_report(response.text)
                if pdf_data:
                    st.download_button("📥 Download PDF Report", data=pdf_data, file_name="Diet_Plan.pdf", mime="application/pdf")

            except Exception as e:
                # This catches the 429 "Resource Exhausted" error specifically
                if "429" in str(e) or "limit" in str(e).lower():
                    st.warning("⚠️ GOOGLE LIMIT REACHED. Start 48s Cooldown.")
                    
                    # LIVE COUNTDOWN TIMER
                    timer_placeholder = st.empty()
                    for i in range(48, 0, -1):
                        timer_placeholder.metric("⏳ Waiting for API Reset...", f"{i} seconds")
                        time.sleep(1)
                    timer_placeholder.success("✅ Ready! Please click the button again.")
                else:
                    st.error(f"System Error: {e}")
