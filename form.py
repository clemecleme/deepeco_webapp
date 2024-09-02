import streamlit as st
import requests
import os
from dotenv import load_dotenv
import threading

load_dotenv()

API_URL = os.getenv('API_URL')

# Set page config
st.set_page_config(page_title="Deep Ecology u2p050", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS (unchanged)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap');
    
    body {
        color: #FFFFFF;
        background-color: #0E1117;
    }
    .stApp {
        background-color: #0E1117;
    }
    .stTextInput > div > div > input {
        color: #FFFFFF;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stSelectbox > div > div > div {
        color: #FFFFFF;
        background-color: #0E1117;
    }
    .stSlider > div > div > div > div {
        color: #FFFFFF;
    }
    .stButton > button {
        color: #FFFFFF;
        background-color: rgba(255, 255, 255, 0.1);
        border: none;
    }
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    h1, h2, h3, p, label {
        color: #FFFFFF !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    .stAlert > div {
        color: #0E1117;
    }
    .main-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        box-sizing: border-box;
    }
    /* Improve visibility of success messages */
    .element-container div[data-testid="stText"] {
        color: #4CAF50 !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Questions (unchanged)
questions = {
    "English": [
        "What is your name?",
        "How old are you?",
        "What country are you living in these days?",
        "And what do you do for a living?",
        "How would you rate your comfort with technology, from 1 to 10?\n(10 being the maximum knowledge of technology)"
    ],
    "Chinese": [
        "你叫什麼名字?",
        "你多大年紀了?",
        "這些天你住在哪個國家?",
        "你是做什麼工作的?",
        "你如何評價你對技術的熟悉程度，從1到10？\n（10代表對技術有最高程度的了解）"
    ]
}

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = None
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'generating' not in st.session_state:
    st.session_state.generating = False

def run_api_calls(user_data):
    try:
        response = requests.post(f'{API_URL}/user_doc', json=user_data)
        if response.status_code == 200:
            user_id = response.json().get("user_id")
            gen_response = requests.post(f"{API_URL}/generate_experience", json={"user_id": user_id})
            if gen_response.status_code == 200:
                result = gen_response.json()
                if result.get("completed"):
                    st.session_state.completion_message = f"Experience completed for {result['name']}"
    except Exception as e:
        pass  # Silently handle any errors

# Main content area
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Language selection
if st.session_state.language is None:
    st.markdown("<h1 style='text-align: center;'>Select your language</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("English"):
            st.session_state.language = "English"
            st.rerun()
    with col2:
        if st.button("中文"):
            st.session_state.language = "Chinese"
            st.rerun()

# Form
elif st.session_state.language in questions and not st.session_state.form_submitted:
    st.markdown(f"<h1 style='text-align: center;'>Deep Ecology u2p050</h1>", unsafe_allow_html=True)
    
    with st.form("user_form"):
        for i, question in enumerate(questions[st.session_state.language]):
            if i == 4:  # Technology comfort question
                st.session_state.answers[question] = st.slider(question, 1, 10, 5)
            else:
                st.session_state.answers[question] = st.text_input(question)
        
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            st.session_state.form_submitted = True

            # Prepare user data
            user_data = {
                "language": st.session_state.language,
                "name": str(st.session_state.answers.get(questions[st.session_state.language][0], "")),
                "age": int(st.session_state.answers.get(questions[st.session_state.language][1], 0)),
                "country": str(st.session_state.answers.get(questions[st.session_state.language][2], "")),
                "profession": str(st.session_state.answers.get(questions[st.session_state.language][3], "")),
                "tech_relation": int(st.session_state.answers.get(questions[st.session_state.language][4], 5))
            }
            
            # Start API calls in a separate thread
            thread = threading.Thread(target=run_api_calls, args=(user_data,))
            thread.start()

            st.rerun()

# After form submission
if st.session_state.form_submitted:
    name = st.session_state.answers.get(questions[st.session_state.language][0], "")
    st.write(f"Thank you, {name}. We'll start soon.")
    
    # Reset button
    if st.button("Start New Form"):
        for key in ['language', 'answers', 'form_submitted', 'user_id']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)