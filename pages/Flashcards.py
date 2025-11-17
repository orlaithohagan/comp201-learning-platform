import streamlit as st
import json
import time, random
from pathlib import Path

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
#Page Configuration
st.set_page_config(page_title="Flashcards", page_icon=":books:", layout="wide")
st.title("Flashcard & Quizzes Dashboard")

# Apply external CSS styling
css_path = Path(__file__).resolve().parents[1] / "styles" / "flashcards.css"
local_css(css_path)


#Flashcards Data Loading
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

#Helpers
def list_topics():
    seen = set()
    topics_in_order = []
    for card in flashcards_data:
        t = card.get("topic")
        if t and t not in seen:
            seen.add(t)
            topics_in_order.append(t)
    return topics_in_order

def cards_for(topic: str):
    return [c for c in flashcards_data if c.get("topic") == topic]

def card_ids(cards):
    return [c.get("id") or f"{c.get('topic','')}_{i}" for i, c in enumerate(cards)]

#Mode State
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

#Dashboard rendering
def render_dashboard():
    st.subheader("Revision Topics:")
    topics = list_topics()
    if not topics:
        st.info("No revision topics available.")
        return

    for topic in topics:
        cards = cards_for(topic)
        total = len(cards) or 1
        seen = len(st.session_state.stats.get(topic, {}).get("seen", set()))
        pct = int((seen / total) * 100)

        col_topic, col_prog, col_study, col_quiz = st.columns([4, 3, 2, 2])
        with col_topic:
            st.write(f"**{topic}**")
        with col_prog:
            # small inline progress bar
            st.markdown(
                f'<div class="topic-progress"><span style="width:{pct}%"></span></div>'
                f'<div style="font-size:12px;margin-top:4px;color:#6b7280">{seen}/{total} studied</div>',
                unsafe_allow_html=True
            )
        with col_study:
            if st.button("Study", key=f"study_{topic}"):
                st.session_state.selected_topic = topic
                st.session_state.mode = "study"
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
                # start stats timer if first time
                st.session_state.stats.setdefault(topic, {"start": time.time(), "seen": set(), "flips": 0})
                st.rerun()
        with col_quiz:
            st.button("Quiz", key=f"quiz_{topic}")  # Phase 2 placeholder


#Study Mode Rendering
def render_study():
    topic = st.session_state.selected_topic
    all_cards = cards_for(topic)

    # Controls row: Back, Shuffle, Review-only, Difficulty filter (optional)
    top_l, top_m, top_r = st.columns([1, 5, 4])
    with top_l:
        if st.button("← Back"):
            st.session_state.mode = "dashboard"
            st.rerun()
    with top_m:
        st.header(f"Studying Topic: {topic}")
    with top_r:
        st.session_state.shuffle[topic] = st.toggle("Shuffle cards", value=st.session_state.shuffle.get(topic, False))
        review_only = st.toggle("Review only", value=False)

    # Apply order/filter
    cards = list(all_cards)  # copy
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

    # Current index (bound to filtered deck length)
    if st.session_state.flashcard_index >= len(cards):
        st.session_state.flashcard_index = 0
    idx = st.session_state.flashcard_index
    show_answer = st.session_state.show_answer
    card = cards[idx]

    q = card.get("prompt") or card.get("question") or "No question available."
    a = card.get("answer") or "No answer available."
    cid = card.get("id") or f"{card.get('topic','')}_{idx}"

    # --- Flip card (animated) ---
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

    #Learning aids (CSS-centered)
    st.markdown('<div class="learning-aids">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Got it! - Don't ask again.", use_container_width=True):
            st.session_state.review.discard(cid)
    with col2:
        if st.button("Review", use_container_width=True):
            st.session_state.review.add(cid)
    st.markdown('</div>', unsafe_allow_html=True)


    # Flip + nav
    c_flip, c_prog, c_prev, c_next = st.columns([2, 5, 2, 2])
    with c_flip:
        if st.button("Flip Card"):
            st.session_state.show_answer = not show_answer
            # stats: flip count
            st.session_state.stats.setdefault(topic, {"start": time.time(), "seen": set(), "flips": 0})
            st.session_state.stats[topic]["flips"] += 1
            st.rerun()

    # stats: mark this card as seen
    st.session_state.stats.setdefault(topic, {"start": time.time(), "seen": set(), "flips": 0})
    st.session_state.stats[topic]["seen"].add(cid)

    # progress + label
    with c_prog:
        total = len(cards)
        st.progress((idx + 1) / total)
        st.caption(f"Card {idx + 1} / {total}")

    with c_prev:
        if st.button("Previous", disabled=idx == 0):
            st.session_state.flashcard_index = idx - 1
            st.session_state.show_answer = False
            st.rerun()
    with c_next:
        if st.button("Next", disabled=idx >= total - 1):
            st.session_state.flashcard_index = idx + 1
            st.session_state.show_answer = False
            st.rerun()

if st.session_state.mode == "dashboard":
    render_dashboard()
elif st.session_state.mode == "study":
    render_study()
else:
    st.session_state.mode = "dashboard"
    render_dashboard()
