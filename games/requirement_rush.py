import time
import streamlit as st
from streamlit_sortables import sort_items  # drag & drop component

# ---------------- GAME DATA ----------------

REQ_ITEMS_MASTER = [
    ("The system shall allow users to reset their password via email.", "Functional"),
    ("The system must respond to user requests within 2 seconds.", "Non-functional"),
    ("Users shall be able to view their order history.", "Functional"),
    ("The system must be available 99.9% of the time.", "Non-functional"),
    ("The system shall send a confirmation email after registration.", "Functional"),
    ("The user interface must be accessible to screen readers.", "Non-functional"),
    ("The system shall allow students to submit assignments online.", "Functional"),
    ("The application must support up to 500 concurrent users.", "Non-functional"),
]

TIME_LIMIT_SECONDS = 30  # visual “beat the clock” target


# ---------------- CSS LOADER ----------------

def load_rr_css():
    """Load Requirement Rush–specific CSS from styles/requirement_rush.css."""
    try:
        with open("styles/requirement_rush.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(
            "Could not find styles/requirement_rush.css. "
            "Requirement Rush will use default styling."
        )


# ---------------- STATE HELPERS ----------------

def init_requirement_rush_state():
    """Initialise all state needed for the drag-and-drop board."""
    ss = st.session_state

    # Map requirement text -> correct type
    if "rr_type_map" not in ss:
        ss.rr_type_map = {text: rtype for text, rtype in REQ_ITEMS_MASTER}

    # Containers for drag-and-drop (Unassigned, Functional, Non-functional)
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
    """Reset the game board to the initial state."""
    ss = st.session_state

    if "rr_type_map" not in ss:
        ss.rr_type_map = {text: rtype for text, rtype in REQ_ITEMS_MASTER}

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
    """Render and run the Requirement Rush drag-and-drop mini-game."""
    load_rr_css()
    init_requirement_rush_state()
    ss = st.session_state

    # ------- TIMER (visual only) -------
    elapsed = time.time() - ss.rr_start_time
    remaining = max(0, int(TIME_LIMIT_SECONDS - elapsed))

    # ------- TITLE / INTRO -------
    st.markdown(
        "<h2 style='text-align:center; margin-bottom:0.25rem;'>"
        "Requirement Rush – Drag & Drop Board 🎮"
        "</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#6b7280; margin-bottom:1rem;'>"
        "Drag each requirement card into <b>Functional</b> or <b>Non-functional</b>. "
        "Try to finish within 30 seconds, then click <b>Check my answers</b>!</p>",
        unsafe_allow_html=True,
    )

    # Back button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Back to Games Hub", key="rr_back"):
            ss.view = "hub"
            st.rerun()

    # ------- DRAG & DROP CONTAINERS -------
    containers = ss.rr_containers

    # This renders the actual draggable lists
    sorted_containers = sort_items(
        containers,
        multi_containers=True,
        key="rr_sortables",
    )
    ss.rr_containers = sorted_containers

    # Extract lists by header
    by_header = {c["header"]: c["items"] for c in sorted_containers}
    unassigned_items = by_header.get("Unassigned", [])
    functional_items = by_header.get("Functional", [])
    nonfunctional_items = by_header.get("Non-functional", [])

    total = len(ss.rr_type_map)
    placed = total - len(unassigned_items)

    # ------- SCOREBOARD STRIP -------
    st.markdown(
        "<div class='rr-score-row'>"
        f"<div class='rr-score-card'>"
        f"<h4>Time Goal</h4>"
        f"<div>⏱ {remaining}s left (aim)</div>"
        f"</div>"
        f"<div class='rr-score-card'>"
        f"<h4>Cards Sorted</h4>"
        f"<div>{placed} / {total} placed</div>"
        f"</div>"
        f"<div class='rr-score-card'>"
        f"<h4>Status</h4>"
        f"<div>{'Ready to check ✅' if len(unassigned_items)==0 else 'Sorting in progress…'}</div>"
        f"</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ------- CHECK / RESET CONTROLS -------
    all_assigned = len(unassigned_items) == 0

    check_col, reset_col = st.columns([2, 1])

    with check_col:
        if st.button(
            "✅ Check my answers",
            key="rr_check",
            disabled=not all_assigned,
        ):
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

    # ------- FEEDBACK / RESULTS -------
    if ss.rr_checked:
        st.markdown("### Results 🎉")
        st.write(f"You correctly classified **{ss.rr_score} / {total}** requirements.")

        if ss.rr_score == total:
            st.success("Perfect! You're a requirements pro 🤓")
            st.balloons()
        elif ss.rr_score >= total * 0.75:
            st.info("Nice work! Just a few to revise.")
        else:
            st.warning(
                "Good attempt! Revisit the differences between Functional and "
                "Non-functional requirements."
            )

        with st.expander("See detailed feedback"):
            def bucket_of(text: str) -> str:
                if text in functional_items:
                    return "Functional"
                if text in nonfunctional_items:
                    return "Non-functional"
                if text in unassigned_items:
                    return "Unassigned"
                return "Unknown"

            for text, correct_type in ss.rr_type_map.items():
                chosen = bucket_of(text)
                is_correct = (chosen == correct_type)
                icon = "✅" if is_correct else "❌"
                st.markdown(
                    f"{icon} **Your choice:** {chosen} — **Correct:** {correct_type}  \n"
                    f"> {text}"
                )

        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Play again 🧩", key="rr_play_again"):
                reset_requirement_rush()
                st.rerun()
        with c2:
            if st.button("Back to Games Hub 🏠", key="rr_back_from_results"):
                ss.view = "hub"
                st.rerun()
