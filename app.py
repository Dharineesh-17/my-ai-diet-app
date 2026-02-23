import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. PREMIUM UI & STATE ENGINE ---
st.set_page_config(page_title="AI Based Diet Plan Generator", layout="wide")

# Persistent memory for cross-tab communication
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': "", 'messages': []}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. EXTRACTION ENGINE ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def sync_dashboard_from_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = " ".join([p.extract_text() for p in reader.pages])
    else:
        reader = load_ocr()
        text = " ".join([res[1] for res in reader.readtext(np.array(Image.open(file)))])
    
    st.session_state.raw_text = text
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sync_prompt = f"Extract weight(kg), height(cm), age from text: '{text}'. Return ONLY JSON: {{\"w\":num, \"h\":num, \"a\":num}}"
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": sync_prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        vitals = json.loads(resp.choices[0].message.content)
        st.session_state.w = max(30.0, min(200.0, float(vitals.get('w', st.session_state.w))))
        st.session_state.h = max(100.0, min(250.0, float(vitals.get('h', st.session_state.h))))
        st.session_state.a = max(1, min(120, int(vitals.get('a', st.session_state.a))))
    except Exception as e:
        st.warning(f"Extraction Note: {e}")

# --- 3. SIDEBAR (Global Settings) ---
with st.sidebar:
    st.title("📂 Control Center")
    uploaded_file = st.file_uploader("Upload Lab Report", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file and st.button("🔍 Sync Clinical Data"):
        with st.status("🧬 Analyzing Data...") as s:
            sync_dashboard_from_file(uploaded_file)
            s.update(label="✅ Data Synced!", state="complete")
    
    st.divider()
    model_choice = st.selectbox("LLM Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if st.button("🗑️ Reset All Sessions"):
        st.session_state.messages = []
        st.session_state.res_text = ""
        st.rerun()

# --- 4. NAVIGATION SEPARATION ---
st.title("🥗 AI Clinical Intelligence System")
tab1, tab2 = st.tabs(["📊 Patient Dashboard & Report", "💬 Clinical AI Chatbot"])

# --- TAB 1: DATA & GENERATION ---
with tab1:
    st.markdown("### 🩺 Verify Patient Vitals")
    v1, v2, v3, v4 = st.columns(4)
    weight = v1.number_input("Weight (kg)", 30.0, 200.0, key="w")
    height = v2.number_input("Height (cm)", 100.0, 250.0, key="h")
    age = v3.number_input("Age", 1, 120, key="a")
    with v4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "Healthy" if 18.5 <= bmi <= 25 else "Attention Required")

    c1, c2 = st.columns(2)
    with c1: culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto", "Mediterranean"], default=["South Indian"])
    with c2: goal = st.select_slider("Clinical Goal", options=["Loss", "Maintain", "Muscle"])

    if st.button("🚀 GENERATE NUTRITION REPORT", use_container_width=True):
        if not st.session_state.raw_text and not uploaded_file:
            st.error("Please upload a report first.")
        else:
            with st.spinner("Analyzing Clinical Markers..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Dietitian: Analyze this lab data: {st.session_state.raw_text}. Create {goal} plan for {age}y, {weight}kg ({culture})."
                chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
                st.session_state.res_text = chat.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": f"**System:** Initial Plan Generated."})
                st.success("Report Generated! Move to the Chatbot tab for discussion.")

    if st.session_state.res_text:
        st.markdown("---")
        st.markdown("### 📋 Generated Nutrition Prescription")
        st.info(st.session_state.res_text)
        
        # --- NEW: DOWNLOAD OPTION ---
        st.download_button(
            label="📥 Download Clinical Diet Plan",
            data=st.session_state.res_text,
            file_name=f"Diet_Plan_{age}y_{goal}.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- TAB 2: CHATBOT ---
with tab2:
    if not st.session_state.res_text:
        st.info("⚠️ Please generate a report in the first tab to start the consultation.")
    else:
        st.markdown("### 💬 Clinical Consultation")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if user_input := st.chat_input("Ask about swaps, allergies, or clinical values..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                system_context = f"""
                You are a Clinical Nutritionist. Base answers strictly on this report: {st.session_state.res_text}.
                Patient: {age}y, {weight}kg, Goal: {goal}. Ensure medical safety.
                """
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_context}, *st.session_state.messages],
                    model=model_choice,
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
