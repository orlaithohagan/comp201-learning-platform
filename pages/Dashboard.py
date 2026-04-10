import streamlit as st
import pandas as pd
import json
import altair as alt
from datetime import datetime
from pathlib import Path
from src.progress import get_quiz_summary, get_recent_quiz_attempts, get_topic_progress, get_attempted_topics, get_quiz_attempts_for_topic, get_learning_streak, get_leaderboard
from src.services.navigation import render_sidebar_navigation
from src.services.auth_ui import require_login, logout_button
from src.gamification import BADGES, get_user_badges
from src.services.theme import apply_styles

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

apply_styles("styles/dashboard.css")
require_login()
render_sidebar_navigation("pages/Dashboard.py")
logout_button()

def get_all_quiz_topics():
    data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"

    if not data_path.exists():
        return []

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topics = sorted({card.get("topic") for card in data if card.get("topic")})
    return topics

def render_badge_card(badge, earned_badges):
    earned = badge["id"] in earned_badges

    icon = "🏅" if earned else "🔒"
    status = "Unlocked" if earned else "Locked"
    state_class = "badge-earned" if earned else "badge-locked"

    st.markdown(
        f"""
        <div class="badge-card {state_class}">
            <div class="badge-title">{icon} {badge['name']}</div>
            <div class="badge-description">{badge['description']}</div>
            <div class="badge-status">{status}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    st.title("📊 User Dashboard")
    tab1, tab2 = st.tabs(["My Progress", "Leaderboard"])
    with tab1:
        username = st.session_state.get("username")
        if username:
            st.write(f"Welcome back, **{username}**.")
        else:
            st.write("View your quiz progress and recent learning activity.")

        st.caption("Track your quiz results, topic mastery, and recent learning activity.")

        user_id = st.session_state.get("user_id")

        summary = get_quiz_summary(user_id)
        recent_attempts = get_recent_quiz_attempts(user_id)
        topic_progress = get_topic_progress(user_id)
        weak_topics = [t for t in topic_progress if (t[1] or 0) < 40]

        attempted_topics = get_attempted_topics(user_id)
        all_topics = get_all_quiz_topics()
        untested_topics = [topic for topic in all_topics if topic not in attempted_topics]

        completed_count = len(attempted_topics)
        total_topics = len(all_topics)
        progress_percent = int((completed_count / total_topics) * 100) if total_topics > 0 else 0
        learning_streak = get_learning_streak(user_id) 
        leaderboard = get_leaderboard()

        best_topic_score = max(
            [abs(round(avg_score or 0)) for _, avg_score in topic_progress],
            default=0
        )

        user_stats = {
            "quizzes_completed": summary["quizzes_completed"],
            "streak": learning_streak,
            "best_topic_score": best_topic_score,
            "topics_attempted": completed_count
        }

        earned_badges = get_user_badges(user_stats)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Quizzes Completed", summary["quizzes_completed"])

        with col2:
            st.metric("Average Score", f"{summary['average_score']}%")

        with col3:
            st.metric("Best Score", f"{summary['best_score']}%")

        st.markdown("---")
        st.subheader("🔥 Learning Streak")

        if learning_streak > 0:
            st.success(f"You are on a {learning_streak}-day learning streak!")
        else:
            st.info("No learning streak yet. Complete a quiz today to start one.")


        st.markdown("---")
        st.subheader("🏆 Achievements")

        cols = st.columns(2)

        for i, badge in enumerate(BADGES):
            with cols[i % 2]:
                render_badge_card(badge, earned_badges)

        st.markdown("---")
        st.subheader("📘 Course Progress")

        st.write(f"{completed_count} / {total_topics} Topics Attempted")
        st.progress(progress_percent / 100)
        st.caption(f"{progress_percent}% of course topics attempted")

        st.markdown("---")
        st.subheader("Topic Mastery")

        if topic_progress:
            for topic_name, avg_score in topic_progress:
                score_value = abs(round(avg_score or 0))

                col1, col2 = st.columns([5, 1])

                with col1:
                    if score_value >= 70:
                        st.success(f"{topic_name} — {score_value}% (Mastered)")
                    elif score_value >= 40:
                        st.warning(f"{topic_name} — {score_value}% (In Progress)")
                    else:
                        st.error(f"{topic_name} — {score_value}% (Needs Revision)")

                with col2:
                    if score_value < 40:
                        if st.button("Get Help using AI Tutor", key=f"ask_tutor_{topic_name}"):
                            st.session_state["tutor_prefill"] = topic_name
                            st.switch_page("pages/AITutor.py")
        else:
            st.info("No topic mastery data available yet.")

        st.markdown("---")
        st.subheader("Quiz Performance by Topic")
        st.caption("Only topics with at least one completed quiz attempt are shown.")

        if attempted_topics:
            selected_chart_topic = st.selectbox("Select a topic",options=attempted_topics)

            topic_attempts = get_quiz_attempts_for_topic(user_id, selected_chart_topic)

            if topic_attempts:
                chart_df = pd.DataFrame(
                    topic_attempts,
                    columns=["Score", "Attempted At"]
                )

                chart_df["Score"] = chart_df["Score"].abs().round().astype(int)
                chart_df["Attempt Number"] = range(1, len(chart_df) + 1)

                chart = (
                    alt.Chart(chart_df)
                    .mark_bar()
                    .encode(
                        x=alt.X("Attempt Number:O", title="Attempt", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("Score:Q", title="Score (%)", scale=alt.Scale(domain=[0, 100])),
                        tooltip=["Attempt Number", "Score", "Attempted At"]
                    )
                    .properties(width=600, height=300)
                )

                st.altair_chart(chart, width = "stretch")
            else:
                st.info("No quiz attempts available for this topic yet.")
        else:
            st.info("No quiz topics have been attempted yet.")
        
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
        else:
            st.info("No quiz attempts recorded yet.")
        
        st.markdown("---")
        st.subheader("📌 Suggested Next Step")

        if untested_topics:
            st.info("You haven't attempted these topics yet. Try one of them next:")

            for topic in untested_topics[:3]:
                st.write(f"• **{topic}**")

        elif weak_topics:
            weakest_topic = min(weak_topics, key=lambda x: x[1] or 0)
            topic_name, score = weakest_topic

            st.warning(
                f"You should revisit **{topic_name}**. "
                f"Your current average score is {round(abs(score or 0))}%."
            )

        else:
            st.success(
                "Great progress! You have attempted all topics and have no major weak areas right now."
            )

    with tab2:
        st.subheader("🏆 Leaderboard")
        st.caption("Compare quiz performance across all users.")

        if leaderboard:
            current_user = st.session_state.get("username")
            leaderboard_df = pd.DataFrame(
                leaderboard,
                columns=["Username", "Average Score (%)", "Quizzes Completed"]
            )

            leaderboard_df["Average Score (%)"] = leaderboard_df["Average Score (%)"].round(2)
            leaderboard_df.insert(0, "Rank", range(1, len(leaderboard_df) + 1))
            medals = ["🥇", "🥈", "🥉"]
            leaderboard_df["Rank"] = leaderboard_df["Rank"].apply(lambda x: medals[x - 1] if x <= 3 else x)

            if current_user in leaderboard_df["Username"].values:
                user_row = leaderboard_df[leaderboard_df["Username"] == current_user]
                user_rank = user_row.index[0] + 1
                st.info(f"You are currently ranked **#{user_rank}** on the leaderboard.")

            st.dataframe(leaderboard_df, width="stretch", hide_index=True)
        else:
            st.info("No leaderboard data available yet.")



if __name__ == "__main__":
    main()