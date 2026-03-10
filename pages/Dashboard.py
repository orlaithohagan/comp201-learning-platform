import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from src.progress import get_quiz_summary, get_recent_quiz_attempts, get_topic_progress, get_quiz_scores_over_time, get_attempted_topics
from src.services.auth_ui import require_login, logout_button

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

require_login()
logout_button()

def get_all_quiz_topics():
    data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"

    if not data_path.exists():
        return []

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topics = sorted({card.get("topic") for card in data if card.get("topic")})
    return topics

def main():
    st.title("📊 User Dashboard")

    username = st.session_state.get("username")
    if username:
        st.write(f"Welcome back, **{username}**.")
    else:
        st.write("View your quiz progress and recent learning activity.")

    st.caption("Track your quiz results, topic mastery, and recent learning activity.")
    st.write("")

    user_id = st.session_state.get("user_id")

    summary = get_quiz_summary(user_id)
    recent_attempts = get_recent_quiz_attempts(user_id)
    topic_progress = get_topic_progress(user_id)
    score_history = get_quiz_scores_over_time(user_id)

    attempted_topics = get_attempted_topics(user_id)
    all_topics = get_all_quiz_topics()
    untested_topics = [topic for topic in all_topics if topic not in attempted_topics]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Quizzes Completed", summary["quizzes_completed"])

    with col2:
        st.metric("Average Score", f"{summary['average_score']}%")

    with col3:
        st.metric("Best Score", f"{summary['best_score']}%")

    st.markdown("---")
    st.subheader("Topic Progress")

    if topic_progress:
        for topic_name, avg_score in topic_progress:
            score_value = abs(round(avg_score or 0))
            st.write(f"**{topic_name}** — {score_value}%")
            st.progress(score_value / 100)
    else:
        st.info("No topic progress recorded yet.")

    st.markdown("---")
    st.subheader("Quiz Performance Over Time")

    if score_history:

        attempts = list(range(1, len(score_history) + 1))
        scores = [abs(row[1]) for row in score_history]

        chart_df = pd.DataFrame({
            "Attempt": attempts,
            "Score (%)": scores
        })

        st.line_chart(chart_df.set_index("Attempt"))

    else:
        st.info("No quiz history available yet.")
    
    st.markdown("---")
    st.subheader("Recent Quiz Attempts")

    if recent_attempts:
        for topic_name, score, total_questions, attempted_at in recent_attempts:
            score_value = abs(round(score or 0))
            formatted_date = datetime.strptime(attempted_at, "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y – %H:%M")

            st.markdown(
                f"""
                **Topic:** {topic_name or 'General'}  
                **Score:** {score_value}%  
                **Questions:** {total_questions}  
                **Date:** {formatted_date}
                """
            )
            st.markdown("---")
    else:
        st.info("No quiz attempts recorded yet.")
    
    st.markdown("---")
    st.subheader("Topics Needing Revision")

    weak_topics = [t for t in topic_progress if (t[1] or 0) < 40]

    if weak_topics:
        for topic_name, score in weak_topics:
            st.write(f"⚠ **{topic_name}** — {round(abs(score or 0))}%")
    else:
        st.success("Great work! No weak topics detected.")

    st.markdown("---")
    st.subheader("Topics Not Yet Tested")

    if untested_topics:
        for topic in untested_topics:
            st.info(topic)
    else:
        st.success("Great work! You have attempted quizzes for all available topics.")


if __name__ == "__main__":
    main()