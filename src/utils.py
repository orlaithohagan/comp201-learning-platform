from pathlib import Path


def load_css(*files):
    css = ""
    for file in files:
        path = Path(file)
        if path.exists():
            css += path.read_text(encoding="utf-8") + "\n"
    return css