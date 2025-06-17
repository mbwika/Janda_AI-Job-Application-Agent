

# File: streamlit_app.py
import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Job Assistant", layout="centered")
st.title("🤖 AI Job Assistant")

# Session state to track conversation
if "step" not in st.session_state:
    st.session_state.step = "ask_email"
if "email" not in st.session_state:
    st.session_state.email = ""

if st.session_state.step == "ask_email":
    st.markdown("### 👋 Hi! What's your email address?")
    email_input = st.text_input("Email", key="email_input")
    if st.button("Submit Email") and email_input:
        st.session_state.email = email_input
        try:
            res = requests.post(f"{BACKEND_URL}/check-profile/", data={"email": email_input})
            data = res.json()
            st.session_state.profile_status = data.get("status")
            st.session_state.profile_message = data.get("message")
            st.session_state.step = "profile_response"
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

elif st.session_state.step == "profile_response":
    st.markdown(f"### 📬 {st.session_state.profile_message}")

    if st.session_state.profile_status == "new":
        st.markdown("Please [upload your resume here](http://localhost:8000/docs#/default/upload_resume_upload_resume_post) to get started.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Upload More Documents"):
                st.markdown("Please [upload your resume here](http://localhost:8000/docs#/default/upload_resume_upload_resume_post)")
        with col2:
            if st.button("Proceed to Job Search"):
                st.markdown("Starting job search and matching...")
                try:
                    res = requests.post(f"{BACKEND_URL}/run-multiagent/", data={"email": st.session_state.email})
                    st.success("🧠 Agent started processing in background!")
                except Exception as e:
                    st.error(f"Error: {e}")

