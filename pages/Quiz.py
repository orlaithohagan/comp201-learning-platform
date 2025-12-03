import json
import random
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------


def load_flashcards_data() -> list:
    """
    Load questions from data/flashcards.json.
    Expects a list of objects with at least:
    id, topic, prompt, answer, (optional) distractors.
    """
    data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"

    if not data_path.exists():
        st.error(f"Could not find flashcards data at {data_path}")
        return []

    try:
        with data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse flashcards JSON: {e}")
        return []

    if not isinstance(data, list):
        st.error("flashcards.json must contain a JSON list of question objects.")
        return []

    return data


def get_topics(questions: list) -> list:
    """Return a sorted list of unique topics."""
    topics = sorted({q.get("topic", "Unknown") for q in questions})
    return topics


def prepare_quiz_questions(all_questions: list, topic: str, num_questions: int = 10) -> list:
    """
    Filter questions by topic and build a quiz:
    - Up to num_questions questions
    - Each question has 4 options (correct + 3 distractors)
    - Options are shuffled, and we store the index of the correct one
    """
    topic_questions = [q for q in all_questions if q.get("topic") == topic]

    if not topic_questions:
        return []

    random.shuffle(topic_questions)
    selected = topic_questions[:num_questions]

    quiz_questions = []

    # Build options for each question
    for q in selected:
        correct_answer = q.get("answer", "")
        distractors = q.get("distractors", [])

        # Fallback: if fewer than 3 distractors, pad with other answers from same topic
        if len(distractors) < 3:
            extra_pool = [x.get("answer", "") for x in topic_questions if x is not q]
            random.shuffle(extra_pool)
            while len(distractors) < 3 and extra_pool:
                candidate = extra_pool.pop()
                if candidate != correct_answer and candidate not in distractors:
                    distractors.append(candidate)

        # Still not enough? Just duplicate some (rare edge case, keeps quiz running)
        while len(distractors) < 3:
            distractors.append(f"Option {len(distractors) + 1}")

        options = [correct_answer] + distractors[:3]
        random.shuffle(options)
        correct_index = options.index(correct_answer)

        quiz_questions.append(
            {
                "id": q.get("id"),
                "topic": topic,
                "prompt": q.get("prompt", ""),
                "options": options,
                "correct_index": correct_index,
                "answer": correct_answer,
            }
        )

    return quiz_questions


def reset_quiz_state():
    """Clear quiz-related state (but keep the selected topic)."""
    for key in [
        "quiz_questions",
        "quiz_index",
        "quiz_answers",
        "quiz_score",
        "quiz_complete",
    ]:
        if key in st.session_state:
            del st.session_state[key]


# ---------------------------------------------------------
# Main page
# ---------------------------------------------------------


def main():
    st.set_page_config(page_title="Topic Quiz", page_icon="❓", layout="wide")

    st.title("Topic Quiz")
    st.write(
        "Each quiz is built from the questions for a single COMP201 topic. "
        "You’ll answer up to 10 questions and see your score at the end."
    )

    all_questions = load_flashcards_data()
    if not all_questions:
        return

    topics = get_topics(all_questions)
    if not topics:
        st.warning("No topics found in flashcards.json.")
        return

    # ---------------- Sidebar: topic + controls ----------------
    st.sidebar.header("Quiz Settings")

    # Default topic comes from the Flashcards page (if set)
    default_topic = st.session_state.get("quiz_topic_from_dashboard")
    if default_topic in topics:
        default_index = topics.index(default_topic)
    else:
        default_index = 0

    selected_topic = st.sidebar.selectbox(
        "Choose a topic",
        topics,
        index=default_index,
    )

    # Start / restart quiz button
    if st.sidebar.button("Start / Restart Quiz"):
        reset_quiz_state()
        st.session_state.quiz_topic_from_dashboard = selected_topic  # remember last topic
        st.session_state.quiz_questions = prepare_quiz_questions(
            all_questions, selected_topic, num_questions=10
        )
        st.session_state.quiz_index = 0
        st.session_state.quiz_answers = []
        st.session_state.quiz_score = 0
        st.session_state.quiz_complete = False

    # ---------------- Main content: quiz or instructions ----------------
    quiz_questions = st.session_state.get("quiz_questions", [])
    quiz_index = st.session_state.get("quiz_index", 0)
    quiz_complete = st.session_state.get("quiz_complete", False)

    if not quiz_questions and not quiz_complete:
        st.info("Choose a topic in the sidebar and click **Start / Restart Quiz** to begin.")
        return

    if quiz_complete:
        show_quiz_results()
    else:
        show_current_question(quiz_questions, quiz_index)


def show_current_question(quiz_questions: list, quiz_index: int):
    """Render the current quiz question and handle answer submission."""
    total_questions = len(quiz_questions)
    if total_questions == 0:
        st.warning("No quiz questions available for this topic.")
        return

    question = quiz_questions[quiz_index]

    st.subheader(
        f"Question {quiz_index + 1} of {total_questions} "
        f"· Topic: {question.get('topic', 'Unknown')}"
    )

    st.write(question["prompt"])

    # Simple progress bar
    st.progress((quiz_index) / total_questions)

    # Use a unique key per question so Streamlit remembers choices
    radio_key = f"quiz_q_{quiz_index}"
    selected_option = st.radio(
        "Choose one answer:",
        question["options"],
        index=None,
        key=radio_key,
    )

    is_last = quiz_index == total_questions - 1
    button_label = "Finish quiz" if is_last else "Next question"

    if st.button(button_label):
        if selected_option is None:
            st.warning("Please select an answer before continuing.")
            return

        # Store the chosen option index
        option_index = question["options"].index(selected_option)

        answers = st.session_state.get("quiz_answers", [])
        if len(answers) <= quiz_index:
            answers.append(option_index)
        else:
            answers[quiz_index] = option_index
        st.session_state.quiz_answers = answers

        if is_last:
            # Compute final score
            score = 0
            for i, q in enumerate(quiz_questions):
                if i < len(answers) and answers[i] == q["correct_index"]:
                    score += 1

            st.session_state.quiz_score = score
            st.session_state.quiz_complete = True
        else:
            st.session_state.quiz_index = quiz_index + 1
        st.rerun()


def show_quiz_results():
    """Display final score and per-question feedback."""
    quiz_questions = st.session_state.get("quiz_questions", [])
    answers = st.session_state.get("quiz_answers", [])
    score = st.session_state.get("quiz_score", 0)

    total = len(quiz_questions)
    if total == 0:
        st.warning("No questions were in this quiz.")
        return

    st.subheader("Quiz complete! 🎉")

    st.write(f"**Your score:** {score} / {total}")
    st.progress(score / total)

    # Simple breakdown
    st.markdown("### Review")
    for i, q in enumerate(quiz_questions):
        user_choice_index = answers[i] if i < len(answers) else None
        correct_index = q["correct_index"]

        if user_choice_index == correct_index:
            result_text = "✅ Correct"
        elif user_choice_index is None:
            result_text = "⚠️ No answer selected"
        else:
            result_text = "❌ Incorrect"

        st.markdown(f"**Q{i + 1}. {q['prompt']}**")
        st.write(result_text)
        st.write(f"- **Correct answer:** {q['options'][correct_index]}")
        if user_choice_index is not None and user_choice_index != correct_index:
            st.write(f"- **Your answer:** {q['options'][user_choice_index]}")
        st.write("---")

    if st.button("Take quiz again"):
        reset_quiz_state()
        st.rerun()


if __name__ == "__main__":
    main()
