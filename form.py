import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()
API_URL = os.getenv('API_URL')

# Check query parameters to determine the view
query_params = st.experimental_get_query_params()
is_mediator = 'mediator' in query_params

st.set_page_config(page_title="DeepEcology", layout="centered")

# Initialize session state
if 'form_state' not in st.session_state:
    st.session_state.form_state = 'initial'
if 'language' not in st.session_state:
    st.session_state.language = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

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

def visitor_view():
    st.markdown("<h1 style='text-align: center;'>Deep Ecology</h1>", unsafe_allow_html=True)

    if st.session_state.form_state == 'initial':
        pass  # Just show "Deep Ecology"
    elif st.session_state.form_state == 'language_selection':
        st.markdown("<h2 style='text-align: center;'>Select your language</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("English"):
                st.session_state.language = "English"
                st.session_state.form_state = 'form'
                st.rerun()
        with col2:
            if st.button("中文"):
                st.session_state.language = "Chinese"
                st.session_state.form_state = 'form'
                st.rerun()
    elif st.session_state.form_state == 'form':
        with st.form("user_form"):
            answers = {}
            for i, question in enumerate(questions[st.session_state.language]):
                if i == 4:  # Technology comfort question
                    answers[question] = st.slider(question, 1, 10, 5)
                else:
                    answers[question] = st.text_input(question)
            
            submit_button = st.form_submit_button("Submit")
            
            if submit_button:
                user_data = {
                    "language": st.session_state.language,
                    "name": str(answers.get(questions[st.session_state.language][0], "")),
                    "age": int(answers.get(questions[st.session_state.language][1], "")),
                    "country": str(answers.get(questions[st.session_state.language][2], "")),
                    "profession": str(answers.get(questions[st.session_state.language][3], "")),
                    "tech_relation": int(answers.get(questions[st.session_state.language][4], ""))
                }
                
                try:
                    response = requests.post(f'{API_URL}/user_doc', json=user_data)
                    if response.status_code == 200:
                        st.session_state.form_state = 'submitted'
                        st.session_state.user_data = user_data
                        st.session_state.user_data['user_id'] = response.json().get("user_id")
                        st.rerun()
                    else:
                        st.error('Error submitting data. Please try again.')
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")
    elif st.session_state.form_state == 'submitted':
        st.success("✅ Submitted")
        time.sleep(2)
        st.session_state.form_state = 'initial'
        st.session_state.language = None
        st.rerun()

def mediator_view():
    st.title("Mediator Dashboard")
    if st.button("Allow New Form"):
        st.session_state.form_state = 'language_selection'
        st.success("New form allowed. Visitor can now select language.")

    if st.session_state.user_data:
        st.write(f"Last submission: {st.session_state.user_data['name']}")
        if st.button("Generate Experience"):
            st.write(f"Generating voice over for {st.session_state.user_data['name']}, (visitor ID: {st.session_state.user_data['user_id']})")
            try:
                response = requests.post(f"{API_URL}/generate_experience", json={"user_id": st.session_state.user_data['user_id']})
                if response.status_code == 200:
                    st.success(f"Generation completed. Experience is ready to be started for {st.session_state.user_data['name']}.")
                else:
                    st.error("Error generating experience. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")

# Main app logic
if is_mediator:
    mediator_view()
else:
    visitor_view()