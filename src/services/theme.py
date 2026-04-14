"""
Theme service for CSS styling and visual customisation.

Provides functions to load and apply CSS stylesheets, including main application
styles and page-specific customisations for consistent UI theming.
"""

import streamlit as st
from src.utils import load_css

def apply_styles(*page_css_files: str) -> None:
    """Load and apply CSS styles from the main stylesheet and any additional page-specific styles."""
    files = ["styles/main.css", *page_css_files]
    css = load_css(*files)
    if css:
        st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True
        )