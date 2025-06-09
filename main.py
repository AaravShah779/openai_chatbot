import streamlit as st
import openai
from openai import OpenAI
import time

# Streamlit page configuration
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0;
        margin: 0;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        height: 70vh;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background: #fafafa;
        margin-bottom: 20px;
    }
    
    /* User message bubble */
    .user-message {
        background: #007bff;
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 10px 0;
        margin-left: 20%;
        text-align: right;
        box-shadow: 0 2px 5px rgba(0,123,255,0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    /* Assistant message bubble */
    .assistant-message {
        background: #f1f3f4;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: 20%;
        text-align: left;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        animation: slideInLeft 0.3s ease-out;
        border-left: 4px solid #4CAF50;
    }
    
    /* Animations */
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e0e0e0;
        padding: 12px 20px;
        font-size: 16px;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #007bff;
        box-shadow: 0 0 10px rgba(0,123,255,0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,123,255,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,123,255,0.4);
    }
    
    /* API Key section */
    .api-section {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 5px 25px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 5px solid #007bff;
    }
    
    /* Status indicators */
    .status-connected {
        background: #d4edda;
        color: #155724;
        padding: 10px 15px;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 10px 15px;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 10px 0;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: inline-block;
        padding: 8px 16px;
        background: #f1f3f4;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: 20%;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        background: linear-gradient(45deg, #007bff, #0056b3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for Enter key functionality
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(function(mutations) {
        const input = document.querySelector('input[aria-label="Type your message..."]');
        if (input && !input.hasAttribute('data-listener-added')) {
            input.setAttribute('data-listener-added', 'true');
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const sendButton = document.querySelector('button[kind="primary"]');
                    if (sendButton) {
                        sendButton.click();
                    }
                }
            });
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
""", unsafe_allow_html=True)

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_validated" not in st.session_state:
    st.session_state.api_validated = False

def validate_api_key(api_key):
    """Validate OpenAI API key by making a simple request"""
    try:
        client = OpenAI(api_key=api_key)
        # Test with a minimal request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        return True, "API key is valid!"
    except openai.AuthenticationError:
        return False, "❌ Invalid API key. Please check your key and try again."
    except openai.RateLimitError:
        return False, "❌ Rate limit exceeded. Please check your OpenAI account."
    except openai.APIError as e:
        return False, f"❌ OpenAI API error: {str(e)}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# Main title
st.markdown('<h1 class="main-title">🤖 AI Chat Assistant</h1>', unsafe_allow_html=True)

# API Key section
if not st.session_state.api_key or not st.session_state.api_validated:
    st.markdown('<div class="api-section">', unsafe_allow_html=True)
    
    st.markdown("### 🔑 Connect Your OpenAI API Key")
    st.info("💡 Your API key is stored only for this session and is never saved permanently.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        api_key_input = st.text_input(
            "OpenAI API Key:", 
            type="password", 
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/api-keys",
            key="api_input"
        )
    
    with col2:
        st.write("")  # Empty space for alignment
        st.write("")  # Empty space for alignment
        connect_clicked = st.button("🔗 Connect", key="connect_btn")
    
    # Real-time API key validation
    if api_key_input and api_key_input.startswith("sk-"):
        if connect_clicked:
            with st.spinner("🔍 Validating API key..."):
                is_valid, message = validate_api_key(api_key_input)
                
            if is_valid:
                st.session_state.api_key = api_key_input
                st.session_state.api_validated = True
                st.markdown('<div class="status-connected">✅ Connected successfully! You can now start chatting.</div>', unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                st.markdown(f'<div class="status-error">{message}</div>', unsafe_allow_html=True)
    elif api_key_input and not api_key_input.startswith("sk-"):
        st.markdown('<div class="status-error">❌ API key should start with "sk-"</div>', unsafe_allow_html=True)
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📋 How to get your OpenAI API Key:")
    st.markdown("""
    1. 🌐 Go to [OpenAI Platform](https://platform.openai.com/)
    2. 👤 Sign up or log in to your account  
    3. 🔑 Go to [API Keys section](https://platform.openai.com/api-keys)
    4. ➕ Click 'Create new secret key'
    5. 📋 Copy the key and paste it above
    """)
    
    st.markdown("### 💡 Important Notes:")
    st.markdown("""
    • 💰 You will be charged based on your OpenAI usage
    • 🔒 Your API key is only stored in this browser session  
    • 🛡️ This app doesn't store or share your API key anywhere
    • 🚀 GPT-4 models cost more than GPT-3.5
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Initialize OpenAI client
try:
    client = OpenAI(api_key=st.session_state.api_key)
except Exception as e:
    st.markdown(f'<div class="status-error">❌ Error initializing OpenAI client: {e}</div>', unsafe_allow_html=True)
    if st.button("🔄 Reset API Key"):
        st.session_state.api_key = ""
        st.session_state.api_validated = False
        st.rerun()
    st.stop()

# Connected status
st.markdown('<div class="status-connected">🔗 Connected with your OpenAI API key</div>', unsafe_allow_html=True)

def get_openai_response(user_input, model="gpt-3.5-turbo"):
    """Get response from OpenAI API"""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful, friendly, and knowledgeable AI assistant. Provide clear, concise, and helpful responses."}
        ]
        
        # Add conversation history (last 10 messages to manage tokens)
        for msg in st.session_state.messages[-10:]:
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
            stream=False
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Chat interface
st.markdown("---")

# Display chat history in a container
chat_container = st.container()

with chat_container:
    if st.session_state.messages:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><strong>🤖 Assistant:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 50px; color: #666;">
            <h3>👋 Welcome to your AI Chat Assistant!</h3>
            <p>Start a conversation by typing a message below.</p>
            <p><em>Press Enter to send your message</em></p>
        </div>
        """, unsafe_allow_html=True)

# Input section
st.markdown("---")
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Type your message...", 
        placeholder="Ask me anything... (Press Enter to send)",
        key=f"user_input_{len(st.session_state.messages)}",  # Unique key to reset input
        label_visibility="collapsed"
    )

with col2:
    send_clicked = st.button("📤 Send", key="send_btn")

# Handle message sending
if (send_clicked or user_input) and user_input.strip():
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    
    # Get model from sidebar
    selected_model = getattr(st.session_state, 'selected_model', 'gpt-3.5-turbo')
    
    # Show typing indicator and get response
    with st.spinner("🤔 Thinking..."):
        ai_response = get_openai_response(user_input.strip(), selected_model)
    
    # Add AI response
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # Rerun to show updated conversation and clear input
    st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Chat Settings")
    
    # Model selection
    model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4o"]
    selected_model = st.selectbox(
        "🧠 Choose AI Model:",
        model_options,
        index=0,
        help="GPT-4 models are more capable but cost more"
    )
    st.session_state.selected_model = selected_model
    
    st.markdown("---")
    
    # Chat management
    st.markdown("## 💬 Chat Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🔄 New Session"):
            st.session_state.api_key = ""
            st.session_state.api_validated = False
            st.session_state.messages = []
            st.rerun()
    
    # Statistics
    st.markdown("---")
    st.markdown("## 📊 Session Stats")
    st.metric("Messages", len(st.session_state.messages))
    st.metric("Model", selected_model.upper())
    
    # Usage info
    st.markdown("---")
    st.markdown("## 💰 Usage Info")
    st.info("""
    **Your API Usage:**
    • Using your personal OpenAI key
    • Charges apply based on usage
    • Clear chat to save tokens
    • GPT-4 costs more than GPT-3.5
    """)
    
    # Tips
    st.markdown("---")
    st.markdown("## 💡 Pro Tips")
    st.success("""
    **Keyboard Shortcuts:**
    • Press **Enter** to send messages
    • Use **Shift+Enter** for new lines
    
    **Best Practices:**
    • Be specific in your questions
    • Break complex tasks into steps
    • Clear chat periodically to save costs
    """)
