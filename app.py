import streamlit as st
import requests
import json
import os

# Configure the page
st.set_page_config(page_title="NanoCoder AI", page_icon="💻", layout="wide")

# Retrieve OpenRouter API Key from Hugging Face Secrets
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

st.title("💻 NanoCoder Web App")
st.caption("Powered by Hugging Face Spaces & OpenRouter Free Models")

# Sidebar for settings
st.sidebar.header("Configuration")
model_option = st.sidebar.selectbox(
    "Choose Free Coding Model:",
    [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "poolside/laguna-m.1:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nvidia/nemotron-3-nano-30b-a3b:free"
    ]
)

system_prompt = st.sidebar.text_area(
    "System Prompt", 
    "You are NanoCoder, a hyper-efficient, concise coding assistant. Provide clean, production-ready code blocks without unnecessary fluff."
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What do you want to code today?"):
    # Check if API key is present
    if not OPENROUTER_API_KEY:
        st.error("Missing OpenRouter API Key! Please set it up in your Space settings.")
        st.stop()

    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call OpenRouter API
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("*Thinking...*")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://huggingface.co/spaces", # Required by OpenRouter
            "Content-Type": "application/json"
        }
        
        # Format the context payload
        api_messages = [{"role": "system", "content": system_prompt}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        
        payload = {
            "model": model_option,
            "messages": api_messages
        }

        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if res.status_code == 200:
                response_json = res.json()
                assistant_response = response_json['choices'][0]['message']['content']
                response_placeholder.markdown(assistant_response)
                # Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                response_placeholder.markdown(f"⚠️ Error: {res.status_code} - {res.text}")
                
        except Exception as e:
            response_placeholder.markdown(f"⚠️ Failed to connect to OpenRouter: {str(e)}")
