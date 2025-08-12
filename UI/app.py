import streamlit as st
import os
from PIL import Image
from agent_prep import get_agent_response, initialize_agent

# ========== Initialize Session State ==========
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default language is English
if 'agent' not in st.session_state:
    st.session_state.agent = initialize_agent() # Initialize the agent once
if 'config' not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "streamlit_session"}}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []



# ========== Text Translations ==========
translations = {
    'en': {
        'page_title': "GRC Agent | Saudi Cybersecurity Assistant",
        'banner_title': "🤖 GRC Agent – Saudi Cybersecurity Chatbot",
        'welcome_text': "Welcome to the Governance, Risk & Compliance (GRC) assistant powered by Saudi NCA guidelines.",
        'input_placeholder': "📝 Ask your question below:",
        'submit_button': "🔍 Submit",
        'response_title': "### 💡 GRC Agent Response:",
        'empty_input_warning': "⚠️ Please enter a valid question.",
        'language_button': "🌐 العربية"
    },
    'ar': {
        'page_title': "مساعد الأمن السيبراني السعودي | GRC Agent",
        'banner_title': "🤖 مساعد الأمن السيبراني السعودي",
        'welcome_text': " المدعوم بإرشادات الهيئة الوطنية للأمن السيبراني السعودي(GRC)مرحبًا بك في مساعد الحوكمة والمخاطر والامتثال",   
        'input_placeholder': "📝 اكتب سؤالك هنا:",
        'submit_button': "🔍 إرسال",
        'response_title': "### 💡 رد المساعد:",
        'empty_input_warning': "⚠️ الرجاء إدخال سؤال صحيح.",
        'language_button': "🌐 English"
    }
}

# Function to get text based on current language
def get_text(key):
    return translations[st.session_state.language][key]

# ========== UI ==========

st.set_page_config(page_title=get_text('page_title'), layout="wide")

# Load external CSS using a more reliable method
def local_css(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Get the absolute path to the CSS file
css_path = os.path.join(os.path.dirname(__file__), 'static', 'style.css')
local_css(css_path)

# Set a darker blue background color (dark mode) with enhanced aesthetics
st.markdown("""
    <style>
    .stApp {
        background-color: #0a1128; /* Even darker blue for dark mode */
        background-image: linear-gradient(to bottom right, #0a1128, #1a2a57); /* Gradient background */
    }
    
    /* Add a custom background for the main content area */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        margin-top: -3rem; /* Further reduce space between elements */
    }
    
    /* Style for the language button */
    .stButton > button {
        background-color: #4a90e2;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1.2rem;
        font-size: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #3a7bc8;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Increase font size for all text */
    p, div, span, h1, h2, h3, h4, h5, h6 {
        font-size: 1.25rem !important;
    }
    
    /* Make headings even larger with better styling */
    h1 {
        font-size: 2.5rem !important;
        color: #4a90e2 !important;
        margin-top: -2rem !important; /* Further reduce space after image */
        margin-bottom: 0.5rem !important; /* Reduce space below heading */
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    h2 {
        font-size: 2rem !important;
        color: #3a7bc8 !important;
    }
    
    h3 {
        font-size: 1.75rem !important;
        color: #2c5d99 !important;
    }
    
    /* Increase font size for input fields and improve styling */
    .stTextInput > div > div > input {
        font-size: 1.2rem !important;
        border-radius: 8px !important;
        border: 2px solid #4a90e2 !important;
        padding: 0.8rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3a7bc8 !important;
        box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.3) !important;
    }
    
    /* Add some spacing improvements */
    .row-widget {
        margin-bottom: 0 !important;
    }
    
    /* Reduce space between elements */
    .stTextInput {
        margin-top: -0.5rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Reduce space after markdown text */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    /* Specifically target the welcome text to reduce space after it */
    p {
        margin-bottom: 0.25rem !important;
    }
    
    /* Style for the image to make it look like an icon */
    .stImage img {
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        transition: transform 0.3s ease;
    }
    
    .stImage img:hover {
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# Add the background image using Streamlit's image display

# Create a header row with icon on left and language button on right
col1, col2, col3 = st.columns([1, 5, 1])

# Display the icon on the left
with col1:
    if os.path.exists("123.jpg"):
        st.image("123.jpg", width=90, caption="")



# Language toggle button on the right
with col3:
    if st.button(get_text('language_button')):
        # Toggle language
        st.session_state.language = 'ar' if st.session_state.language == 'en' else 'en'
        st.rerun()

# Title below the image
st.title(get_text('banner_title'))

# Welcome text below the title with custom styling to reduce space
st.markdown(f"""
    <div style="margin-bottom: -1rem;">
        {get_text('welcome_text')}
    </div>
""", unsafe_allow_html=True)

# 🔝 Banner
banner_class = "banner" + (" arabic" if st.session_state.language == 'ar' else "")

st.markdown(f"""
    <div class="{banner_class}">
        <div class="avatar">
            <img src="123.jpg" alt="GRC Agent Logo">
        </div>
        {get_text('banner_title')}
    </div>
""", unsafe_allow_html=True)

# 📦 Main content
content_class = "content" + (" arabic" if st.session_state.language == 'ar' else "")
st.markdown(f'<div class="{content_class}">', unsafe_allow_html=True)

# 💬 Input field
user_input = st.text_input(get_text('input_placeholder'))


# 📤 Submit button
if st.button(get_text('submit_button')):
    if user_input.strip():
        # Get response from the agent function
        with st.spinner("Thinking..."):
            raw_answer = get_agent_response(user_input, st.session_state.agent, st.session_state.config)
        
        # Display the response
        st.markdown(get_text('response_title'))
        st.success(raw_answer)
        

    else:
        st.warning(get_text('empty_input_warning'))


st.markdown('</div>', unsafe_allow_html=True)

# to save the chat history, populate the st.session_state.chat_history list with
# pairs of queries and responses.
# you can do that as a tuple. example: 
### st.session_state.chat_history.append(user_input.strip, raw_anser)
# or as subsequent entries. example:
### st.session_state.chat_history.append(user_input.strip())
### st.session_state.chat_history.append(raw_answer)
# or using any other approach you prefer
