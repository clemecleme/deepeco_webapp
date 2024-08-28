import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

API_URL = os.getenv('API_URL')

# Set page config
st.set_page_config(page_title="Deep Ecology u2p050", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap');
    
    body {
        color: #FFFFFF;
        background-color: #0E1117;
        font-family: 'Roboto', sans-serif;
    }
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 300;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .stTextInput > div > div > input {
        color: #FFFFFF;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    h1, h2, h3 {
        font-weight: 300;
        letter-spacing: 1px;
    }
    .main-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        box-sizing: border-box;
    }
    </style>
    """, unsafe_allow_html=True)

# Questions
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
            # Prepare user data
            user_data = {
                "language": st.session_state.language,
                "name": str(st.session_state.answers.get(questions[st.session_state.language][0], "")),
                "age": int(st.session_state.answers.get(questions[st.session_state.language][1], "")),
                "country": str(st.session_state.answers.get(questions[st.session_state.language][2], "")),
                "profession": str(st.session_state.answers.get(questions[st.session_state.language][3], "")),
                "tech_relation": int(st.session_state.answers.get(questions[st.session_state.language][4], ""))
            }
            
            try:
                response = requests.post(f'{API_URL}/user_doc', json=user_data)
                if response.status_code == 200:
                    st.session_state.form_submitted = True
                    st.session_state.user_id = response.json().get("user_id")
                    st.rerun()
                else:
                    st.markdown('Error submitting data. Please try again.')
            except requests.exceptions.RequestException:
                st.markown("An error occurred. Please try again.")

# After form submission
elif st.session_state.form_submitted:
    st.markdown(f"<h1 style='text-align: center;'>Deep Ecology u2p050</h1>", unsafe_allow_html=True)
    name = st.session_state.answers.get(questions[st.session_state.language][0], "")
    st.success(f"Thank you, {name}. We'll start soon.")
    
    with st.spinner("Generating..."):
        gen_response = requests.post(f"{API_URL}/generate_experience", json={"user_id": st.session_state.user_id})
        if gen_response.status_code == 200:
            while True:
                try:
                    check_response = requests.get(f"{API_URL}/check_audio_files", params={"user_id": st.session_state.user_id})
                    if check_response.status_code == 200:
                        data = check_response.json()
                        if data.get("audio_files_count", 0) == 6:
                            st.success("Experience generated successfully!")
                            break
                    time.sleep(5)  # Wait for 5 seconds before checking again
                except requests.exceptions.RequestException:
                    st.markdown("<p style='color: grey;'>More info in the log.</p>", unsafe_allow_html=True)
                    break
        else:
            st.markdown("<p style='color: grey;'>More info in the log.</p>", unsafe_allow_html=True)

    # Reset button
    if st.button("Start New Session"):
        for key in ['language', 'answers', 'form_submitted', 'user_id']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()