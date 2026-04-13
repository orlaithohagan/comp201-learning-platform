import streamlit as st
from games.games_hub import run_games_hub
from src.services.auth_ui import require_login, logout_button
from src.services.navigation import render_sidebar_navigation
from src.services.theme import apply_styles

# Set page configuration and apply styles
st.set_page_config(page_title="Mini Games", page_icon="🎮", layout="wide")
apply_styles("styles/mini_games.css")

# Render the mini games hub page with authentication and navigation
require_login()
render_sidebar_navigation("pages/MiniGames.py")
logout_button()
run_games_hub()