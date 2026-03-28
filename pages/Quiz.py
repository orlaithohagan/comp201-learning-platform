import json
import random
from pathlib import Path
import streamlit as st
from src.progress import log_quiz_attempt, log_daily_activity
from src.services.auth_ui import require_login, logout_button
from src.services.navigation import render_sidebar_navigation
from src.services.theme import apply_styles

apply_styles("styles/quiz.css")
st.set_page_config(page_title="Topic Quiz", page_icon="❓", layout="wide")

require_login()
render_sidebar_navigation("pages/Quiz.py")
logout_button()


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
    return topics  # list of (topic, count)


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

        # Build options from answer + distractors
        options = [correct]
        distractors = card.get("distractors") or []
        for d in distractors:
            if isinstance(d, str) and d not in options:
                options.append(d)

        # Ensure we have at least one option
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


# Optional: reuse your flashcards CSS if you like
css_path = Path(__file__).resolve().parents[1] / "styles" / "flashcards.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialise session state defaults
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

st.title("Topic Quiz")
st.write(
    "Each quiz is built from the questions for a single COMP201 topic. "
    "You’ll answer up to 10 questions and see your score at the end."
)

st.markdown("---")

# ------------ Views ------------ #

view = st.session_state.quiz_view

# ---- Home view: list all topics with 'Start quiz' buttons ---- #
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

# ---- Quiz view: show current question ---- #
elif view == "quiz":

    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_index
    total = len(questions)

    if not questions:
        st.warning("No questions loaded for this quiz. Returning to topic list.")
        reset_quiz_state()
        st.rerun()

    if idx >= total:
        # Safety: if index goes out of range, show results instead
        st.session_state.quiz_view = "results"
        st.rerun()

    q = questions[idx]

    st.markdown(
        f"### Question {idx + 1} of {total} · "
        f"Topic: {st.session_state.quiz_topic}"
    )

    st.write(q["prompt"])

    # Progress bar
    st.progress((idx) / total)

    # Answer options
    selected = st.radio(
        "Choose one answer:",
        q["options"],
        key=f"q_{idx}",
    )

    # Next / finish button
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

# ---- Results view: show score + review ---- #
elif view == "results":

    total = len(st.session_state.quiz_questions)
    score = st.session_state.quiz_score

    # TEST
    # st.write("DEBUG user_id:", st.session_state.get("user_id"))

    user_id = st.session_state.get("user_id")
    topic_name = st.session_state.get("quiz_topic")
    score_percent = round((score / total) * 100, 2) if total > 0 else 0

    if user_id is not None and total > 0 and not st.session_state.quiz_logged:
        log_quiz_attempt(
            user_id=user_id,
            topic_name=topic_name,
            score=score_percent,
            total_questions=total
        )
        log_daily_activity(user_id)
        st.session_state.quiz_logged = True

    st.subheader("Quiz complete! 🎉")
    st.write(f"**Your score:** {score} / {total}")

    if total > 0:
        st.progress(score / total)

    st.markdown("### Review")

    for i, ans in enumerate(st.session_state.quiz_answers, start=1):
        st.markdown(f"**Q{i}. {ans['prompt']}**")

        if ans["is_correct"]:
            st.markdown("✅ Correct")
        else:
            st.markdown("❌ Incorrect")

        st.markdown(f"- **Correct answer:** {ans['correct']}")
        st.markdown(f"- **Your answer:** {ans['selected']}")
        st.markdown("---")

    if st.button("Back to all quizzes"):
        reset_quiz_state()
        st.rerun()

else:
    # Fallback if the view somehow gets into an unknown state
    reset_quiz_state()
    st.rerun()
