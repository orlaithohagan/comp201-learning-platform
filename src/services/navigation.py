import streamlit as st

# Page paths constants
PAGES = {
    "Flashcards": "pages/Flashcards.py",
    "Concept Map": "pages/ConceptMap.py",
    "Quiz": "pages/Quiz.py",
    "Mini Games": "pages/MiniGames.py",
    "AI Tutor": "pages/AITutor.py",
    "Dashboard": "pages/Dashboard.py"
}

# Navigation sections
NAV_SECTIONS = {
    "📚 Learn": ["Flashcards", "Concept Map"],
    "🧠 Practice": ["Quiz", "Mini Games"],
    "🤖 Support": ["AI Tutor"],
    "📊 Progress": ["Dashboard"]
}


def nav_button(label, page_path, current_page):
    """
    Renders a navigation button in the sidebar.

    Args:
        label (str): The display label for the button.
        page_path (str): The path to the page to navigate to.
        current_page (str): The current page path to highlight if matching.
    """
    if current_page == page_path:
        st.sidebar.markdown(
            """
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
            """.format(label=label),
            unsafe_allow_html=True
        )
    else:
        if st.sidebar.button(label, key=f"nav_{label}_{page_path}"):
            st.switch_page(page_path)


def render_sidebar_navigation(current_page):
    """
    Renders the sidebar navigation with sections and buttons.

    Args:
        current_page (str): The current page path to highlight active button.
    """
    st.sidebar.markdown(
        "<div style='font-size:22px; font-weight:700; margin-bottom:18px;'>🎓 COMP201 Hub</div>",
        unsafe_allow_html=True
    )

    for section, items in NAV_SECTIONS.items():
        st.sidebar.markdown(f"### {section}")
        for item in items:
            nav_button(item, PAGES[item], current_page)