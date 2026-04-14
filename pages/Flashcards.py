"""
Flashcards Page Module.

This module implements the Flashcards page for the COMP201 learning platform,
providing an interactive flashcard study system for reviewing course concepts.

Key features:
- Topic selection from available flashcard sets
- Interactive flashcard display with show/hide answer functionality
- Progress tracking showing studied cards and completion status
- Navigation between cards with previous/next buttons
- Session state management for study progress and current card position
- Dashboard integration showing topic progress and study statistics

"""
import streamlit as st
import json
import time, random
from pathlib import Path
from src.services.auth_ui import require_login, logout_button
from src.services.navigation import render_sidebar_navigation
from src.services.theme import apply_styles

# Set page configuration and apply styles
st.set_page_config(page_title="Flashcards", page_icon=":books:", layout="wide")
apply_styles("styles/flashcards.css")

require_login()
render_sidebar_navigation("pages/Flashcards.py")
logout_button()

st.title("Flashcards")
st.markdown(
    "<p style='color:#4b5563; margin-top:0.25rem;'>"
    "Choose a topic to start studying with interactive flashcards."
    "</p>",
    unsafe_allow_html=True,
)

# Load flashcards data from JSON file
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"
flashcards_data = []
if DATA_PATH.exists():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            flashcards_data = json.load(f)
            if not isinstance(flashcards_data, list):
                st.error("Flashcards JSON must be a list of objects.")
                flashcards_data = []
    except json.JSONDecodeError:
        st.error("Failed to parse flashcards JSON — please check the file format.")
else:
    st.warning("No flashcards data found.")


def list_topics():
    """Extract a sorted list of unique quiz topics from the flashcards data."""
    seen = set()
    topics_in_order = []
    for card in flashcards_data:
        t = card.get("topic")
        if t and t not in seen:
            seen.add(t)
            topics_in_order.append(t)
    return topics_in_order


def cards_for(topic: str):
    """Return a list of flashcards for the given topic."""
    return [c for c in flashcards_data if c.get("topic") == topic]


def card_ids(cards):
    """Generate a list of unique identifiers for the given list of cards."""
    return [c.get("id") or f"{c.get('topic','')}_{i}" for i, c in enumerate(cards)]

# Initialize session state variables for flashcard functionality
if "mode" not in st.session_state:
    st.session_state.mode = "dashboard"
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "flashcard_index" not in st.session_state:
    st.session_state.flashcard_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "stats" not in st.session_state:     
    st.session_state.stats = {}
if "review" not in st.session_state:    
    st.session_state.review = set()
if "shuffle" not in st.session_state:   
    st.session_state.shuffle = {}


def render_dashboard():
    """Render the dashboard view with a list of flashcard topics, progress bars, and study buttons."""
    st.subheader("Revision Topics")

    topics = list_topics()
    if not topics:
        st.info("No revision topics available.")
        return

    for topic in topics:
        cards = cards_for(topic)
        total = len(cards) or 1
        seen = len(st.session_state.stats.get(topic, {}).get("seen", set()))
        pct = int((seen / total) * 100)

        col_topic, col_prog, col_study = st.columns([4, 4, 2])

        with col_topic:
            st.markdown(f"<span class='topic-name'>{topic}</span>", unsafe_allow_html=True)

        with col_prog:
            st.markdown(
                f"""
                <div class="topic-progress">
                  <span style="width:{pct}%;"></span>
                </div>
                <div style="font-size:12px;margin-top:4px;color:#6b7280">
                  {seen} of {total} cards studied
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_study:
            if st.button("Study", key=f"study_{topic}"):
                st.session_state.selected_topic = topic
                st.session_state.mode = "study"
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
                st.session_state.stats.setdefault(
                    topic,
                    {"start": time.time(), "seen": set(), "flips": 0},
                )
                st.rerun()

        st.markdown("---")

def render_study():
    """Render the flashcard study view for the selected topic, with flip animation and review options."""
    topic = st.session_state.selected_topic
    all_cards = cards_for(topic)

    # Header with topic name, shuffle toggle, and review-only toggle
    top_l, top_m, top_r = st.columns([1, 5, 4])
    with top_l:
        if st.button("← Back"):
            st.session_state.mode = "dashboard"
            st.rerun()
    with top_m:
        st.subheader(f"Studying Topic: {topic}")
    with top_r:
        st.session_state.shuffle[topic] = st.toggle("Shuffle cards", value=st.session_state.shuffle.get(topic, False))
        review_only = st.toggle("Review only", value=False)

    # Filter and optionally shuffle cards based on user preferences
    cards = list(all_cards) 
    if st.session_state.shuffle.get(topic):
        random.shuffle(cards)
    if review_only:
        wanted = set(st.session_state.review)
        ids = set(card_ids(all_cards))
        cards = [c for c in cards if (c.get("id") or "") in wanted or
                 (f"{c.get('topic','')}_{all_cards.index(c)}" in wanted and c.get("id") is None)]

    if not cards:
        st.info("No flashcards available for this selection.")
        return

    # Ensure flashcard index is within bounds, then display the current card with flip animation and navigation buttons
    if st.session_state.flashcard_index >= len(cards):
        st.session_state.flashcard_index = 0
    idx = st.session_state.flashcard_index
    show_answer = st.session_state.show_answer
    card = cards[idx]

    q = card.get("prompt") or card.get("question") or "No question available."
    a = card.get("answer") or "No answer available."
    cid = card.get("id") or f"{card.get('topic','')}_{idx}"

    # Card display with flip animation
    st.markdown(
        f"""
        <div class="flip-wrap">
          <div class="flip-inner {'is-flipped' if show_answer else ''}">
            <div class="flip-face flip-front"><b>Question:</b>&nbsp;{q}</div>
            <div class="flip-face flip-back"><b>Answer:</b>&nbsp;{a}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Buttons for marking card for review and navigating between cards
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Got it! - Don't ask again.", use_container_width=True):
            st.session_state.review.discard(cid)
    with col2:
        if st.button("Review", use_container_width=True):
            st.session_state.review.add(cid)
    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation buttons and progress bar
    c_prev, c_prog, c_next, c_flip = st.columns([2, 5, 2, 2])

    st.session_state.stats.setdefault(topic, {"start": time.time(), "seen": set(), "flips": 0})
    st.session_state.stats[topic]["seen"].add(cid)

    with c_prev:
        if st.button("Previous", disabled=idx == 0, key="prev_card_btn"):
            st.session_state.flashcard_index = idx - 1
            st.session_state.show_answer = False
            st.rerun()

    with c_prog:
        total = len(cards)
        st.progress((idx + 1) / total)
        st.caption(f"Card {idx + 1} / {total}")

    with c_next:
        if st.button("Next", disabled=idx >= total - 1, key="next_card_btn"):
            st.session_state.flashcard_index = idx + 1
            st.session_state.show_answer = False
            st.rerun()

    with c_flip:
        if st.button("Flip Card", key="flip_card_btn"):
            st.session_state.show_answer = not show_answer
            st.session_state.stats.setdefault(topic, {"start": time.time(), "seen": set(), "flips": 0})
            st.session_state.stats[topic]["flips"] += 1
            st.rerun()

if st.session_state.mode == "dashboard":
    render_dashboard()
elif st.session_state.mode == "study":
    render_study()
else:
    st.session_state.mode = "dashboard"
    render_dashboard()
