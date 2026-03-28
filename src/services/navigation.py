import streamlit as st

def nav_button(label, page_path, current_page):
    if current_page == page_path:
        st.sidebar.markdown(
            f"""
            <div style="
                background-color: #1d4ed8;
                color: white;
                padding: 10px 12px;
                border-radius: 10px;
                font-weight: 700;
                margin-bottom: 6px;
            ">
                ➜ {label}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if st.sidebar.button(label, key=f"nav_{label}_{page_path}"):
            st.switch_page(page_path)


def render_sidebar_navigation(current_page):
    st.sidebar.markdown(
        "<div style='font-size:22px; font-weight:700; margin-bottom:18px;'>🎓 COMP201 Hub</div>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown("### 📚 Learn")
    nav_button("Flashcards", "pages/Flashcards.py", current_page)
    nav_button("Concept Map", "pages/ConceptMap.py", current_page)

    st.sidebar.markdown("### 🧠 Practice")
    nav_button("Quiz", "pages/Quiz.py", current_page)
    nav_button("Mini Games", "pages/MiniGames.py", current_page)

    st.sidebar.markdown("### 🤖 Support")
    nav_button("AI Tutor", "pages/AITutor.py", current_page)

    st.sidebar.markdown("### 📊 Progress")
    nav_button("Dashboard", "pages/Dashboard.py", current_page)