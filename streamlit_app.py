import streamlit as st
from src.services.db import init_db
from src.services.auth_ui import require_login, logout_button
from src.progress import create_progress_tables

st.set_page_config(page_title="COMP201 Learning Hub", layout="wide")

init_db()
create_progress_tables()  # Initialize progress tracking tables
require_login()   # shows Welcome/Login/Signup until authenticated

# Sidebar logout + user label
logout_button()

# Main app content
st.title("COMP201 Learning Platform")
st.caption(f"Welcome back, {st.session_state['user']['username']} 👋")
st.write("Use the sidebar to access tools.")


