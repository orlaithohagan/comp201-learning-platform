"""
Utility helpers for the COMP201 app.

Provides common helper functions used across the application, such as loading
CSS files for page styling.
"""

from pathlib import Path

def load_css(*files):
    """Load one or more CSS files and concatenate their contents.

    Args:
        *files: Paths to CSS files to read.

    Returns:
        A single string containing the contents of all existing CSS files,
        separated by newlines.
    """
    css = ""
    for file in files:
        path = Path(file)
        if path.exists():
            css += path.read_text(encoding="utf-8") + "\n"
    return css