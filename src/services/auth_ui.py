# src/services/auth_ui.py
import streamlit as st
from src.services.auth_service import authenticate, create_user


def _hide_sidebar():
    """Inject CSS to hide the sidebar on auth pages."""
    st.markdown('<div class="auth-hide-sidebar"></div>', unsafe_allow_html=True)

def _set_view(view: str):
    """Set the current auth view (welcome, login, signup) and rerun."""
    st.session_state["auth_view"] = view
    st.rerun()

def welcome_page():
    """Render the welcome page with options to log in or sign up."""
    _hide_sidebar()
    st.title("COMP201 Software Engineering Learning Hub 👋")
    st.write(
        "Welcome! Log in or create an account to access the AI Tutor, Flashcards, Quizzes, and Mini-Games."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Log in", use_container_width=True):
            _set_view("login")

    with col2:
        if st.button("Sign up", use_container_width=True):
            _set_view("signup")

def _login_user(user: dict):
    """Set the authenticated user in session state."""
    st.session_state["user"] = user
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]

def login_page():
    """Render the login page with username and password fields."""
    _hide_sidebar()
    st.title("Log in")
    st.caption("Enter your username and password to continue.")

    if st.button("Back", key="back_from_login"):
        _set_view("welcome")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Log in", use_container_width=True, key="login_btn"):
        user = authenticate(username, password)
        if not user:
            st.error("Invalid username or password.")
            st.stop()

        _login_user(user)

        st.success(f"Welcome, {user['username']}!")
        st.rerun()

    if st.button("Don’t have an account? Create one now", use_container_width=True, key="go_signup"):
        _set_view("signup")


def signup_page():
    """Render the signup page with fields for new username and password."""
    _hide_sidebar()
    st.title("Create account")
    st.caption("Create a student account to access the learning tools.")

    if st.button("Back", key="back_from_signup"):
        _set_view("welcome")

    new_user = st.text_input("New username", key="new_user")
    new_pass = st.text_input("New password", type="password", key="new_pass")
    new_pass2 = st.text_input("Confirm password", type="password", key="new_pass2")

    if st.button("Create account", use_container_width=True, key="create_btn"):
        if not new_user.strip():
            st.error("Please enter a username.")
            st.stop()

        if len(new_pass) < 6:
            st.error("Password should be at least 6 characters.")
            st.stop()

        if new_pass != new_pass2:
            st.error("Passwords do not match.")
            st.stop()

        ok = create_user(new_user.strip(), new_pass, role="student")
        if not ok:
            st.error("Username already exists (or database error).")
            st.stop()

        st.success("Account created! Please log in.")
        _set_view("login")

    if st.button("Already have an account? Log in", use_container_width=True, key="go_login"):
        _set_view("login")


def require_login():
    """Check if user is authenticated; if not, show auth UI and stop execution."""

    if st.session_state.get("user"):
        return

    if "auth_view" not in st.session_state:
        st.session_state["auth_view"] = "welcome"

    view = st.session_state["auth_view"]

    if view == "welcome":
        welcome_page()
        st.stop()

    if view == "signup":
        signup_page()
        st.stop()

    login_page()
    st.stop()

def _logout_user():
    """Clear user authentication from session state."""
    st.session_state.pop("user", None)
    st.session_state.pop("user_id", None)
    st.session_state.pop("username", None)
    st.session_state["auth_view"] = "welcome"

def logout_button():
    """Show logout in the sidebar when logged in."""
    if st.session_state.get("user"):
        with st.sidebar:
            st.markdown("---")
            st.write(f"👤 **{st.session_state['user']['username']}**")
            if st.button("Logout", use_container_width=True):
                _logout_user()
                st.rerun()

