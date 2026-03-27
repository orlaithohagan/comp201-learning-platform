import json
import re
from pathlib import Path


def load_flashcards():
    data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"

    if not data_path.exists():
        return []

    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_relevant_flashcards(question: str, max_results: int = 5):
    flashcards = load_flashcards()

    question_words = set(re.findall(r"\b\w+\b", question.lower()))
    scored_cards = []

    for card in flashcards:
        prompt = str(card.get("prompt", "")).strip()
        answer = str(card.get("answer", "")).strip()
        tags = " ".join(card.get("tags", []))
        topic = str(card.get("topic", "")).strip()

        combined_text = f"{topic} {prompt} {answer} {tags}".lower()

        score = 0

        for word in question_words:
            if word in combined_text:
                score += 1

        if score > 0:
            scored_cards.append(
                {
                    "topic": card.get("topic", ""),
                    "prompt": prompt,
                    "answer": answer,
                    "score": score,
                }
            )

    scored_cards.sort(key=lambda x: x["score"], reverse=True)
    return scored_cards[:max_results]


def build_context_from_flashcards(question: str, max_results: int = 5):
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