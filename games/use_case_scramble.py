# games/use_case_scramble.py
import json
import random
from pathlib import Path

import streamlit as st
from streamlit_sortables import sort_items


# More robust: build path relative to this file -> project root -> data/use_cases.json
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "use_cases.json"
CSS_PATH = PROJECT_ROOT / "styles" / "use_case_scramble.css"

def exit_use_case_scramble():
    for key in list(st.session_state.keys()):
        if key.startswith("uc_"):
            del st.session_state[key]

    st.session_state.view = "hub"
    st.rerun()


def load_css():
    """Inject the game's CSS (kept in styles/)."""
    try:
        css = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # If you forget to add the CSS file, the game still runs.
        pass


def load_use_cases():
    if not DATA_PATH.exists():
        st.error("use_cases.json not found in /data")
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def start_new_round(use_cases):
    case = random.choice(use_cases)

    correct_steps = case["steps"]
    scrambled = correct_steps[:]
    random.shuffle(scrambled)

    # Avoid accidental already-correct scramble
    if scrambled == correct_steps and len(scrambled) > 1:
        scrambled.reverse()

    st.session_state.uc_case = case
    st.session_state.uc_correct = correct_steps
    st.session_state.uc_items = scrambled
    st.session_state.uc_checked = False
    st.session_state.uc_score = None

    # IMPORTANT:
    # Changing this value forces streamlit_sortables to fully reset.
    st.session_state.uc_round_id = st.session_state.get("uc_round_id", 0) + 1


def play_use_case_scramble():
    load_css()

    st.title("Use Case Scramble ")

    st.markdown(
    "<div class='uol-info-box'><b>Drag the steps into the correct order</b></div>",
    unsafe_allow_html=True,
)
    st.markdown(
        "<div class='ucs-instructions'>"
        "Tip: drag items up/down, then click <b>Check answers</b> to see what’s correct."
        "</div>",
        unsafe_allow_html=True,
    )

    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("← Back to Games Hub"):
            exit_use_case_scramble()

    use_cases = load_use_cases()
    if not use_cases:
        return

    if "uc_case" not in st.session_state:
        start_new_round(use_cases)

    case = st.session_state.uc_case
    correct = st.session_state.uc_correct

    st.subheader(case["title"])
    st.markdown(f"**Difficulty:** {case.get('difficulty', '—')}")

    st.markdown("---")
    st.markdown("### Reorder the steps")

    # FIX for your issue:
    # Key changes every round -> the draggable list refreshes properly when you press "New use case"
    round_id = st.session_state.get("uc_round_id", 0)
    sort_key = f"use_case_sort_{round_id}"

    user_order = sort_items(
        st.session_state.uc_items,
        direction="vertical",
        key=sort_key,
    )

    st.session_state.uc_items = user_order

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check answers", key=f"ucs_check_{round_id}"):
            # Defensive scoring: handle any mismatch in lengths safely
            n = min(len(user_order), len(correct))
            score = sum(1 for i in range(n) if user_order[i] == correct[i])

            st.session_state.uc_score = score
            st.session_state.uc_checked = True

    with col2:
        if st.button(
            "New use case",
            key=f"ucs_new_{round_id}",
            disabled=not st.session_state.uc_checked
        ):
            start_new_round(use_cases)
            st.rerun()

    if not st.session_state.uc_checked:
        st.caption("Check your answers to unlock the next use case.")

    if st.session_state.uc_checked:
        st.markdown("---")
        st.markdown(
            f"<div class='ucs-score'><h3>Score: {st.session_state.uc_score} / {len(correct)}</h3></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<h3 class='ucs-feedback-title'>Feedback</h3>", unsafe_allow_html=True)

        # Per-step feedback (green if correct position, red if not)
        n = min(len(user_order), len(correct))
        for i in range(n):
            step = user_order[i]
            is_ok = (step == correct[i])

            cls = "ucs-step correct" if is_ok else "ucs-step wrong"
            icon = "✅" if is_ok else "❌"

            st.markdown(
                f"<div class='{cls}'><b>{i+1}.</b> {icon} {step}</div>",
                unsafe_allow_html=True,
            )

        with st.expander("Show correct order"):
            for i, step in enumerate(correct, start=1):
                st.write(f"{i}. {step}")
