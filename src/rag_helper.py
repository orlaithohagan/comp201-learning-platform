import json
import re
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "how", "why", "when",
    "this", "that", "these", "those", "it", "in", "on", "of", "for", "to", "and",
    "or", "me", "give", "explain", "summarise", "summary", "topic", "about",
    "please", "can", "could", "would", "tell", "some", "sample", "question",
    "questions", "provide", "with", "from", "into", "using", "asked", "ask"
}


def load_flashcards():
    data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"

    if not data_path.exists():
        return []

    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_keywords(text: str):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]


def get_relevant_flashcards(question: str, max_results: int = 3):
    flashcards = load_flashcards()
    keywords = extract_keywords(question)

    if not keywords:
        return []

    scored_cards = []

    for card in flashcards:
        topic = str(card.get("topic", "")).strip()
        prompt = str(card.get("prompt", "")).strip()
        answer = str(card.get("answer", "")).strip()
        tags = " ".join(card.get("tags", []))

        combined_text = f"{topic} {prompt} {answer} {tags}".lower()

        score = 0
        matched_keywords = []

        for keyword in keywords:
            if keyword in combined_text:
                score += 1
                matched_keywords.append(keyword)

        # keep only stronger matches
        if score >= 2:
            scored_cards.append(
                {
                    "topic": topic,
                    "prompt": prompt,
                    "answer": answer,
                    "score": score,
                    "matched_keywords": matched_keywords,
                }
            )

    scored_cards.sort(key=lambda x: x["score"], reverse=True)
    return scored_cards[:max_results]


def build_context_from_flashcards(question: str, max_results: int = 3):
    relevant_cards = get_relevant_flashcards(question, max_results=max_results)

    if not relevant_cards:
        return "", []

    context_parts = []
    for i, card in enumerate(relevant_cards, start=1):
        context_parts.append(
            f"""Course Material {i}
            Topic: {card['topic']}
            Prompt: {card['prompt']}
            Answer: {card['answer']}"""
        )

    context = "\n\n".join(context_parts)
    return context, relevant_cards