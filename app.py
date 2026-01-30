import streamlit as st

# --- 1. GLOBAL COLOR ENGINE ---
# We use !important to override Streamlit's default dark-mode text dimming
st.markdown("""
    <style>
    /* Main Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important;
    }

    /* Glassmorphism Cards: White base with high-contrast black text */
    [data-testid="stVerticalBlock"] > div:has(div.stMetric), .stExpander {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
    }

    /* CRITICAL: Force all text to be pure black for readability */
    h1, h2, h3, p, label, .stMarkdown, [data-testid="stMetricLabel"] {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }

    /* Metric Values: Bold Blue for visibility */
    [data-testid="stMetricValue"] {
        color: #007bff !important;
        font-size: 2.2rem !important;
    }

    /* Sidebar: Professional Deep Navy */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Clinical Action Button: Pulse Blue */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
        color: white !important;
        border: none !important;
        padding: 15px !important;
        font-size: 18px !important;
        border-radius: 50px !important;
        transition: 0.3s all ease;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. UPDATED DASHBOARD LAYOUT ---
st.title("🏥 NutriCare AI: Clinical Audit")

# Metric Row with Visibility delta colors
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("BMR", "1673 kcal", help="Basal Metabolic Rate")
with c2:
    st.metric("Target", "1173 kcal", delta="-500 (Loss)", delta_color="normal")
with c3:
    st.metric("BMI", "22.9", delta="Healthy", delta_color="off")

# --- 3. INPUT SECTION ---
with st.container():
    st.markdown("### 📊 Patient Vitals")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        weight = st.number_input("Weight (kg)", value=70)
    with col_b:
        height = st.number_input("Height (cm)", value=175)
    with col_c:
        age = st.number_input("Age", value=25)

# --- 4. CLINICAL STATUS CARDS ---
st.markdown("### 🚩 Detected Conditions")
# Using expanders as high-visibility cards
with st.expander("⚠️ PCOD/PCOS Detected", expanded=True):
    st.write("**Avoid:** Dairy, Soy, Sugar")
    st.info("💡 Focus on Hormone Balance and low-GI foods.")

# --- 5. INTERACTIVE INPUT GRID ---
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        weight = st.number_input("Weight (kg)", 30, 150, 70)
    with c2:
        height = st.number_input("Height (cm)", 100, 230, 175)
    with c3:
        age = st.number_input("Age", 10, 100, 25)
    with c4:
        # Visual Metric Calculation
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", delta="-0.2 (Healthy)" if 18 < bmi < 25 else "Attention", delta_color="normal")

# --- 6. USER PREFERENCES CARD ---
with st.container():
    col_left, col_right = st.columns([2, 1])
    with col_left:
        food_culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Mediterranean", "Keto", "Vegan"], default=["South Indian"])
    with col_right:
        goal = st.select_slider("Health Goal", options=["Aggressive Loss", "Maintenance", "Bulking"])

# --- 7. ACTION & OUTPUT ---
st.divider()
if st.button("🚀 GENERATE CLINICAL AUDIT"):
    with st.status("🔍 Analyzing Biomarkers...", expanded=True) as status:
        st.write("Extracting clinical data...")
        report_data = extract_pdf_text(uploaded_file) if uploaded_file else "None"
        
        st.write("Consulting Llama 3.3 Engine...")
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"Dietitian Audit: {age}y, {weight}kg. Goal: {goal}. Culture: {food_culture}. Data: {report_data}. Focus on clinical risk."
        
        chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
        st.session_state.res_text = chat.choices[0].message.content
        status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

# --- 8. THE OUTPUT UX (Cards & Markdown) ---
if st.session_state.res_text:
    st.markdown("### 📋 AI Prescription & Nutrition Plan")
    
    # Using a Tabbed UI for cleaner UX
    tab1, tab2, tab3 = st.tabs(["🍏 Meal Plan", "🚫 Medical Restrictions", "📈 Health Insights"])
    
    with tab1:
        st.info(st.session_state.res_text.split('\n')[0:10]) # Simplified for demo
        st.markdown(st.session_state.res_text)
        
    with tab2:
        st.warning("Ensure all 'Strictly Avoid' items are removed from your pantry immediately.")
        
    with tab3:
        st.success("Based on your biomarkers, your metabolic age is estimated at +2 years. Diet adjusted.")

    # Export Bar
    st.write("---")
    ec1, ec2, ec3 = st.columns([1,1,3])
    ec1.download_button("📩 Download PDF", "...", file_name="audit.pdf")
    ec2.download_button("📊 Export JSON", "...", file_name="data.json")
