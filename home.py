import streamlit as st

st.set_page_config(page_title="DeepEcology", layout="centered")

st.title("DeepEcology")

col1, col2 = st.columns(2)
with col1:
    if st.button("Visitor Form"):
        st.switch_page("pages/1_form.py")
with col2:
    if st.button("Mediator Dashboard"):
        st.switch_page("pages/2_mediator_dashboard.py")