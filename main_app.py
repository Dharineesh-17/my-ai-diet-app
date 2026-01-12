import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- 1. APP CONFIG (Must be at the very top) ---
st.set_page_config(page_title="AI Health Hub", page_icon="🥗", layout="wide")

# --- 2. PDF HELPER FUNCTION ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Clean text for PDF safety
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

# --- 3. AI CONFIGURATION ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 4. WEB INTERFACE UI ---
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

    # Hydration Tracker
    st.divider()
    st.header("💧 Hydration Tracker")
    water_goal = st.number_input("Daily Goal (L)", 1.0, 5.0, 2.5)
    current_water = st.slider("Water Consumed", 0.0, water_goal, 0.0, step=0.25)
    st.progress(current_water / water_goal)

with col2:
    if generate_btn:
        # Step 1: Calculate and Generate
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        with st.spinner("AI is crafting your plan..."):
            prompt = f"Create a {duration}-day {goal} plan for {calories:.0f} calories."
            response = model.generate_content(prompt)
            st.markdown("### 📝 Your Personalized Meal Plan")
            st.markdown(response.text)
            
            # Step 2: PDF Download (This waits for the response!)
            pdf_data = create_pdf(response.text)
            st.download_button(
                label="📥 Download Plan as PDF",
                data=pdf_data,
                file_name="diet_plan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Step 3: Shopping List
            st.divider()
            with st.expander("🛒 Smart Shopping List"):
                shop_prompt = f"List 10 items for a {goal} diet."
                shop_res = model.generate_content(shop_prompt)
                st.markdown(shop_res.text)
    else:
        st.info("Enter stats and click 'Generate'!")

with col2:
    with st.expander("💡 Pro Health Tips"):
        st.write("🏃 Cardio | 😴 Sleep | 🧂 Sodium")
