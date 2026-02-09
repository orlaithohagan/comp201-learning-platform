# auth_ui.py
import streamlit as st
from src.services.auth_service import authenticate, create_user

def require_login():
    if st.session_state.get("user"):
        return

    st.title("Login")

    tab1, tab2 = st.tabs(["Login", "Create account"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            user = authenticate(username, password)
            if not user:
                st.error("Invalid username or password.")
                st.stop()
            st.session_state["user"] = user
            st.success(f"Welcome, {user['username']}!")
            st.rerun()

    with tab2:
        new_user = st.text_input("New username", key="new_user")
        new_pass = st.text_input("New password", type="password", key="new_pass")
        new_pass2 = st.text_input("Confirm password", type="password", key="new_pass2")
        if st.button("Create account", use_container_width=True):
            if new_pass != new_pass2:
                st.error("Passwords do not match.")
                st.stop()
            ok = create_user(new_user, new_pass, role="student")
            if not ok:
                st.error("Username already exists (or database error).")
                st.stop()
            st.success("Account created. Go to Login tab.")
            st.stop()

    st.stop()

def logout_button():
    if st.session_state.get("user"):
        if st.button("Logout"):
            st.session_state.pop("user", None)
            st.rerun()
