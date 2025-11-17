from __future__ import annotations
import streamlit as st
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd

from src.quiz import (
    load_flashcards,
    list_topics,
    generate_quiz_questions,
    QuizQuestion,
    Flashcard,
)


# Session state keys used:
QS_STARTED = "quiz_started"
QS_INDEX = "current_question_index"
QS_QUESTIONS = "quiz_questions"
QS_ANSWERS = "user_answers"
QS_SCORE = "score"


def init_session_state() -> None:
    if QS_STARTED not in st.session_state:
        st.session_state[QS_STARTED] = False
    if QS_INDEX not in st.session_state:
        st.session_state[QS_INDEX] = 0
    if QS_QUESTIONS not in st.session_state:
        st.session_state[QS_QUESTIONS] = []
    if QS_ANSWERS not in st.session_state:
        st.session_state[QS_ANSWERS] = []
    if QS_SCORE not in st.session_state:
        st.session_state[QS_SCORE] = 0


def start_quiz(topic: str, flashcards: List[Flashcard], num_questions: int = 10) -> None:
    questions = generate_quiz_questions(topic, flashcards, num_questions=num_questions)
    st.session_state[QS_QUESTIONS] = questions
    st.session_state[QS_INDEX] = 0
    st.session_state[QS_ANSWERS] = [None] * len(questions)
    st.session_state[QS_SCORE] = 0
    st.session_state[QS_STARTED] = True
    # clear any per-question locks if present
    for i in range(len(questions)):
        lock_key = f"locked_{i}"
        if lock_key in st.session_state:
            del st.session_state[lock_key]
        radio_key = f"radio_{i}"
        if radio_key in st.session_state:
            # remove prior selections so radio will reflect new quiz
            del st.session_state[radio_key]


def submit_answer(index: int) -> None:
    q_key = f"radio_{index}"
    chosen = st.session_state.get(q_key, None)
    if chosen is None:
        st.warning("Please select an option before submitting.")
        return

    # lock the answer for this index
    st.session_state[f"locked_{index}"] = True
    st.session_state[QS_ANSWERS][index] = chosen

    # update score if correct
    q: QuizQuestion = st.session_state[QS_QUESTIONS][index]
    if chosen == q.correct_answer:
        # Avoid double counting if user submits more than once (shouldn't happen when locked)
        # Count only if not previously recorded as correct
        # We'll assume answers are muted once set, so increment if newly correct
        # If a previous value existed, we won't change score.
        # Here we only increment if this submit sets a previously None answer.
        # Because we store answers only once, this is safe.
        st.session_state[QS_SCORE] += 1


def go_next() -> None:
    idx = st.session_state[QS_INDEX]
    total = len(st.session_state[QS_QUESTIONS])
    if idx < total - 1:
        st.session_state[QS_INDEX] = idx + 1
    else:
        # reached the end; mark quiz as finished by setting started False but keeping questions/answers
        st.session_state[QS_STARTED] = False


def restart_quiz() -> None:
    # Reset all quiz-related session state
    keys = [QS_STARTED, QS_INDEX, QS_QUESTIONS, QS_ANSWERS, QS_SCORE]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]
    # Remove any per-question keys like radio_*/locked_*
    for key in list(st.session_state.keys()):
        if key.startswith("radio_") or key.startswith("locked_"):
            del st.session_state[key]
    init_session_state()

def main() -> None:
    st.set_page_config(page_title="Quiz Mode", layout="centered")
    st.title("Quiz Mode")

    init_session_state()

    # Load flashcards
    try:
        flashcards = load_flashcards()
    except FileNotFoundError:
        st.error("Could not find data/flashcards.json. Make sure it exists.")
        return
    except Exception as exc:
        st.error(f"Error loading flashcards: {exc}")
        return

    topics = list_topics(flashcards)
    if not topics:
        st.warning("No topics found in flashcards.json.")
        return

    # Topic selection and quiz controls
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.selectbox("Choose a topic", options=topics)
    with col2:
        num_q = st.number_input("Questions", min_value=1, max_value=50, value=10, step=1)

    # If quiz not started, show Start button
    if not st.session_state[QS_STARTED] and (not st.session_state[QS_QUESTIONS] or st.session_state[QS_INDEX] == 0):
        start_col1, start_col2 = st.columns([3, 1])
        with start_col1:
            st.write("")  # spacing
        with start_col2:
            if st.button("Start Quiz"):
                start_quiz(topic, flashcards, num_questions=int(num_q))

     # If quiz started, show current question
    if st.session_state[QS_STARTED]:
        questions: List[QuizQuestion] = st.session_state[QS_QUESTIONS]
        idx: int = st.session_state[QS_INDEX]
        total = len(questions)
        if total == 0:
            st.info("No questions available for this topic. Try another topic.")
            st.session_state[QS_STARTED] = False
            return

        q = questions[idx]
        st.markdown(f"**Question {idx + 1} of {total}**")
        st.write(q.prompt)

        # Radio key and locked key
        radio_key = f"radio_{idx}"
        locked_key = f"locked_{idx}"
        locked = st.session_state.get(locked_key, False)

        # Show options with radio buttons
        # Note: st.radio will default-select the first option. We rely on 'Submit Answer' to lock choice.
        choice = st.radio("Select one answer", options=q.options, key=radio_key, disabled=locked)

        submit_col, next_col = st.columns(2)
        with submit_col:
            if not locked:
                if st.button("Submit Answer"):
                    submit_answer(idx)
                    st.experimental_rerun()
            else:
                st.write("Answer submitted.")
        with next_col:
            if st.button("Next"):
                # Allow Next only after submission
                if not st.session_state[QS_ANSWERS][idx]:
                    st.warning("Please submit an answer before moving to the next question.")
                else:
                    go_next()
                    st.experimental_rerun()

# If quiz has been started before and is now not started (meaning finished) OR user pressed Next to finish
    if (not st.session_state[QS_STARTED]) and st.session_state[QS_QUESTIONS]:
        # Show results summary
        questions: List[QuizQuestion] = st.session_state[QS_QUESTIONS]
        answers: List[Optional[str]] = st.session_state[QS_ANSWERS]
        score: int = st.session_state[QS_SCORE]

        st.header("Quiz Results")
        st.markdown(f"Your score: **{score} / {len(questions)}**")

        # Build summary table
        rows = []
        for i, q in enumerate(questions):
            user_ans = answers[i] if i < len(answers) else None
            correct = user_ans == q.correct_answer
            rows.append(
                {
                    "Question #": i + 1,
                    "Prompt": q.prompt,
                    "Your answer": user_ans or "<no answer>",
                    "Correct answer": q.correct_answer,
                    "Correct?": "✅" if correct else "❌",
                }
            )

        df = pd.DataFrame(rows)
        # show a compact table
        st.dataframe(df[["Question #", "Your answer", "Correct answer", "Correct?"]], use_container_width=True)

        # Restart button
        if st.button("Restart Quiz"):
            restart_quiz()
            st.experimental_rerun()


if __name__ == "__main__":
    main()