# My Personal Gemini AI 🤖

A fully featured, multi-chat AI assistant web application built with **Python**, **Streamlit**, and the **Google Gemini API** (using the advanced `google-genai` SDK).

## ✨ Features
- **💬 Multi-Chat Dashboards:** Create, rename, and delete multiple conversation histories seamlessly.
- **🎭 AI Personality Swapper:** Change your assistant's tone instantly (Expert Code Tutor, Creative Writer, Sarcastic Friend).
- **📎 Multi-Modal File Controller:** Upload text documentation or source code files for analysis, or upload images directly to the chatbot.
- **🎤 Voice Input Processor:** Directly record voice prompts into the app interface.
- **⚠️ Quota Management:** Built-in catch features to gracefully lock input streams when api limits are crossed.

## ⚙️ How to Setup locally

1. **Clone the project repository:**
   ```bash
   git clone https://github.com
   cd My-own-custom-Gemini
   ```

2. **Install necessary dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Secrets:**
   Create a folder named `.streamlit` and add a `secrets.toml` file inside it:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

4. **Launch the application interface:**
   ```bash
   streamlit run app.py
   ```
