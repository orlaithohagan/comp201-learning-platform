# import json
# import random
# from pathlib import Path

# import streamlit as st

# # ---------------------------------------------------------
# # Basic helpers
# # ---------------------------------------------------------


# def load_flashcards_data() -> list:
#     """
#     Load questions from data/flashcards.json.
#     Expects a list of objects with at least:
#     id, topic, prompt, answer, (optional) distractors.
#     """
#     data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"

#     if not data_path.exists():
#         st.error(f"Could not find flashcards data at {data_path}")
#         return []

#     try:
#         with data_path.open("r", encoding="utf-8") as f:
#             data = json.load(f)
#     except json.JSONDecodeError as e:
#         st.error(f"Failed to parse flashcards JSON: {e}")
#         return []

#     if not isinstance(data, list):
#         st.error("flashcards.json must contain a JSON list of question objects.")
#         return []

#     return data


# def get_topics(questions: list) -> list:
#     """Return a sorted list of unique topics."""
#     topics = sorted({q.get("topic", "Unknown") for q in questions})
#     return topics


# def prepare_quiz_questions(all_questions: list, topic: str, num_questions: int = 10) -> list:
#     """
#     Filter questions by topic and build a quiz:
#     - Up to num_questions questions
#     - Each question has 4 options (correct + 3 distractors)
#     - Options are shuffled, and we store the index of the correct one
#     """
#     topic_questions = [q for q in all_questions if q.get("topic") == topic]

#     if not topic_questions:
#         return []

#     random.shuffle(topic_questions)
#     selected = topic_questions[:num_questions]

#     quiz_questions = []

#     # Build options for each question
#     for q in selected:
#         correct_answer = q.get("answer", "")
#         distractors = q.get("distractors", [])

#         # Fallback: if fewer than 3 distractors, pad with other answers from same topic
#         if len(distractors) < 3:
#             extra_pool = [x.get("answer", "") for x in topic_questions if x is not q]
#             random.shuffle(extra_pool)
#             while len(distractors) < 3 and extra_pool:
#                 candidate = extra_pool.pop()
#                 if candidate != correct_answer and candidate not in distractors:
#                     distractors.append(candidate)

#         # Still not enough? Just duplicate some (rare edge case, keeps quiz running)
#         while len(distractors) < 3:
#             distractors.append(f"Option {len(distractors) + 1}")

#         options = [correct_answer] + distractors[:3]
#         random.shuffle(options)
#         correct_index = options.index(correct_answer)

#         quiz_questions.append(
#             {
#                 "id": q.get("id"),
#                 "topic": topic,
#                 "prompt": q.get("prompt", ""),
#                 "options": options,
#                 "correct_index": correct_index,
#                 "answer": correct_answer,
#             }
#         )

#     return quiz_questions


# def reset_quiz_state():
#     """Clear quiz-related state (but keep the selected topic)."""
#     for key in [
#         "quiz_questions",
#         "quiz_index",
#         "quiz_answers",
#         "quiz_score",
#         "quiz_complete",
#     ]:
#         if key in st.session_state:
#             del st.session_state[key]


# # ---------------------------------------------------------
# # Main page
# # ---------------------------------------------------------


# def main():
#     st.set_page_config(page_title="Topic Quiz", page_icon="❓", layout="wide")

#     st.title("Topic Quiz")
#     st.write(
#         "Each quiz is built from the questions for a single COMP201 topic. "
#         "You’ll answer up to 10 questions and see your score at the end."
#     )

#     all_questions = load_flashcards_data()
#     if not all_questions:
#         return

#     topics = get_topics(all_questions)
#     if not topics:
#         st.warning("No topics found in flashcards.json.")
#         return

#     # ---------------- Sidebar: topic + controls ----------------
#     st.sidebar.header("Quiz Settings")

#     # Default topic comes from the Flashcards page (if set)
#     default_topic = st.session_state.get("quiz_topic_from_dashboard")
#     if default_topic in topics:
#         default_index = topics.index(default_topic)
#     else:
#         default_index = 0

#     selected_topic = st.sidebar.selectbox(
#         "Choose a topic",
#         topics,
#         index=default_index,
#     )

#     # Start / restart quiz button
#     if st.sidebar.button("Start / Restart Quiz"):
#         reset_quiz_state()
#         st.session_state.quiz_topic_from_dashboard = selected_topic  # remember last topic
#         st.session_state.quiz_questions = prepare_quiz_questions(
#             all_questions, selected_topic, num_questions=10
#         )
#         st.session_state.quiz_index = 0
#         st.session_state.quiz_answers = []
#         st.session_state.quiz_score = 0
#         st.session_state.quiz_complete = False

#     # ---------------- Main content: quiz or instructions ----------------
#     quiz_questions = st.session_state.get("quiz_questions", [])
#     quiz_index = st.session_state.get("quiz_index", 0)
#     quiz_complete = st.session_state.get("quiz_complete", False)

#     if not quiz_questions and not quiz_complete:
#         st.info("Choose a topic in the sidebar and click **Start / Restart Quiz** to begin.")
#         return

#     if quiz_complete:
#         show_quiz_results()
#     else:
#         show_current_question(quiz_questions, quiz_index)


# def show_current_question(quiz_questions: list, quiz_index: int):
#     """Render the current quiz question and handle answer submission."""
#     total_questions = len(quiz_questions)
#     if total_questions == 0:
#         st.warning("No quiz questions available for this topic.")
#         return

#     question = quiz_questions[quiz_index]

#     st.subheader(
#         f"Question {quiz_index + 1} of {total_questions} "
#         f"· Topic: {question.get('topic', 'Unknown')}"
#     )

#     st.write(question["prompt"])

#     # Simple progress bar
#     st.progress((quiz_index) / total_questions)

#     # Use a unique key per question so Streamlit remembers choices
#     radio_key = f"quiz_q_{quiz_index}"
#     selected_option = st.radio(
#         "Choose one answer:",
#         question["options"],
#         index=None,
#         key=radio_key,
#     )

#     is_last = quiz_index == total_questions - 1
#     button_label = "Finish quiz" if is_last else "Next question"

#     if st.button(button_label):
#         if selected_option is None:
#             st.warning("Please select an answer before continuing.")
#             return

#         # Store the chosen option index
#         option_index = question["options"].index(selected_option)

#         answers = st.session_state.get("quiz_answers", [])
#         if len(answers) <= quiz_index:
#             answers.append(option_index)
#         else:
#             answers[quiz_index] = option_index
#         st.session_state.quiz_answers = answers

#         if is_last:
#             # Compute final score
#             score = 0
#             for i, q in enumerate(quiz_questions):
#                 if i < len(answers) and answers[i] == q["correct_index"]:
#                     score += 1

#             st.session_state.quiz_score = score
#             st.session_state.quiz_complete = True
#         else:
#             st.session_state.quiz_index = quiz_index + 1
#         st.rerun()


# def show_quiz_results():
#     """Display final score and per-question feedback."""
#     quiz_questions = st.session_state.get("quiz_questions", [])
#     answers = st.session_state.get("quiz_answers", [])
#     score = st.session_state.get("quiz_score", 0)

#     total = len(quiz_questions)
#     if total == 0:
#         st.warning("No questions were in this quiz.")
#         return

#     st.subheader("Quiz complete! 🎉")

#     st.write(f"**Your score:** {score} / {total}")
#     st.progress(score / total)

#     # Simple breakdown
#     st.markdown("### Review")
#     for i, q in enumerate(quiz_questions):
#         user_choice_index = answers[i] if i < len(answers) else None
#         correct_index = q["correct_index"]

#         if user_choice_index == correct_index:
#             result_text = "✅ Correct"
#         elif user_choice_index is None:
#             result_text = "⚠️ No answer selected"
#         else:
#             result_text = "❌ Incorrect"

#         st.markdown(f"**Q{i + 1}. {q['prompt']}**")
#         st.write(result_text)
#         st.write(f"- **Correct answer:** {q['options'][correct_index]}")
#         if user_choice_index is not None and user_choice_index != correct_index:
#             st.write(f"- **Your answer:** {q['options'][user_choice_index]}")
#         st.write("---")

#     if st.button("Take quiz again"):
#         reset_quiz_state()
#         st.rerun()


# if __name__ == "__main__":
#     main()

import json
import random
from pathlib import Path

import streamlit as st


# ------------ Helpers ------------ #

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


def reset_quiz_state():
    """Return to the main topic list."""
    st.session_state.quiz_view = "home"
    st.session_state.quiz_topic = None
    st.session_state.quiz_questions = []
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = []


# ------------ Page setup ------------ #

st.set_page_config(page_title="Topic Quiz", page_icon="❓", layout="wide")

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
