import streamlit as st
import json
from pathlib import Path

#Page Configuration
st.set_page_config(page_title="Flashcards", page_icon=":books:", layout="centered")
st.title("Flashcard & Quizzes Dashboard")

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
    return sorted({c.get("topic") for c in flashcards_data if c.get("topic")})

def cards_for(topic: str):
    return [c for c in flashcards_data if c.get("topic") == topic]

#Mode State
if "mode" not in st.session_state:
    st.session_state.mode = "dashboard"
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "flashcard_index" not in st.session_state:
    st.session_state.flashcard_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

#Dashboard rendering
def render_dashboard():
    st.subheader("Revision Topics:")
    topics = list_topics()
    if not topics:
        st.info("No revision topics available.")
        return

    for topic in topics:
        col_topic, col_study, col_quiz = st.columns([6, 2, 2])
        with col_topic:
            st.write(f"**{topic}**")
        with col_study:
            if st.button("Study", key=f"study_{topic}"):
                st.session_state.selected_topic = topic
                st.session_state.mode = "study"
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
                st.rerun()
        with col_quiz:
            st.button("Quiz", key=f"quiz_{topic}")

#Study Mode Rendering
def render_study():
    topic = st.session_state.selected_topic
    flashcards = cards_for(topic)

    top_bar = st.columns([1, 6])
    with top_bar[0]:
        if st.button("← Back"):
            st.session_state.mode = "dashboard"
            st.rerun()
    with top_bar[1]:
        st.header(f"Studying Topic: {topic}")

    if not flashcards:
        st.info("No flashcards available for this topic.")
        return

    idx = st.session_state.flashcard_index
    show_answer = st.session_state.show_answer
    card = flashcards[idx]

    q = card.get("prompt", "No question available.")
    a = card.get("answer", "No answer available.")

    st.markdown(
        f"""
        <div style="
            background:#f8f9fa; padding:28px; border-radius:12px;
            box-shadow:0 2px 8px rgba(0,0,0,.06); text-align:center; font-size:18px;">
            {'<b>Answer:</b> ' + a if show_answer else '<b>Question:</b> ' + q}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("Flip Card"):
        st.session_state.show_answer = not show_answer
        st.rerun()

    col_prev, col_prog, col_next = st.columns([1, 4, 1])
    with col_prev:
        if st.button("Previous", disabled=idx == 0):
            st.session_state.flashcard_index = idx - 1
            st.session_state.show_answer = False
            st.rerun()
    with col_prog:
        st.progress((idx + 1) / len(flashcards))
        st.caption(f"Card {idx + 1} / {len(flashcards)}")
    with col_next:
        if st.button("Next", disabled=idx >= len(flashcards) - 1):
            st.session_state.flashcard_index = idx + 1
            st.session_state.show_answer = False
            st.rerun()

# Main rendering logic
if st.session_state.mode == "dashboard":
    render_dashboard()
elif st.session_state.mode == "study" and st.session_state.selected_topic:
    render_study()
else:
    st.session_state.mode = "dashboard"
    render_dashboard()
