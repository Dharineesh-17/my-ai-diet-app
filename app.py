import streamlit as st
import json
import numpy as np
import easyocr
import PyPDF2
from groq import Groq
from PIL import Image

# --- 1. PREMIUM UI & STATE ENGINE ---
st.set_page_config(page_title="AI Based Diet Plan Generator", layout="wide")

# Added 'messages' to session state for Chatbot history
for key, val in {'w': 70.0, 'h': 175.0, 'a': 25, 'res_text': "", 'raw_text': "", 'messages': []}.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.markdown("""
    <style>
    .stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

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
        st.warning(f"Note: Some vitals couldn't be auto-filled. ({e})")

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📂 1. Clinical Input")
    uploaded_file = st.file_uploader("Upload Lab Report/Screenshot", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file and st.button("🔍 Sync Dashboard from File"):
        with st.status("🧬 Analyzing Data...") as s:
            sync_dashboard_from_file(uploaded_file)
            s.update(label="✅ Dashboard Updated!", state="complete")
    
    st.divider()
    model_choice = st.selectbox("LLM Engine", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 4. DASHBOARD ---
st.title("🥗 AI Based Diet Plan & Clinical Chat")

with st.container():
    st.markdown("### 🩺 2. Verify Patient Vitals")
    v1, v2, v3, v4 = st.columns(4)
    weight = v1.number_input("Weight (kg)", 30.0, 200.0, key="w")
    height = v2.number_input("Height (cm)", 100.0, 250.0, key="h")
    age = v3.number_input("Age", 1, 120, key="a")
    
    with v4:
        bmi = weight / ((height/100)**2)
        st.metric("Live BMI", f"{bmi:.1f}", "Healthy" if 18.5 <= bmi <= 25 else "Attention Required")

    p1, p2 = st.columns([2, 1])
    with p1: culture = st.multiselect("Dietary Culture", ["South Indian", "North Indian", "Keto", "Mediterranean"], default=["South Indian"])
    with p2: goal = st.select_slider("Clinical Goal", options=["Loss", "Maintain", "Muscle"])

    if st.button("🚀 GENERATE INITIAL REPORT", use_container_width=True):
        if not st.session_state.raw_text and not uploaded_file:
            st.error("Please upload a report or sync data first.")
        else:
            with st.status("🔍 Analyzing...") as status:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Dietitian: Analyze this lab data: {st.session_state.raw_text}. Create {goal} plan for {age}y, {weight}kg ({culture})."
                chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model_choice)
                st.session_state.res_text = chat.choices[0].message.content
                # Store report in chat history for RAG context
                st.session_state.messages.append({"role": "assistant", "content": f"**System: Initial Diet Plan Generated.**\n\n{st.session_state.res_text}"})
                status.update(label="✅ Report Ready! You can now chat below.", state="complete")

# --- 5. RAG CHATBOT INTERFACE ---
if st.session_state.res_text:
    st.divider()
    st.markdown("### 💬 Chat about your Nutrition Report")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if user_input := st.chat_input("Ask about swaps, allergies, or clinical values..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Context-Aware Inference
        with st.chat_message("assistant"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            # RAG Logic: Pass the generated report as system context
            system_context = f"""
            You are a Clinical Nutritionist Chatbot. 
            Base your answers on this generated report: {st.session_state.res_text}.
            Patient Vitals: Age {age}, Weight {weight}kg, Goal {goal}.
            Stay strictly within medical safety bounds.
            """
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_context},
                    *st.session_state.messages
                ],
                model=model_choice,
            )
            
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
