import streamlit as st
import openai
from openai import OpenAI
import os

# Streamlit page configuration
st.set_page_config(
    page_title="OpenAI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 OpenAI Chatbot")

# Check if API key is provided
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if not st.session_state.api_key:
    st.write("Welcome! To use this chatbot, you need to provide your own OpenAI API key.")
    
    # API Key input section
    st.markdown("### 🔑 Enter Your OpenAI API Key")
    st.info("Your API key is stored only for this session and is not saved anywhere.")
    
    api_key_input = st.text_input(
        "OpenAI API Key:", 
        type="password", 
        placeholder="sk-...",
        help="Get your API key from https://platform.openai.com/api-keys"
    )
    
    if st.button("Connect"):
        if api_key_input.strip():
            if api_key_input.startswith("sk-"):
                st.session_state.api_key = api_key_input.strip()
                st.success("✅ API Key connected! You can now start chatting.")
                st.rerun()
            else:
                st.error("❌ Please enter a valid OpenAI API key (starts with 'sk-')")
        else:
            st.warning("⚠️ Please enter your API key first")
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📋 How to get your OpenAI API Key:")
    st.markdown("1. Go to [OpenAI Platform](https://platform.openai.com/)")
    st.markdown("2. Sign up or log in to your account")
    st.markdown("3. Go to [API Keys section](https://platform.openai.com/api-keys)")
    st.markdown("4. Click 'Create new secret key'")
    st.markdown("5. Copy the key and paste it above")
    
    st.markdown("### 💡 Note:")
    st.markdown("• You will be charged based on your OpenAI usage")
    st.markdown("• Your API key is only stored in this session")
    st.markdown("• This app doesn't store or share your API key")
    
    st.stop()

# If API key is provided, show the chatbot
st.write("🔗 Connected with your OpenAI API key")

# Initialize OpenAI client with user's API key
try:
    client = OpenAI(api_key=st.session_state.api_key)
except Exception as e:
    st.error(f"❌ Invalid API key: {e}")
    if st.button("Reset API Key"):
        st.session_state.api_key = ""
        st.rerun()
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_openai_response(user_input):
    """Get response from OpenAI API"""
    try:
        # Prepare conversation history for OpenAI
        messages = [
            {"role": "system", "content": "You are a helpful, friendly assistant. Keep responses conversational and helpful."}
        ]
        
        # Add conversation history (last 10 messages to avoid token limits)
        for msg in st.session_state.messages[-10:]:
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_input})
        
        # Get response from OpenAI
        selected_model = getattr(st.session_state, 'selected_model', 'gpt-3.5-turbo')
        response = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Assistant:** {message['content']}")

# User input
user_input = st.text_input("Type your message:", placeholder="Ask me anything...", key="input")

if st.button("Send"):
    if user_input.strip():
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("Thinking..."):
            ai_response = get_openai_response(user_input)
        
        # Add AI response to history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Rerun to clear input and show updated conversation
        st.rerun()
    else:
        st.warning("Please type a message first!")

# Sidebar options
with st.sidebar:
    st.header("Chat Options")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Change API Key"):
        st.session_state.api_key = ""
        st.session_state.messages = []
        st.rerun()
    
    st.write(f"Messages: {len(st.session_state.messages)}")
    
    # Model selection
    st.markdown("---")
    st.markdown("**Settings:**")
    model_choice = st.selectbox(
        "Choose Model:",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        index=0
    )
    
    # Note about usage
    st.markdown("---")
    st.markdown("**Your Usage:**")
    st.markdown("• Using your own OpenAI API key")
    st.markdown("• You pay for what you use")
    st.markdown("• GPT-4 costs more than GPT-3.5")
    st.markdown("• Clear chat to save tokens")

# Update the model in the function if user changes it
if 'model_choice' in locals():
    st.session_state.selected_model = model_choice
