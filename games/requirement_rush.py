"""
Requirement Rush Game Module.

This module implements the "Requirement Rush" mini-game for the COMP201 learning platform.
The game helps students practice classifying software requirements as either "Functional"
or "Non-functional" by dragging and dropping requirement statements into the correct categories.

Key features:
- Loads requirements from a JSON data file
- Randomly selects up to 10 requirements per game session
- Uses drag-and-drop interface for classification
- Provides immediate feedback with scoring
- Tracks game state using Streamlit session variables
- Includes detailed feedback showing correct/incorrect classifications

The game reinforces understanding of functional vs non-functional requirements,
a key concept in software engineering requirements analysis.
"""

import json
import random
from pathlib import Path
from src.services.theme import apply_styles
import streamlit as st
from streamlit_sortables import sort_items 

# Path to requirements data and max number of requirements per game
REQ_DATA_PATH = Path("data/requirements_rush.json")
MAX_REQ_PER_GAME = 10


@st.cache_data
def load_all_requirements():
    """Load all requirements from the JSON file and return a list of (text, type) tuples."""
    with REQ_DATA_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [(item["text"], item["type"]) for item in raw]


def choose_game_requirements():
        """Select a random subset of requirements for the game, up to MAX_REQ_PER_GAME."""
        all_reqs = load_all_requirements()
        if len(all_reqs) <= MAX_REQ_PER_GAME:
            return all_reqs
        return random.sample(all_reqs, MAX_REQ_PER_GAME)


def init_requirement_rush_state():
    """Initialize session state variables for the Requirement Rush game if they don't already exist."""
    ss = st.session_state

    if "rr_type_map" not in ss:
        selected = choose_game_requirements()
        ss.rr_type_map = {text: rtype for text, rtype in selected}

    # Initialize the containers for the drag-and-drop interface
    if "rr_containers" not in ss:
        all_texts = list(ss.rr_type_map.keys())
        ss.rr_containers = [
            {"header": "Unassigned", "items": all_texts},
            {"header": "Functional", "items": []},
            {"header": "Non-functional", "items": []},
        ]

    if "rr_checked" not in ss:
        ss.rr_checked = False

    if "rr_score" not in ss:
        ss.rr_score = 0

    if "rr_board_version" not in ss:
        ss.rr_board_version = 0


def reset_requirement_rush():
    """Reset the game state for a new round of Requirement Rush."""
    ss = st.session_state

    if "rr_board_version" not in ss:
        ss.rr_board_version = 0

    selected = choose_game_requirements()
    ss.rr_type_map = {text: rtype for text, rtype in selected}

    all_texts = list(ss.rr_type_map.keys())
    ss.rr_containers = [
        {"header": "Unassigned", "items": all_texts},
        {"header": "Functional", "items": []},
        {"header": "Non-functional", "items": []},
    ]
    ss.rr_checked = False
    ss.rr_score = 0
    ss.rr_board_version += 1  

def play_requirement_rush():
    """Main function to render the Requirement Rush game interface and handle game logic."""
    st.set_page_config(page_title="Requirement Rush", page_icon="⚡")
    apply_styles("styles/requirement_rush.css")
    init_requirement_rush_state()
    ss = st.session_state

    st.title("Requirement Rush")
    st.markdown(
    "<div class='uol-info-box'><b>Drag each requirement into Functional or Non-functional.</b></div>",
    unsafe_allow_html=True,
    )

    st.caption(
        f"Each round uses a random selection of up to {MAX_REQ_PER_GAME} requirements. Then click Check my answers."
    )

    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Games Hub", key="rr_back"):
            ss.view = "hub"
            st.rerun()

    # Render the drag-and-drop interface using the current state of the containers
    containers = ss.rr_containers

    sorted_containers = sort_items(
        containers,
        multi_containers=True,
        key=f"rr_sortables_{ss.rr_board_version}",
    )
    ss.rr_containers = sorted_containers

    # Extract grouped items for easier scoring and display
    by_header = {c["header"]: c["items"] for c in sorted_containers}
    unassigned_items = by_header.get("Unassigned", [])
    functional_items = by_header.get("Functional", [])
    nonfunctional_items = by_header.get("Non-functional", [])

    # Display score and status information based on how many requirements have been sorted
    total = len(ss.rr_type_map)
    placed = total - len(unassigned_items)

    st.markdown(
        "<div class='rr-score-row'>"
        f"<div class='rr-score-card'><h4>Cards Sorted</h4><div>{placed} / {total} placed</div></div>"
        f"<div class='rr-score-card'><h4>Status</h4><div>{'Ready to check!' if len(unassigned_items)==0 else 'Sorting…'}</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Check and Reset buttons, with logic to only enable Check when all requirements have been sorted
    all_assigned = len(unassigned_items) == 0
    check_col, reset_col = st.columns([2, 1])

    with check_col:
        if st.button("Check my answers.", key="rr_check", disabled=not all_assigned):
            score = 0
            for text in functional_items:
                if ss.rr_type_map[text] == "Functional":
                    score += 1
            for text in nonfunctional_items:
                if ss.rr_type_map[text] == "Non-functional":
                    score += 1
            ss.rr_score = score
            ss.rr_checked = True

    with reset_col:
        if st.button("Reset board.", key="rr_reset"):
            reset_requirement_rush()
            st.rerun()

    # Results and feedback section, only shown after the user clicks Check my answers
    if ss.rr_checked:
        st.markdown("### Results!")
        st.write(f"You correctly classified **{ss.rr_score} / {total}** requirements.")

        if ss.rr_score == total:
            st.success("Perfect! You're a requirements pro.")
            st.balloons()
        elif ss.rr_score >= total * 0.75:
            st.info("Nice work! Just a few to revise.")
        else:
            st.warning("Good attempt! Revisit Functional vs Non-functional requirements.")

        with st.expander("See detailed feedback"):
            def bucket_of(text):
                if text in functional_items:
                    return "Functional"
                if text in nonfunctional_items:
                    return "Non-functional"
                if text in unassigned_items:
                    return "Unassigned"
                return "Unknown"

            for text, correct_type in ss.rr_type_map.items():
                chosen = bucket_of(text)
                icon = "✅" if chosen == correct_type else "❌"
                st.markdown(f"{icon} **Your choice:** {chosen} — **Correct:** {correct_type}\n\n> {text}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Play again!", key="rr_play_again"):
                reset_requirement_rush()
                st.rerun()
        with c2:
            if st.button("Back to Games Hub", key="rr_back_from_results"):
                ss.view = "hub"
                st.rerun()
