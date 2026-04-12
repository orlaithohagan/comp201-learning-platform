# games/MiniGames.py
import streamlit as st
from games.requirement_rush import play_requirement_rush, reset_requirement_rush
from games.use_case_scramble import play_use_case_scramble

def run_games_hub():
    # Which screen are we on? (hub or a specific game)
    if "view" not in st.session_state:
        st.session_state.view = "hub"

    # If we're in a specific game, jump straight there
    if st.session_state.view == "requirement_rush":
        play_requirement_rush()
        return

    if st.session_state.view == "use_case_scramble":
        play_use_case_scramble()
        return
    

    # ---------- HUB SCREEN ----------
    st.title("Mini Games Hub")
    st.caption("Reinforce COMP201 concepts with interactive mini-games.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Requirement Rush")
        st.write("Classify each requirement as Functional or Non-functional.")
        start_rr = st.button("Play Requirement Rush", key="btn_rr")

    with col2:
        st.markdown("### Use Case Scramble")
        st.write("Drag and drop steps into the correct order.")
        start_ucs = st.button("Play Use Case Scramble", key="btn_ucs")


    st.write("---")

    if start_rr:
        reset_requirement_rush()             
        st.session_state.view = "requirement_rush"
        st.rerun()
    
    if start_ucs:
        st.session_state.view = "use_case_scramble"
        st.rerun()


