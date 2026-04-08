# 🥗 AI BAESED-DIET PLAN GENERATOR | Clinical AI Engine
**Next-Gen Precision Nutrition & Automated Lab Analytics**

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Inference-Groq_Cloud-1D9E75?style=for-the-badge)
![LLM](https://img.shields.io/badge/LLM-Llama_3.3_70B-orange?style=for-the-badge)

---

## 🚀 Overview
An intelligent clinical assistant that bridges the gap between raw medical data and actionable nutrition. **AI BAESED-DIET PLAN GENERATOR** automates the extraction of patient vitals from lab reports and generates hyper-personalized diet protocols using RAG-enhanced LLMs.

*   **Clinical OCR Sync:** Instant extraction of BMI, glucose, and lipid markers.
*   **Agentic RAG Chatbot:** Context-aware Q&A based on the generated nutrition report.
*   **Dynamic BMR/TDEE Engine:** Real-time metabolic calculations using Mifflin-St Jeor logic.

---

## 🏗️ System Architecture
```mermaid
graph LR
    A[Lab Report / PDF] --> B{OCR Engine}
    B -->|Extract Vitals| C[Logic Engine]
    C -->|BMR / TDEE| D[Groq Llama 3.3]
    D -->|Gen AI| E[Personalized Diet Plan]
    E --> F[RAG Chatbot Interface]
