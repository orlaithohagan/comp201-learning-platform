import streamlit as st
from games.MiniGames import run_games_hub
from src.services.auth_ui import require_login, logout_button
from src.services.navigation import render_sidebar_navigation

require_login()
render_sidebar_navigation("pages/MiniGames.py")
logout_button()

st.set_page_config(page_title="Mini Games", page_icon="🎮", layout="wide")

run_games_hub()