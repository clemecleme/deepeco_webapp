import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')

st.set_page_config(page_title="DeepEcology Mediator Dashboard", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS (you can adjust as needed)
st.markdown("""
    <style>
    /* Your CSS styles */
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'form_state' not in st.session_state:
    st.session_state.form_state = 'initial'
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False
if 'allow_new_form' not in st.session_state:
    st.session_state.allow_new_form = False

st.title("Mediator Dashboard")

if st.button("Allow New Form"):
    st.session_state.form_state = 'language_selection'
    st.session_state.user_data = None
    st.session_state.generation_complete = False
    st.session_state.allow_new_form = True
    st.success("New form allowed. Waiting for visitor submission...")

if st.session_state.user_data and not st.session_state.generation_complete:
    user_data = st.session_state.user_data
    st.write(f"Generating voice over for {user_data['name']}, (visitor ID: {user_data['user_id']})")
    st.spinner("Generating...")
    
    # Start generation
    try:
        response = requests.post(f"{API_URL}/generate_experience", json={"user_id": user_data['user_id']})
        if response.status_code == 200:
            st.session_state.generation_complete = True
            st.success(f"Generation completed. Experience is ready to be started for {user_data['name']}.")
        else:
            st.error("Error generating experience. Please try again.")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")

elif st.session_state.generation_complete:
    user_data = st.session_state.user_data
    st.success(f"Experience is ready to be started for {user_data['name']}.")