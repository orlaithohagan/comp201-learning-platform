import streamlit as st
from src.utils import load_css


def apply_styles(*page_css_files: str) -> None:
    files = ["styles/main.css", *page_css_files]
    css = load_css(*files)
    if css:
        st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True
        )