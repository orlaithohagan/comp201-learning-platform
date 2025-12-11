# games/MiniGames.py
import streamlit as st
from games.requirement_rush import play_requirement_rush, reset_requirement_rush


def run_games_hub():
    # Which screen are we on? (hub or a specific game)
    if "view" not in st.session_state:
        st.session_state.view = "hub"

    # If we're in a specific game, jump straight there
    if st.session_state.view == "requirement_rush":
        play_requirement_rush()
        return

    # ---------- HUB SCREEN ----------
    st.title("Mini Games Hub 🎮")
    st.caption("Reinforce COMP201 concepts with interactive mini-games.")

    col1, col2, col3 = st.columns(3)

    # === Requirement Rush card ===
    with col1:
        st.markdown("### Requirement Rush")
        st.write("Classify each requirement as Functional or Non-functional.")
        start_rr = st.button("Play Requirement Rush", key="btn_rr")

    # === Use Case Scramble placeholder ===
    with col2:
        st.markdown("### Use Case Scramble")
        st.write("Coming soon...")
        st.button("Locked", disabled=True, key="btn_locked_ucs")

    # === Design Detective placeholder ===
    with col3:
        st.markdown("### Design Detective")
        st.write("Coming soon...")
        st.button("Locked", disabled=True, key="btn_locked_dd")

    st.write("---")

    # If player clicks Play, reset game state and go to full-screen game view
    if start_rr:
        reset_requirement_rush()              # start a fresh run
        st.session_state.view = "requirement_rush"
        st.rerun()
