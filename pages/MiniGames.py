"""
Mini Games Page Module.

This module implements the Mini Games page for the COMP201 learning platform,
serving as the entry point for accessing interactive mini-games that reinforce
software engineering concepts through gamified learning experiences.

The page provides a simple wrapper that:
- Sets up page configuration and styling
- Handles user authentication and navigation
- Delegates to the games hub for game selection and management

"""

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