import streamlit as st
from src.services.db import init_db
from src.services.auth_ui import require_login, logout_button

st.set_page_config(page_title="COMP201 Learning Platform", layout="wide")

if "user" not in st.session_state:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )


init_db()          # ensure tables exist
require_login()    # block if not logged in
logout_button()

st.title("COMP201 Learning Platform")
st.caption(f"Logged in as: {st.session_state['user']['username']}")
