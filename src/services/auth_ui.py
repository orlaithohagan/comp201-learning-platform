# """
# Authentication UI components for login, signup, and session management.

# Provides Streamlit UI functions for user authentication flows including
# welcome page, login/signup forms, logout functionality, and login requirements.
# """

# import streamlit as st
# from src.services.auth_service import authenticate, create_user

# def _hide_sidebar():
#     """Inject CSS to hide the sidebar on auth pages."""
#     st.markdown('<div class="auth-hide-sidebar"></div>', unsafe_allow_html=True)

# def _set_view(view: str):
#     """Set the current auth view (welcome, login, signup) and rerun."""
#     st.session_state["auth_view"] = view
#     st.rerun()

# def welcome_page():
#     """Render the welcome page with options to log in or sign up."""
#     _hide_sidebar()
#     st.title("COMP201 Software Engineering Learning Hub 👋")
#     st.write(
#         "Welcome! Log in or create an account to access the AI Tutor, Flashcards, Quizzes, and Mini-Games."
#     )

#     col1, col2 = st.columns(2)

#     with col1:
#         if st.button("Log in", use_container_width=True):
#             _set_view("login")

#     with col2:
#         if st.button("Sign up", use_container_width=True):
#             _set_view("signup")

# def _login_user(user: dict):
#     """Set the authenticated user in session state."""
#     st.session_state["user"] = user
#     st.session_state["user_id"] = user["id"]
#     st.session_state["username"] = user["username"]

# def login_page():
#     """Render the login page with username and password fields."""
#     _hide_sidebar()
#     st.title("Log in")
#     st.caption("Enter your username and password to continue.")

#     if st.button("Back", key="back_from_login"):
#         _set_view("welcome")

#     username = st.text_input("Username", key="login_user")
#     password = st.text_input("Password", type="password", key="login_pass")

#     if st.button("Log in", use_container_width=True, key="login_btn"):
#         user = authenticate(username, password)
#         if not user:
#             st.error("Invalid username or password.")
#             st.stop()

#         _login_user(user)

#         st.success(f"Welcome, {user['username']}!")
#         st.rerun()

#     if st.button("Don’t have an account? Create one now", use_container_width=True, key="go_signup"):
#         _set_view("signup")


# def signup_page():
#     """Render the signup page with fields for new username and password."""
#     _hide_sidebar()
#     st.title("Create account")
#     st.caption("Create a student account to access the learning tools.")

#     if st.button("Back", key="back_from_signup"):
#         _set_view("welcome")

#     new_user = st.text_input("New username", key="new_user")
#     new_pass = st.text_input("New password", type="password", key="new_pass")
#     new_pass2 = st.text_input("Confirm password", type="password", key="new_pass2")

#     if st.button("Create account", use_container_width=True, key="create_btn"):
#         if not new_user.strip():
#             st.error("Please enter a username.")
#             st.stop()

#         if len(new_pass) < 6:
#             st.error("Password should be at least 6 characters.")
#             st.stop()

#         if new_pass != new_pass2:
#             st.error("Passwords do not match.")
#             st.stop()

#         ok = create_user(new_user.strip(), new_pass, role="student")
#         if not ok:
#             st.error("Username already exists (or database error).")
#             st.stop()

#         st.success("Account created! Please log in.")
#         _set_view("login")

#     if st.button("Already have an account? Log in", use_container_width=True, key="go_login"):
#         _set_view("login")


# def require_login():
#     """Check if user is authenticated; if not, show auth UI and stop execution."""

#     if st.session_state.get("user"):
#         return

#     if "auth_view" not in st.session_state:
#         st.session_state["auth_view"] = "welcome"

#     view = st.session_state["auth_view"]

#     if view == "welcome":
#         welcome_page()
#         st.stop()

#     if view == "signup":
#         signup_page()
#         st.stop()

#     login_page()
#     st.stop()

# def _logout_user():
#     """Clear user authentication from session state."""
#     st.session_state.pop("user", None)
#     st.session_state.pop("user_id", None)
#     st.session_state.pop("username", None)
#     st.session_state["auth_view"] = "welcome"

# def logout_button():
#     """Show logout in the sidebar when logged in."""
#     if st.session_state.get("user"):
#         with st.sidebar:
#             st.markdown("---")
#             st.write(f"👤 **{st.session_state['user']['username']}**")
#             if st.button("Logout", use_container_width=True):
#                 _logout_user()
#                 st.rerun()

"""
Authentication UI components for login, signup, and session management.

Provides Streamlit UI functions for user authentication flows including
welcome page, login/signup forms, logout functionality, and login requirements.
"""

import streamlit as st
from src.services.auth_service import authenticate, create_user
from src.services.theme import apply_styles


def _hide_sidebar():
    """Inject CSS hook to hide the sidebar on authentication screens."""
    st.markdown('<div class="auth-hide-sidebar"></div>', unsafe_allow_html=True)


def _set_view(view: str):
    """Set the current auth view and rerun the app."""
    st.session_state["auth_view"] = view
    st.rerun()


def _login_user(user: dict):
    """Store authenticated user details in session state."""
    st.session_state["user"] = user
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]


def _logout_user():
    """Clear authenticated user data from session state."""
    st.session_state.pop("user", None)
    st.session_state.pop("user_id", None)
    st.session_state.pop("username", None)
    st.session_state["auth_view"] = "welcome"


def _handle_create_user_result(result):
    """
    Normalise create_user return values.

    Supports:
    - bool
    - tuple[bool, str | None]
    """
    if isinstance(result, tuple):
        return result

    if result is True:
        return True, None

    return False, "Username already exists or an unexpected database error occurred."


def welcome_page():
    """Render improved welcome page UI."""
    _hide_sidebar()

    with open("styles/auth.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
    <div class="centered-title">
        <h1>COMP201 Software Engineering Learning Hub</h1>
        <p>
            Welcome to an interactive study platform designed to support software engineering revision 
            through quizzes, flashcards, AI support, progress tracking, and learning activities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="centered-info">
        Create an account or log in to start tracking your learning progress.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-title">
        🚀 What you can do
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">AI Tutor</div>
            <div class="feature-desc">Ask questions and get instant explanations</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Flashcards</div>
            <div class="feature-desc">Revise key topics using active recall</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Quizzes</div>
            <div class="feature-desc">Test your understanding and track results</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Mini Games</div>
            <div class="feature-desc">Learn through interactive activities</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Log in", use_container_width=True):
            _set_view("login")

    with col2:
        if st.button("Create account", use_container_width=True):
            _set_view("signup")

def login_page():
    """Render the login form."""
    _hide_sidebar()

    st.title("Log in")
    st.caption("Enter your username and password to continue.")

    if st.button("← Back", key="back_from_login"):
        _set_view("welcome")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Log in", use_container_width=True, key="login_btn"):
        user = authenticate(username.strip(), password)

        if not user:
            st.error("Invalid username or password.")
            st.stop()

        _login_user(user)
        st.success(f"Welcome, {user['username']}!")
        st.rerun()

    st.markdown("---")
    if st.button(
        "Don’t have an account? Create one now",
        use_container_width=True,
        key="go_signup",
    ):
        _set_view("signup")


def signup_page():
    """Render the signup form."""
    _hide_sidebar()

    st.title("Create account")
    st.caption("Create a student account to access the learning tools.")

    if st.button("← Back", key="back_from_signup"):
        _set_view("welcome")

    new_user = st.text_input("New username", key="new_user")
    new_pass = st.text_input("New password", type="password", key="new_pass")
    new_pass2 = st.text_input("Confirm password", type="password", key="new_pass2")

    if st.button("Create account", use_container_width=True, key="create_btn"):
        username = new_user.strip()

        if not username:
            st.error("Please enter a username.")
            st.stop()

        if len(new_pass) < 6:
            st.error("Password should be at least 6 characters.")
            st.stop()

        if new_pass != new_pass2:
            st.error("Passwords do not match.")
            st.stop()

        result = create_user(username, new_pass, role="student")
        ok, message = _handle_create_user_result(result)

        if not ok:
            st.error(message or "Could not create account.")
            st.stop()

        st.success("Account created successfully. Please log in.")
        _set_view("login")

    st.markdown("---")
    if st.button(
        "Already have an account? Log in",
        use_container_width=True,
        key="go_login",
    ):
        _set_view("login")


def require_login():
    """Show authentication pages until the user is logged in."""
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


def logout_button():
    """Render logout controls in the sidebar for authenticated users."""
    if st.session_state.get("user"):
        with st.sidebar:
            st.markdown("---")
            st.write(f"👤 **{st.session_state['user']['username']}**")
            if st.button("Logout", use_container_width=True):
                _logout_user()
                st.rerun()