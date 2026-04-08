import streamlit as st

PAGES = {
    "Flashcards": "pages/Flashcards.py",
    "Concept Map": "pages/ConceptMap.py",
    "Quiz": "pages/Quiz.py",
    "Mini Games": "pages/MiniGames.py",
    "AI Tutor": "pages/AITutor.py",
    "Dashboard": "pages/Dashboard.py",
}

NAV_SECTIONS = {
    "📚 Learn": ["Flashcards", "Concept Map"],
    "🧠 Practice": ["Quiz", "Mini Games"],
    "🤖 Support": ["AI Tutor"],
    "📊 Progress": ["Dashboard"],
}


def nav_button(label: str, page_path: str, current_page: str) -> None:
    if current_page == page_path:
        st.sidebar.markdown(
            f'<div class="sidebar-active-link">➜ {label}</div>',
            unsafe_allow_html=True,
        )
    else:
        if st.sidebar.button(label, key=f"nav_{label}_{page_path}"):
            st.switch_page(page_path)


def render_sidebar_navigation(current_page: str) -> None:
    st.sidebar.markdown(
        '<div class="sidebar-brand">🎓 COMP201 Hub</div>',
        unsafe_allow_html=True,
    )

    for section, items in NAV_SECTIONS.items():
        st.sidebar.markdown(f"### {section}")
        for item in items:
            nav_button(item, PAGES[item], current_page)