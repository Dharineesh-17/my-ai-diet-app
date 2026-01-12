import streamlit as st
from fpdf import FPDF
import base64
st.set_page_config(
    page_title="AI Health Hub",
    page_icon="🥗", # You can use an emoji or a URL to a custom logo!
    layout="wide"
)
# --- NEW FUNCTION FOR DAY 4 ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # This cleans the AI text so it doesn't break the PDF
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

# ... (Keep your existing AI logic here) ...
import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- 1. PDF HELPER FUNCTION ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")
# Add this inside your 'with col1:' block
st.divider()
st.header("💧 Hydration Tracker")
water_goal = st.number_input("Daily Goal (Liters)", 1.0, 5.0, 2.5)
current_water = st.slider("Water Consumed today", 0.0, water_goal, 0.0, step=0.25)

progress = current_water / water_goal
st.progress(progress)
if progress >= 1.0:
    st.balloons() # Little celebration when you hit your goal!
    st.success("Goal Reached!")

# --- 2. AI CONFIGURATION ---
genai.configure(api_key="AIzaSyAsIfH8g0EmsktC77K2a4vT-1dGoqdPFtI")
model = genai.GenerativeModel('gemini-3-flash-preview')
# Add this at the very bottom of your 'with col2:' block
with st.expander("💡 Pro Health Tips"):
    st.write("🏃 **Cardio:** Aim for 30 mins of zone 2 cardio today.")
    st.write("😴 **Sleep:** 7-9 hours is just as important as your diet.")
    st.write("🧂 **Sodium:** Keep it under 2300mg to avoid bloating.")
# --- 3. WEB INTERFACE UI ---
st.set_page_config(page_title="AI Health Hub", layout="wide")
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
        # Math for Calories
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        
        with st.spinner("AI is crafting your plan..."):
            prompt = f"Create a {duration}-day {goal} plan for {calories:.0f} calories."
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
            # --- THE DOWNLOAD BUTTON (Must be indented here!) ---
            pdf_data = create_pdf(response.text)
            st.download_button(
                label="📥 Download Plan as PDF",
                data=pdf_data,
                file_name="my_ai_diet_plan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Enter your stats and click Generate!")

# Inside 'if generate_btn:', after showing the plan:
# ... (Top part of your code) ...
if generate_btn:
    # STEP 1: AI generates the plan
    with st.spinner("AI is thinking..."):
        prompt = f"Create a {duration}-day plan..."
        response = model.generate_content(prompt) # 'response' is created HERE
        st.markdown(response.text)

    # STEP 2: The PDF lines MUST be at the same level as st.markdown
    # They MUST be indented (pushed right) under the 'if generate_btn:'
    pdf_data = create_pdf(response.text) 
    st.download_button(
        label="📥 Download Plan as PDF",
        data=pdf_data,
        file_name="my_diet_plan.pdf",
        mime="application/pdf"
    )
