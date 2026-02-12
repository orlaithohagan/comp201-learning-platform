import streamlit as st
from src.services.auth_ui import require_login, logout_button


require_login()
logout_button()

st.title("AI Tutor")

st.markdown(
    "Use the AI Tutor to ask questions about COMP201 Software Engineering topics "
    "(e.g., requirements, UML, testing, processes)."
)

GPT_LINK = "https://chatgpt.com/g/g-693c17c97eb4819190780cfb402e9fe4-ai-tutor"

st.link_button("Open AI Tutor (Custom GPT)", GPT_LINK)
st.caption("Note: You may need to be logged into ChatGPT to use the tutor.")
