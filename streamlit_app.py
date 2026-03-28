import streamlit as st
from src.services.db import init_db
from src.services.auth_ui import require_login, logout_button
from src.progress import create_progress_tables
from src.utils import load_css
from src.services.navigation import render_sidebar_navigation

st.set_page_config(page_title="COMP201 Learning Hub", layout="wide")

# Load CSS
st.markdown(
    f"<style>{load_css('styles/main.css', 'styles/home.css')}</style>",
    unsafe_allow_html=True
)

init_db()
create_progress_tables()
require_login()
render_sidebar_navigation("streamlit_app.py")
logout_button()

username = st.session_state["user"]["username"]

# Hero section
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
    st.markdown(
        """
        <div class="uol-card">
            <div class="home-card-title">📊 Dashboard</div>
            <div class="home-card-text">
                View your topic mastery, quiz progress, achievements, and personalised recommendations.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Dashboard", key="home_dashboard"):
        st.switch_page("pages/Dashboard.py")

with col2:
    st.markdown(
        """
        <div class="uol-card">
            <div class="home-card-title">🤖 AI Tutor</div>
            <div class="home-card-text">
                Ask questions, review weak topics, and get course-aware explanations using AI and your learning materials.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open AI Tutor", key="home_tutor"):
        st.switch_page("pages/AITutor.py")

with col3:
    st.markdown(
        """
        <div class="uol-card">
            <div class="home-card-title">📝 Quiz</div>
            <div class="home-card-text">
                Test your understanding of COMP201 topics and build progress through structured revision.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Quiz", key="home_quiz"):
        st.switch_page("pages/Quiz.py")

st.markdown(
    """
    <div class="home-highlight">
        <strong>Getting started:</strong> Use the sidebar to explore flashcards, mini-games, quizzes, concept maps, the dashboard, and the AI tutor.
    </div>
    """,
    unsafe_allow_html=True
)
