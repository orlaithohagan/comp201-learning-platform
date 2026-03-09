import streamlit as st
from src.progress import get_quiz_summary, get_recent_quiz_attempts
from src.services.auth_ui import require_login, logout_button

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

require_login()
logout_button()

def main():
    st.title("📊 User Dashboard")

    username = st.session_state.get("username")
    if username:
        st.write(f"Welcome back, **{username}**.")
    else:
        st.write("View your quiz progress and recent learning activity.")

    user_id = st.session_state.get("user_id")

    # Temporary debug check
    # st.write("DEBUG user_id:", user_id)
    # st.write("DEBUG username:", username)
    # st.write("DEBUG session keys:", list(st.session_state.keys()))


    summary = get_quiz_summary(user_id)
    recent_attempts = get_recent_quiz_attempts(user_id)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Quizzes Completed", summary["quizzes_completed"])

    with col2:
        st.metric("Average Score", f"{summary['average_score']}%")

    with col3:
        st.metric("Best Score", f"{summary['best_score']}%")

    st.markdown("---")
    st.subheader("Recent Quiz Attempts")

    if recent_attempts:
        for topic_name, score, total_questions, attempted_at in recent_attempts:
            st.markdown(
                f"""
                **Topic:** {topic_name or 'General'}  
                **Score:** {score}%  
                **Questions:** {total_questions}  
                **Date:** {attempted_at}
                """
            )
            st.markdown("---")
    else:
        st.info("No quiz attempts recorded yet.")


if __name__ == "__main__":
    main()