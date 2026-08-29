import streamlit as st
from google import genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="My Custom Gemini", page_icon="🤖", layout="centered")

# Initialize Core Session States for Advanced Multi-Chat Memory
if "chats_history" not in st.session_state:
    st.session_state.chats_history = {}  # Format: {chat_id: {"title": str, "messages": list}}
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False  # Track visibility state of the file uploader

API_KEY = st.secrets["GEMINI_API_KEY"]

if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API_KEY)

# Helper function to generate a unique ID string for new conversations
def create_new_chat_session():
    import time
    new_id = f"chat_{int(time.time())}"
    st.session_state.chats_history[new_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_chat_id = new_id
    if "chat_engine" in st.session_state:
        del st.session_state["chat_engine"]

# Auto-initialize a default first conversation session if empty
if not st.session_state.chats_history or st.session_state.active_chat_id is None:
    create_new_chat_session()

active_id = st.session_state.active_chat_id

# 2. SIDEBAR: Chat History Session Dashboard
with st.sidebar:
    st.title("💬 Gemini Chats")
    
    if st.button("➕ New Chat", use_container_width=True):
        create_new_chat_session()
        st.rerun()
        
    st.markdown("---")
    st.subheader("Recent Conversations")
    
    for chat_id in list(st.session_state.chats_history.keys()):
        chat_data = st.session_state.chats_history[chat_id]
        side_col1, side_col2 = st.columns([4, 1]) # Allocate wider space for name label
        
        with side_col1:
            is_current = "🔹 " if chat_id == active_id else ""
            if st.button(f"{is_current}{chat_data['title']}", key=f"sel_{chat_id}", use_container_width=True):
                st.session_state.active_chat_id = chat_id
                if "chat_engine" in st.session_state:
                    del st.session_state["chat_engine"]
                st.rerun()
                
        with side_col2:
            if st.button("🗑️", key=f"del_{chat_id}", use_container_width=True):
                del st.session_state.chats_history[chat_id]
                if st.session_state.active_chat_id == chat_id:
                    st.session_state.active_chat_id = list(st.session_state.chats_history.keys()) if st.session_state.chats_history else None
                if "chat_engine" in st.session_state:
                    del st.session_state["chat_engine"]
                st.rerun()

st.title("🤖 My Personal Gemini AI")

active_messages = st.session_state.chats_history[active_id]["messages"]

# 3. Quick Action Buttons (Only show if chat history is empty)
if not active_messages:
    st.markdown("### ⚡ Quick Prompts")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Explain Asset", use_container_width=True):
            st.session_state.show_uploader = True
            st.rerun()
            
    with col2:
        if st.button("🐛 Review My Code", use_container_width=True):
            st.session_state.show_uploader = True
            st.rerun()
            
    with col3:
        if st.button("📝 Summarize Document", use_container_width=True):
            st.session_state.show_uploader = True
            st.rerun()

# 4. Render active historical chat items to user screen
for msg in active_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. DYNAMIC TOGGLE ASSET CONTROLLER
uploaded_file = None
audio_file = None
ai_role = "Standard Assistant"
instructions = "You are a helpful assistant."

# Toggle button at the workspace layout layer
if st.button("➕ Toggle Asset Panel / Personality Menu"):
    st.session_state.show_uploader = not st.session_state.show_uploader
    st.rerun()

if st.session_state.show_uploader:
    st.markdown("---")
    with st.container():
        st.subheader("📎 Attached Asset Control")
        exp_col1, exp_col2 = st.columns(2)
        
        with exp_col1:
            # Let the user pick personality options
            ai_role = st.selectbox(
                "AI Personality:",
                ["Standard Assistant", "Expert Code Tutor", "Creative Writer", "Sarcastic Friend"]
            )
            if ai_role == "Expert Code Tutor":
                instructions = "You are an expert software engineer. Provide clear code snippets and explain logic step-by-step."
            elif ai_role == "Creative Writer":
                instructions = "You are an imaginative storyteller. Use rich metaphors and vivid descriptions."
            elif ai_role == "Sarcastic Friend":
                instructions = "You are a witty, sarcastic friend. Use lighthearted humor and playful banter."
                
            # If the user swapped roles, safely delete old engine reference to update system instruction configuration cleanly
            if "current_role" not in st.session_state or st.session_state.current_role != ai_role:
                st.session_state.current_role = ai_role
                if "chat_engine" in st.session_state:
                    del st.session_state["chat_engine"]
                
        with exp_col2:
            uploaded_file = st.file_uploader(
                "Upload Image or Text File:", 
                type=["png", "jpg", "jpeg", "txt", "py", "md"]
            )
            # Inside your asset control block
            audio_file = st.audio_input("Record a voice prompt")

            if audio_file is not None:
            # Pass the audio bytes directly into Gemini alongside a text prompt
                response = st.session_state.chat_engine.send_message([
                    "Listen to this voice recording and reply:",
                    audio_file,
                ])

# 6. Initialize the persistent engine connection layer with target instructions payload safely
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = st.session_state.client.chats.create(
        model="gemini-3.6-flash",
        config={"system_instruction": instructions}
    )

# 7. CHAT INPUT LAYER (Locked permanently to screen footer baseline natively)
user_prompt = st.chat_input("Ask your custom Gemini anything...")

# 8. Process Input and Communicate with Gemini Backend
if user_prompt or audio_file:
    # Set a title if it's a new chat
    if st.session_state.chats_history[active_id]["title"] == "New Chat":
        display_title = user_prompt if user_prompt else "Voice Message"
        words = display_title.split()
        short_title = " ".join(words[:4]) + "..." if len(words) > 4 else display_title
        st.session_state.chats_history[active_id]["title"] = short_title
        
    # Display user input in chat
    if user_prompt:
        with st.chat_message("user"):
            st.markdown(user_prompt)
        active_messages.append({"role": "user", "content": user_prompt})
    elif audio_file:
        with st.chat_message("user"):
            st.audio(audio_file)
        active_messages.append({"role": "user", "content": "🎤 [Voice Message]"})

    # Get response from Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 *Thinking...*")
        
        try:
            if audio_file is not None:
                prompt_payload = [user_prompt if user_prompt else "Listen to this voice recording and reply:", audio_file]
                response = st.session_state.chat_engine.send_message(prompt_payload)
            elif uploaded_file is not None:
                file_name = uploaded_file.name
                if any(file_name.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                    img_data = Image.open(uploaded_file)
                    response = st.session_state.chat_engine.send_message([user_prompt, img_data])
                else:
                    file_text_content = uploaded_file.read().decode("utf-8")
                    combined_prompt = f"--- ATTACHED FILE DOCUMENT ---\n{file_text_content}\n---\nQuestion: {user_prompt}"
                    response = st.session_state.chat_engine.send_message(combined_prompt)
            else:
                response = st.session_state.chat_engine.send_message(user_prompt)
                
            message_placeholder.markdown(response.text)
            active_messages.append({"role": "assistant", "content": response.text})
            
            # Hide asset overlay drawer following message submission
            st.session_state.show_uploader = False
            st.rerun()
            
        except Exception as e:
            message_placeholder.markdown(f"❌ **Error:** {e}")