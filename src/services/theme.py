import streamlit as st
from src.utils import load_css


def apply_styles(*page_css_files):
    files = ["styles/main.css", *page_css_files]
    st.markdown(
        f"<style>{load_css(*files)}</style>",
        unsafe_allow_html=True
    )