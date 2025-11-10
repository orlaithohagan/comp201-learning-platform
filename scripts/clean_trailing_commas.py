#!/usr/bin/env python3
"""
Simple utility to remove trailing commas (before } or ]) and stray '=' lines
from a JSON-like file and rewrite it as valid JSON. Makes a .bak backup.

Usage: python scripts/clean_trailing_commas.py data/flashcards.json
"""
import sys
import re
import json
from pathlib import Path


def clean_text(text: str) -> str:
    # Remove lines that only contain = (possibly with spaces)
    text = re.sub(r"^\s*=+\s*$\n?", "", text, flags=re.MULTILINE)

    # Remove trailing commas before closing } or ]
    # This will replace ",   }" or ",\n}\n" etc. with just the closing brace
    text = re.sub(r",\s*(?=[}\]])", "", text)

    return text


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/clean_trailing_commas.py <path/to/file.json>")
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(2)

    text = p.read_text(encoding="utf-8")

    cleaned = clean_text(text)

    # Try to parse to ensure valid JSON
    try:
        obj = json.loads(cleaned)
    except Exception as e:
        print("Clean-up completed but JSON parsing still fails:", e)
        # write cleaned text to .cleaned for inspection
        p.with_suffix(p.suffix + ".cleaned").write_text(cleaned, encoding="utf-8")
        print("Wrote intermediate file:", str(p.with_suffix(p.suffix + ".cleaned")))
        sys.exit(3)

    # Backup original
    bak = p.with_suffix(p.suffix + ".bak")
    bak.write_text(text, encoding="utf-8")
    print(f"Backup saved to {bak}")

    # Write pretty JSON back
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote cleaned JSON to {p}")


if __name__ == "__main__":
    main()
