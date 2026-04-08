# 🥗 AI-Based Diet Plan Generator

A clinical nutrition assistant powered by Groq LLMs. Upload lab reports or medical scans, auto-sync patient vitals, and generate personalized diet plans with a real-time RAG chatbot for follow-up queries.

---

<details>
<summary><b>📁 Project structure</b></summary>

| File | Description |
| :--- | :--- |
| `app.py` | Main Streamlit UI — dashboard, OCR sync, chatbot |
| `ai_engine.py` | Standalone Gemini test script |
| `nutrition_logic.py` | BMR / TDEE calculation utilities |
| `requirements.txt` | All Python dependencies |

</details>

<details>
<summary><b>⚡ Quick start</b></summary>

1. **Clone the repo:** `git clone https://github.com/your-username/ai-diet-plan-generator.git && cd ai-diet-plan-generator`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Setup Secrets:** Create `.streamlit/secrets.toml` and add your Groq API key.
4. **Run:** `streamlit run app.py`

</details>

<details>
<summary><b>🛠️ Tech stack</b></summary>

* **Streamlit**: UI framework
* **Groq API**: LLM inference (LLaMA 3.3 70B)
* **EasyOCR**: Text extraction from image lab reports
* **PyPDF2**: PDF text extraction

</details>
