import streamlit as st
import openai
from openai import OpenAI
import os

# Configure OpenAI API
client = OpenAI(api_key="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")

# Streamlit page configuration
st.set_page_config(
    page_title="OpenAI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 OpenAI Chatbot")
st.write("Powered by OpenAI's GPT model - Ask me anything!")

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
    st.markdown("**Note:**")
    st.markdown("• This uses your OpenAI API key")
    st.markdown("• Each message costs a small amount")
    st.markdown("• GPT-4 is more expensive than GPT-3.5")
    st.markdown("• Clear chat to save on tokens")

# Update the model in the function if user changes it
if 'model_choice' in locals():
    st.session_state.selected_model = model_choice
