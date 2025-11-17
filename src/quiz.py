from __future__ import annotations
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

DATA_FILENAME = "flashcards.json"

@dataclass
class Flashcard:
    id: str
    topic: str
    prompt: str
    answer: str
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    distractors: Optional[List[str]] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Flashcard":
        return Flashcard(
            id=d.get("id", ""),
            topic=d.get("topic", ""),
            prompt=d.get("prompt", ""),
            answer=d.get("answer", ""),
            difficulty=d.get("difficulty"),
            tags=d.get("tags", []),
            distractors=d.get("distractors", []) or [],
        )


@dataclass
class QuizQuestion:
    flashcard_id: str
    prompt: str
    options: List[str]
    correct_answer: str


def _data_file_path() -> Path:
    # src/quiz.py -> parent is src -> parent.parent is repo root
    return Path(__file__).parent.parent / "data" / DATA_FILENAME


def load_flashcards(path: Optional[Path] = None) -> List[Flashcard]:
    """
    Load flashcards from data/flashcards.json.

    Raises:
        FileNotFoundError: if the file doesn't exist.
        json.JSONDecodeError: if the file contains invalid JSON.
    """
    file_path = path or _data_file_path()
    with file_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    if not isinstance(raw, list):
        raise ValueError("flashcards.json must contain a top-level JSON array")

    flashcards = [Flashcard.from_dict(item) for item in raw]
    return flashcards


def list_topics(flashcards: List[Flashcard]) -> List[str]:
    topics = sorted({fc.topic for fc in flashcards if fc.topic})
    return topics


def _collect_distractors_for_flashcard(
    flashcard: Flashcard,
    same_topic_pool: List[Flashcard],
    global_pool: List[Flashcard],
    num_distractors: int = 3,
) -> List[str]:
    """
    Build a list of distractor strings for a flashcard.
    Prefer distractors defined in the flashcard itself, then other answers from the same topic,
    then answers from the global pool.

    Ensures: distractors are unique and not equal to the correct answer.
    """
    distractors_set: List[str] = []

# 1) use explicit distractors from the flashcard if provided
    if flashcard.distractors:
        for d in flashcard.distractors:
            if d and d != flashcard.answer and d not in distractors_set:
                distractors_set.append(d)
                if len(distractors_set) >= num_distractors:
                    return distractors_set[:num_distractors]

    # Helper to pull answers from a pool (excluding correct answer and already-chosen)
    def pull_from_pool(pool: List[Flashcard], needed: int) -> None:
        candidates = [p.answer for p in pool if p.answer and p.answer != flashcard.answer]
        # Deduplicate while preserving random order
        random.shuffle(candidates)
        for c in candidates:
            if c not in distractors_set:
                distractors_set.append(c)
                if len(distractors_set) >= num_distractors:
                    return

    # 2) other answers from same topic
    pull_from_pool(same_topic_pool, num_distractors)

    # 3) fallback to global answers
    if len(distractors_set) < num_distractors:
        pull_from_pool(global_pool, num_distractors)

    # 4) If still not enough, duplicate existing distractors (rare). Ensure not equal to correct answer.
    if len(distractors_set) < num_distractors:
        # Create filler strings that are not the correct answer
        filler = 1
        while len(distractors_set) < num_distractors:
            candidate = f"Option {filler}"
            if candidate != flashcard.answer and candidate not in distractors_set:
                distractors_set.append(candidate)
            filler += 1

    return distractors_set[:num_distractors]

def generate_quiz_questions(
    topic: str,
    flashcards: List[Flashcard],
    num_questions: int = 10,
    seed: Optional[int] = None,
) -> List[QuizQuestion]:
    """
    Build up to `num_questions` QuizQuestion items for the given topic.

    Behavior:
    - If there are fewer flashcards in the topic than num_questions, returns all available (in random order).
    - For each selected flashcard, generates 3 distractors (prefer ordered from flashcard.distractors,
      then other answers in the same topic, then global pool), then shuffles options.
    - Guarantees the correct answer is included and options are unique.
    """
    if seed is not None:
        random.seed(seed)

    if not flashcards:
        return []

    # Filter by topic
    topic_pool = [fc for fc in flashcards if fc.topic == topic]
    if not topic_pool:
        # nothing in this topic
        return []

    # Determine which flashcards to use
    if len(topic_pool) <= num_questions:
        chosen = topic_pool.copy()
        random.shuffle(chosen)
    else:
        chosen = random.sample(topic_pool, k=num_questions)

    # Global pool for distractors fallback (exclude chosen card itself in generation)
    global_pool = [fc for fc in flashcards]

    quiz_questions: List[QuizQuestion] = []
    for fc in chosen:
        # same_topic_pool excludes the current flashcard
        same_topic_pool = [x for x in topic_pool if x.id != fc.id]
        distractors = _collect_distractors_for_flashcard(fc, same_topic_pool, global_pool, 3)

        # Build options (unique)
        options: List[str] = []
        options.append(fc.answer)
        for d in distractors:
            if d not in options:
                options.append(d)
        
        # If somehow we have fewer than 4 options, try to fill from global pool answers
        if len(options) < 4:
            extra_candidates = [g.answer for g in global_pool if g.answer not in options and g.answer != fc.answer]
            random.shuffle(extra_candidates)
            for ex in extra_candidates:
                options.append(ex)
                if len(options) >= 4:
                    break

        # Final safety: dedupe (should already be unique)
        final_options = list(dict.fromkeys(options))  # preserve order, remove duplicates
        # If still less than 4, pad with generic placeholders
        pad_counter = 1
        while len(final_options) < 4:
            pad_val = f"Option {pad_counter}"
            if pad_val != fc.answer and pad_val not in final_options:
                final_options.append(pad_val)
            pad_counter += 1

        random.shuffle(final_options)
        quiz_questions.append(
            QuizQuestion(
                flashcard_id=fc.id,
                prompt=fc.prompt,
                options=final_options,
                correct_answer=fc.answer,
            )
        )

    return quiz_questions