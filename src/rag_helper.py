"""
Retrieval helper for selecting COMP201 flashcards relevant to a user's question.

Provides keyword extraction, flashcard loading, and relevance scoring to build a
context string used for retrieval-augmented generation (RAG) in the AI tutor.
"""

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

SE_KEYWORDS = [
    "software", "engineering", "requirements", "requirements engineering",
    "functional", "non-functional", "agile", "waterfall", "scrum",
    "use case", "uml", "testing", "verification", "validation",
    "design", "architecture", "maintenance", "modelling", "stakeholder"
]

PHRASE_KEYWORDS = [
    "use case",
    "requirements engineering",
    "functional requirements",
    "non-functional requirements",
    "software testing",
    "software design",
]

def load_flashcards():
    # Load flashcards from the project's data file and return them as JSON.
    data_path = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"
    if not data_path.exists():
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_software_engineering_query(question: str) -> bool:
    # Check whether the user question contains software engineering terms.

    q = question.lower()
    return any(keyword in q for keyword in SE_KEYWORDS)


def extract_keywords(text: str):
    # Extract meaningful keywords and key phrases from the input text.
    # This removes common stopwords and keeps important terms for matching.

    text_lower = text.lower()
    phrases = [phrase for phrase in PHRASE_KEYWORDS if phrase in text_lower]
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text_lower)
    filtered_words = [w for w in words if w not in STOPWORDS]
    return list(dict.fromkeys(phrases + filtered_words))


def get_relevant_flashcards(question: str, max_results: int = 3):
    # Score flashcards against the question and return the best matches.
    # Only flashcards with enough relevant keyword matches are kept.

    if not is_software_engineering_query(question):
        return []

    flashcards = load_flashcards()
    keywords = extract_keywords(question)

    if not keywords:
        return []

    scored_cards = []

    for card in flashcards:
        topic = str(card.get("topic", "")).strip().lower()
        prompt = str(card.get("prompt", "")).strip().lower()
        answer = str(card.get("answer", "")).strip().lower()
        tags = " ".join(card.get("tags", [])).lower()

        score = 0
        matched_keywords = []

        for keyword in keywords:
            matched = False

            if keyword in topic:
                score += 3
                matched = True
            if keyword in prompt:
                score += 2
                matched = True
            if keyword in tags:
                score += 2
                matched = True
            if keyword in answer:
                score += 1
                matched = True

            if matched:
                matched_keywords.append(keyword)

        if score >= 3:
            scored_cards.append(
                {
                    "topic": card.get("topic", ""),
                    "prompt": card.get("prompt", ""),
                    "answer": card.get("answer", ""),
                    "score": score,
                    "matched_keywords": list(set(matched_keywords)),
                }
            )

    scored_cards.sort(key=lambda x: x["score"], reverse=True)
    return scored_cards[:max_results]


def build_context_from_flashcards(question: str, max_results: int = 3):
    # Convert the top matching flashcards into a single text block for the AI tutor.

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