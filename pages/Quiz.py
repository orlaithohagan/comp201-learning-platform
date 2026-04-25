"""
Quiz Page Module.

This module implements the Quiz page for the COMP201 learning platform,
providing interactive topic-based quizzes to assess and reinforce student understanding.

Key features:
- Topic selection from available flashcard sets
- Automatic quiz generation from flashcard data (up to 10 questions per quiz)
- Multiple choice questions with answer validation
- Real-time scoring and progress tracking
- Results display with detailed feedback and correct answers
- Progress logging for dashboard analytics and learning streaks
- Session state management for quiz flow and user responses

"""

import json
import random
from pathlib import Path
import streamlit as st
from src.progress import log_quiz_attempt, log_daily_activity
from src.services.auth_ui import require_login, logout_button
from src.services.navigation import render_sidebar_navigation
from src.services.theme import apply_styles

# Set page configuration and apply styles
st.set_page_config(page_title="Topic Quiz", page_icon="❓", layout="wide")
apply_styles("styles/quiz.css")

require_login()
render_sidebar_navigation("pages/Quiz.py")
logout_button()

# Helper functions for loading flashcards, listing topics, and building quiz questions
view = st.session_state.get("quiz_view")
topic = st.session_state.get("quiz_topic")

if view == "quiz" and topic:
    st.title(f"{topic} Quiz")

elif view == "results" and topic:
    st.title(f"{topic} Results")

else:
    st.title("Choose a Topic")
    st.write(
        "Select a COMP201 topic below to begin a quiz. "
        "Each quiz contains up to 10 questions and tracks your progress."
    )

def load_flashcards():
    """Load flashcards JSON and return a list of card dicts."""
    data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"

    if not data_path.exists():
        st.error("Flashcards data file not found. Expected at `data/flashcards.json`.")
        return []

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        st.error("Could not parse `flashcards.json` – please check the file format.")
        return []

    if not isinstance(data, list):
        st.error("Flashcards JSON must be a list of objects.")
        return []

    return data

def get_topics(cards):
    """Return sorted list of unique topic names with counts."""
    topic_counts = {}
    for card in cards:
        topic = card.get("topic", "Unknown topic")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    topics = sorted(topic_counts.items(), key=lambda x: x[0])
    return topics 

def build_questions_for_topic(topic, cards, max_q=10):
    """Create a list of quiz questions for a given topic."""
    topic_cards = [c for c in cards if c.get("topic") == topic]

    if not topic_cards:
        return []

    random.shuffle(topic_cards)
    topic_cards = topic_cards[:max_q]

    questions = []
    for card in topic_cards:
        prompt = card.get("prompt", "No question text")
        correct = card.get("answer", "")

        options = [correct]
        distractors = card.get("distractors") or []
        for d in distractors:
            if isinstance(d, str) and d not in options:
                options.append(d)

        if not options:
            options = [correct]

        random.shuffle(options)

        questions.append(
            {
                "id": card.get("id"),
                "prompt": prompt,
                "correct": correct,
                "options": options,
            }
        )

    return questions

def start_quiz(topic, cards):
    """Initialise quiz state for a given topic."""
    questions = build_questions_for_topic(topic, cards)
    if not questions:
        st.warning("No questions available for this topic yet.")
        return

    st.session_state.quiz_view = "quiz"
    st.session_state.quiz_topic = topic
    st.session_state.quiz_questions = questions
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = []  # list of {prompt, correct, selected, is_correct}
    st.session_state.quiz_logged = False

def reset_quiz_state():
    """Return to the main topic list."""
    st.session_state.quiz_view = "home"
    st.session_state.quiz_topic = None
    st.session_state.quiz_questions = []
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_logged = False

# Session state initialization 
if "quiz_view" not in st.session_state:
    st.session_state.quiz_view = "home"
if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = None
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "quiz_logged" not in st.session_state:
    st.session_state.quiz_logged = False

cards = load_flashcards()
topics = get_topics(cards)


st.markdown("---")
# View logic to switch between topic list, quiz questions, and results based on session state
view = st.session_state.quiz_view

if view == "home":

    if not topics:
        st.info("No topics found in your flashcards data yet.")
    else:
        st.subheader("Choose a topic to start a quiz:")

        for topic, count in topics:
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.markdown(f"**{topic}**")
            with col2:
                st.caption(f"{count} questions available")
            with col3:
                if st.button("Start quiz", key=f"start_{topic}"):
                    start_quiz(topic, cards)
                    st.rerun()

# Display quiz questions and handle user answers, updating session state accordingly
elif view == "quiz":

    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_index
    total = len(questions)

    if not questions:
        st.warning("No questions loaded for this quiz. Returning to topic list.")
        reset_quiz_state()
        st.rerun()

    if idx >= total:
        st.session_state.quiz_view = "results"
        st.rerun()

    q = questions[idx]

    st.markdown(
        f"### Question {idx + 1} of {total} · "
        f"Topic: {st.session_state.quiz_topic}"
    )

    st.markdown(
        f"""
        <div class='quiz-question-card'>
            <div class='quiz-question-title'>{q['prompt']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress((idx) / total)

    selected = st.radio(
        "Choose one answer:",
        q["options"],
        key=f"q_{idx}",
    )

    button_label = "Next question" if idx < total - 1 else "Finish quiz"
    if st.button(button_label):
        if not selected:
            st.warning("Please choose an answer before continuing.")
        else:
            is_correct = selected == q["correct"]
            if is_correct:
                st.session_state.quiz_score += 1

            st.session_state.quiz_answers.append(
                {
                    "prompt": q["prompt"],
                    "correct": q["correct"],
                    "selected": selected,
                    "is_correct": is_correct,
                }
            )

            if idx < total - 1:
                st.session_state.quiz_index += 1
                st.rerun()
            else:
                st.session_state.quiz_view = "results"
                st.rerun()

# Display quiz results, log attempt, and offer review of questions with correct answers
elif view == "results":

    total = len(st.session_state.quiz_questions)
    score = st.session_state.quiz_score
    user_id = st.session_state.get("user_id")
    topic_name = st.session_state.get("quiz_topic")
    score_percent = round((score / total) * 100, 2) if total > 0 else 0

    # Log quiz attempt and daily activity if not already logged for this quiz session
    if user_id is not None and total > 0 and not st.session_state.quiz_logged:
        log_quiz_attempt(
            user_id=user_id,
            topic_name=topic_name,
            score=score_percent,
            total_questions=total
        )
        log_daily_activity(user_id)
        st.session_state.quiz_logged = True

    st.subheader("Quiz complete!")
    st.write(f"**Your score:** {score} / {total}")

    if total > 0:
        st.progress(score / total)

    # Offer detailed review of each question with correct answers and user's selected answers
    st.markdown("### Review")

    for i, ans in enumerate(st.session_state.quiz_answers, start=1):
        st.markdown(f"**Q{i}. {ans['prompt']}**")

        if ans["is_correct"]:
            st.success("Correct")
            st.markdown(f"- **Your answer:** {ans['selected']}")
        else:
            st.error("Incorrect")
            st.markdown(f"- **Your answer:** {ans['selected']}")
            st.markdown(f"- **Correct answer:** {ans['correct']}")
        st.markdown("---")

    if st.button("Back to all quizzes"):
        reset_quiz_state()
        st.rerun()

else:
    reset_quiz_state()
    st.rerun()
