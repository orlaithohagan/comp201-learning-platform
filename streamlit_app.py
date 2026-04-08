import streamlit as st
from src.services.db import init_db
from src.services.auth_ui import require_login, logout_button
from src.progress import create_progress_tables
from src.services.navigation import render_sidebar_navigation
from src.services.theme import apply_styles

st.set_page_config(page_title="COMP201 Learning Hub", layout="wide")
apply_styles("styles/home.css")

init_db()
create_progress_tables()
require_login()
render_sidebar_navigation("streamlit_app.py")
logout_button()

username = st.session_state["user"]["username"]

def render_home_card(title, text, button_label, page_path, button_key):
    st.markdown(
        f"""
        <div class="uol-card">
            <div class="home-card-title">{title}</div>
            <div class="home-card-text">
                {text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button(button_label, key=button_key):
        st.switch_page(page_path)

st.markdown(
    f"""
    <div class="uol-hero">
        <h1>COMP201 Learning Platform</h1>
        <p class="uol-hero-subtext">
            Welcome back, <strong>{username}</strong> 👋
        </p>
        <p class="uol-hero-subtext">
            Your personalised software engineering study hub for revision, practice, progress tracking, and AI-supported learning.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Quick access cards
st.markdown('<div class="home-section-title">Quick Access</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    render_home_card(
        "📊 Dashboard",
        "View your topic mastery, quiz progress, achievements, and personalised recommendations.",
        "Open Dashboard",
        "pages/Dashboard.py",
        "home_dashboard",
    )

with col2:
    render_home_card(
        "🤖 AI Tutor",
        "Ask questions, review weak topics, and get course-aware explanations using AI and your learning materials.",
        "Open AI Tutor",
        "pages/AITutor.py",
        "home_tutor",
    )

with col3:
    render_home_card(
        "📝 Quiz",
        "Test your understanding of COMP201 topics and build progress through structured revision.",
        "Open Quiz",
        "pages/Quiz.py",
        "home_quiz",
    )

st.markdown(
    """
    <div class="home-highlight">
        <strong>Getting started:</strong> Use the sidebar to explore flashcards, mini-games, quizzes, concept maps, the dashboard, and the AI tutor.
    </div>
    """,
    unsafe_allow_html=True
)