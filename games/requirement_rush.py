import time
import json
import random
from pathlib import Path

import streamlit as st
from streamlit_sortables import sort_items  # drag & drop component

# ---------------- CONFIG ----------------

TIME_LIMIT_SECONDS = 30  # visual target (updates when Streamlit reruns)
REQ_DATA_PATH = Path("data/requirements_rush.json")
MAX_REQ_PER_GAME = 10


# ---------------- DATA LOADER ----------------

@st.cache_data
def load_all_requirements():
    with REQ_DATA_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [(item["text"], item["type"]) for item in raw]


def choose_game_requirements():
    all_reqs = load_all_requirements()
    if len(all_reqs) <= MAX_REQ_PER_GAME:
        return all_reqs
    return random.sample(all_reqs, MAX_REQ_PER_GAME)


# ---------------- CSS LOADER ----------------

def load_rr_css():
    try:
        with open("styles/requirement_rush.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Could not find styles/requirement_rush.css. Using default styling.")


# ---------------- STATE HELPERS ----------------

def init_requirement_rush_state():
    ss = st.session_state

    if "rr_type_map" not in ss:
        selected = choose_game_requirements()
        ss.rr_type_map = {text: rtype for text, rtype in selected}

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

    if "rr_start_time" not in ss:
        ss.rr_start_time = time.time()


def reset_requirement_rush():
    ss = st.session_state
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
    ss.rr_start_time = time.time()


# ---------------- MAIN GAME ----------------

def play_requirement_rush():
    load_rr_css()
    init_requirement_rush_state()
    ss = st.session_state

    # Visual timer (updates when Streamlit reruns due to interaction)
    elapsed = time.time() - ss.rr_start_time
    remaining = max(0, int(TIME_LIMIT_SECONDS - elapsed))

    st.markdown(
        "<h2 style='text-align:center; margin-bottom:0.25rem;'>"
        "Requirement Rush – Drag & Drop Board 🎮"
        "</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#6b7280; margin-bottom:1rem;'>"
        f"Drag each requirement into <b>Functional</b> or <b>Non-functional</b>. "
        f"Each round uses a random selection of up to {MAX_REQ_PER_GAME} requirements. "
        "Then click <b>Check my answers</b>.</p>",
        unsafe_allow_html=True,
    )

    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Games Hub", key="rr_back"):
            ss.view = "hub"
            st.rerun()

    containers = ss.rr_containers

    sorted_containers = sort_items(
        containers,
        multi_containers=True,
        key="rr_sortables",
    )
    ss.rr_containers = sorted_containers

    by_header = {c["header"]: c["items"] for c in sorted_containers}
    unassigned_items = by_header.get("Unassigned", [])
    functional_items = by_header.get("Functional", [])
    nonfunctional_items = by_header.get("Non-functional", [])

    total = len(ss.rr_type_map)
    placed = total - len(unassigned_items)

    st.markdown(
        "<div class='rr-score-row'>"
        f"<div class='rr-score-card'><h4>Time</h4><div>⏱ {remaining}s left (aim)</div></div>"
        f"<div class='rr-score-card'><h4>Cards Sorted</h4><div>{placed} / {total} placed</div></div>"
        f"<div class='rr-score-card'><h4>Status</h4><div>{'Ready to check ✅' if len(unassigned_items)==0 else 'Sorting…'}</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    all_assigned = len(unassigned_items) == 0
    check_col, reset_col = st.columns([2, 1])

    with check_col:
        if st.button("✅ Check my answers", key="rr_check", disabled=not all_assigned):
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
        if st.button("🔁 Reset board", key="rr_reset"):
            reset_requirement_rush()
            st.rerun()

    if ss.rr_checked:
        st.markdown("### Results 🎉")
        st.write(f"You correctly classified **{ss.rr_score} / {total}** requirements.")

        if ss.rr_score == total:
            st.success("Perfect! You're a requirements pro 🤓")
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
            if st.button("Play again 🧩", key="rr_play_again"):
                reset_requirement_rush()
                st.rerun()
        with c2:
            if st.button("Back to Games Hub 🏠", key="rr_back_from_results"):
                ss.view = "hub"
                st.rerun()
