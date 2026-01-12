import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="AI Health Hub", page_icon="🥗", layout="wide")

# Securely connect to Gemini using your Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. PDF HELPER FUNCTION ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Clean text to prevent PDF encoding errors
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest="S").encode("latin-1")

# --- 3. THE UI LAYOUT ---
st.title("🥗 Personal AI Diet & Health Hub")

col1, col2 = st.columns([1, 2])

# --- LEFT COLUMN: INPUTS & TRACKERS ---
with col1:
    st.header("📋 Your Stats")
    with st.container(border=True):
        weight = st.number_input("Weight (kg)", 30, 150, 70)
        height = st.number_input("Height (cm)", 100, 230, 175)
        age = st.number_input("Age", 10, 100, 25)
        duration = st.slider("Plan Duration (Days)", 1, 7, 3)
        goal = st.selectbox("Your Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
        generate_btn = st.button("Generate My Plan", use_container_width=True)
    
    st.divider()
    st.header("💧 Hydration Tracker")
    water_goal = st.number_input("Daily Goal (Liters)", 1.0, 5.0, 2.5)
    current_water = st.slider("Water Consumed Today", 0.0, water_goal, 0.0, step=0.25)
    
    progress = current_water / water_goal
    st.progress(progress)
    if progress >= 1.0:
        st.balloons()
        st.success("Goal Reached!")

# --- RIGHT COLUMN: AI RESULTS ---
with col2:
    if generate_btn:
        # Calculate Calories (Mifflin-St Jeor Equation)
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        
        with st.spinner("AI is crafting your plan..."):
            # A. Generate Main Diet Plan
            prompt = f"Create a {duration}-day {goal} plan for {calories:.0f} calories. List specific meals for breakfast, lunch, and dinner."
            response = model.generate_content(prompt)
            st.markdown("### 📝 Your Personalized Meal Plan")
            st.markdown(response.text)
            
            # B. PDF Download Button (Indented inside the button logic!)
            pdf_data = create_pdf(response.text)
            st.download_button(
                label="📥 Download Plan as PDF",
                data=pdf_data,
                file_name="my_ai_diet_plan.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            # C. Smart Shopping List (Indented!)
            st.divider()
            with st.expander("🛒 View Your Smart Shopping List"):
                st.write("Based on your plan, you'll need these essentials:")
                shop_prompt = f"List 10 essential grocery items for a {goal} diet."
                shop_response = model.generate_content(shop_prompt)
                st.markdown(shop_response.text)

            # D. Auto-Generating Meal Inspiration
            st.divider()
            st.subheader("📸 Your Daily Meal Inspiration")
            search_term = goal.replace(" ", "")
            st.image(f"https://loremflickr.com/800/600/healthy,food,{search_term}", 
                     caption=f"AI-Selected {goal} Inspiration",
                     use_container_width=True)
    else:
        st.info("Enter your stats on the left and click 'Generate My Plan' to begin!")
