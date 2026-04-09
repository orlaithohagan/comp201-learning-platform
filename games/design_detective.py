import json
import random
from pathlib import Path

import streamlit as st

DATA_PATH = Path("data/design_detective_cases.json")
DIFFICULTY_POINTS = {"easy": 2, "medium": 4, "hard": 6}
CASES_PER_ROUND = 5

DD_KEYS = [
    "dd_in_session",
    "dd_cases",
    "dd_idx",
    "dd_score",
    "dd_results",
    "dd_checked",
]

@st.cache_data
def load_cases_cached() -> list:
    """Load Design Detective cases from JSON."""
    if not DATA_PATH.exists():
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _init_dd_state() -> None:
    """Initialise Design Detective session state."""
    ss = st.session_state
    ss.setdefault("dd_in_session", False)
    ss.setdefault("dd_cases", [])
    ss.setdefault("dd_idx", 0)
    ss.setdefault("dd_score", 0)
    ss.setdefault("dd_results", [])
    ss.setdefault("dd_checked", False)


def reset_design_detective() -> None:
    """Clear Design Detective session state."""
    for key in DD_KEYS:
        st.session_state.pop(key, None)


def _shuffle_case_options(case: dict) -> dict:
    """Return a copy of a case with shuffled answer options."""
    shuffled_case = dict(case)
    shuffled_case["questions"] = dict(case["questions"])

    primary = dict(case["questions"]["primary"])
    secondary = dict(case["questions"]["secondary"])

    primary_options = list(primary["options"])
    secondary_options = list(secondary["options"])

    random.shuffle(primary_options)
    random.shuffle(secondary_options)

    primary["options"] = primary_options
    secondary["options"] = secondary_options

    shuffled_case["questions"]["primary"] = primary
    shuffled_case["questions"]["secondary"] = secondary
    return shuffled_case


def start_new_round(all_cases: list, n: int = CASES_PER_ROUND) -> None:
    """Start a new round with a random sample of cases."""
    reset_design_detective()
    ss = st.session_state

    if len(all_cases) < n:
        chosen = all_cases[:]
        random.shuffle(chosen)
    else:
        chosen = random.sample(all_cases, n)

    ss.dd_cases = [_shuffle_case_options(case) for case in chosen]
    ss.dd_in_session = True
    ss.dd_idx = 0
    ss.dd_score = 0
    ss.dd_results = []
    ss.dd_checked = False


def _current_case() -> dict | None:
    """Return the current case or None if unavailable."""
    ss = st.session_state
    if not ss.dd_cases:
        return None
    if ss.dd_idx < 0 or ss.dd_idx >= len(ss.dd_cases):
        return None
    return ss.dd_cases[ss.dd_idx]


def _evidence_tabs(case: dict) -> None:
    """Render evidence tabs for the current case."""
    evidence = case.get("evidence", {}) or {}

    tab_names = ["Case file"]
    if evidence.get("requirements"):
        tab_names.append("Requirements")
    if evidence.get("diagram_text"):
        tab_names.append("Model / Diagram")
    if evidence.get("snippet"):
        tab_names.append("Snippet")

    tabs = st.tabs(tab_names)

    with tabs[0]:
        st.markdown("**Scenario**")
        st.write(case.get("scenario", "—"))
        st.write("")

    tab_index = 1

    if evidence.get("requirements"):
        with tabs[tab_index]:
            st.markdown("**Requirements (evidence)**")
            for requirement in evidence["requirements"]:
                st.write(f"• {requirement}")
        tab_index += 1

    if evidence.get("diagram_text"):
        with tabs[tab_index]:
            st.markdown("**Model / Diagram (text)**")
            st.code(evidence["diagram_text"], language="text")
        tab_index += 1

    if evidence.get("snippet"):
        with tabs[tab_index]:
            st.markdown("**Snippet (evidence)**")
            st.code(evidence["snippet"], language="python")


def _score_case(case: dict, chosen_issue: str, chosen_fix: str) -> dict:
    """Score one case based on issue/fix answers."""
    difficulty = case.get("difficulty", "easy").lower()
    base_points = DIFFICULTY_POINTS.get(difficulty, 2)

    q1 = case["questions"]["primary"]
    q2 = case["questions"]["secondary"]

    issue_correct = chosen_issue == q1["answer"]
    fix_correct = chosen_fix == q2["answer"]

    points_per_question = max(1, base_points // 2)
    points = 0
    points += points_per_question if issue_correct else 0
    points += points_per_question if fix_correct else 0

    return {
        "difficulty": difficulty,
        "category": case.get("category", "General"),
        "issue_correct": issue_correct,
        "fix_correct": fix_correct,
        "points_awarded": points,
    }


def _get_weak_topics(results: list) -> list[str]:
    """Return weak categories based on round performance."""
    category_stats = {}

    for result in results:
        category = result["category"]
        category_stats.setdefault(category, {"correct": 0, "total": 0})
        category_stats[category]["total"] += 2
        category_stats[category]["correct"] += (
            (1 if result["issue_correct"] else 0) +
            (1 if result["fix_correct"] else 0)
        )

    weak_topics = []
    for category, stats in category_stats.items():
        accuracy = stats["correct"] / stats["total"]
        if accuracy < 0.6:
            weak_topics.append(category)

    return weak_topics


def render_round_summary(state: dict) -> None:
    """Render the end-of-round summary."""
    correct = state.get("correct_count", 0)
    total = state.get("total_questions", 0)
    weak_topics = state.get("weak_topics", [])[:2]
    pct = (correct / total * 100) if total else 0

    st.markdown("---")
    st.header("Round complete 🎉")
    st.subheader(f"Score: **{correct} / {total}**")

    if pct >= 90:
        st.success("Design Detective level: **Elite** — you’re spotting issues like a pro.")
    elif pct >= 70:
        st.info("Nice work! **Solid Detective** — a bit more practice and you’ll ace it.")
    elif pct >= 50:
        st.warning("Good start! **Getting Warmer** — you’re close, keep going.")
    else:
        st.error("Tough round — but that’s how you learn. **Keep practicing**")

    st.markdown("### Quick tip for next round")
    if weak_topics:
        st.write("Focus on:")
        for topic in weak_topics:
            st.write(f"• **{topic}**")
    else:
        st.write("You didn’t show any clear weak spots — try another round!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Play another round", use_container_width=True):
            all_cases = load_cases_cached()
            start_new_round(all_cases, CASES_PER_ROUND)
            st.rerun()

    with col2:
        if st.button("Back to Games Hub", use_container_width=True):
            st.session_state.view = "hub"
            st.rerun()

    if pct >= 70:
        st.balloons()


def _render_intro_screen(all_cases: list) -> None:
    """Render the intro screen before a round starts."""
    st.title("Design Detective 🕵️")
    st.caption("A case-based game to strengthen your software engineering judgement.")

    st.markdown("### How to play")
    st.write("1) Start a round (you’ll receive 5 random cases).")
    st.write("2) Read the case file and inspect the evidence tabs.")
    st.write("3) Answer two questions:")
    st.write("   • What is the issue?")
    st.write("   • What is the best fix?")
    st.write("4) Check your answers and review the explanation.")
    st.write("5) Move to the next case and improve your score.")

    st.markdown("### Purpose")
    st.write(
        "Design Detective helps you practise analysing realistic software engineering scenarios "
        "by identifying design and modelling problems and selecting appropriate improvements."
    )

    st.markdown("### Scoring")
    st.write("• Difficulty affects points: Easy 2, Medium 4, Hard 6.")
    st.write("• Each case includes two questions, and points are split across them.")

    if st.button("Start round ▶", use_container_width=True):
        start_new_round(all_cases, CASES_PER_ROUND)
        st.rerun()


def _render_feedback(case: dict, result: dict, q1: dict, q2: dict) -> None:
    """Render feedback for a checked case."""
    st.markdown("---")
    st.subheader("Feedback")

    if result["issue_correct"] and result["fix_correct"]:
        st.success("Perfect! Both answers are correct.")
    elif result["issue_correct"] or result["fix_correct"]:
        st.warning("Partially correct — review the explanation below.")
    else:
        st.error("Not quite — review the explanation below.")

    st.write(f"**Points awarded:** {result['points_awarded']}")

    with st.expander("Show explanation"):
        st.write(case.get("explanation", "—"))

    with st.expander("Show correct answers"):
        st.write(f"**Issue (correct):** {q1['answer']}")
        st.write(f"**Best fix (correct):** {q2['answer']}")


def play_design_detective() -> None:
    """Run the Design Detective game."""
    _init_dd_state()
    ss = st.session_state

    top_left, _ = st.columns([1, 5])
    with top_left:
        if st.button("← Back", key="dd_back"):
            ss.mini_games_view = "hub"
            st.rerun()

    all_cases = load_cases_cached()
    if not all_cases:
        st.error("No Design Detective cases found. Check data/design_detective_cases.json")
        return

    if not ss.dd_in_session:
        _render_intro_screen(all_cases)
        return

    if ss.dd_idx >= len(ss.dd_cases):
        correct_q = sum(
            (1 if result["issue_correct"] else 0) + (1 if result["fix_correct"] else 0)
            for result in ss.dd_results
        )
        total_q = len(ss.dd_results) * 2
        weak_topics = _get_weak_topics(ss.dd_results)

        render_round_summary(
            {
                "correct_count": correct_q,
                "total_questions": total_q,
                "weak_topics": weak_topics,
            }
        )
        return

    case = _current_case()
    if not case:
        st.error("Could not load current case.")
        return

    difficulty = case.get("difficulty", "easy").lower()
    category = case.get("category", "General")
    case_id = case.get("id", f"idx_{ss.dd_idx}")

    st.title("Design Detective 🕵️")
    st.markdown(
        f"**Case {ss.dd_idx + 1} of {len(ss.dd_cases)}** — **{case.get('title', 'Untitled Case')}**"
    )

    col1, col2 = st.columns(2)
    col1.metric("Score", ss.dd_score)
    col2.metric("Difficulty", difficulty.capitalize())
    st.caption(f"Category: {category}")

    st.markdown("---")
    _evidence_tabs(case)
    st.markdown("---")

    q1 = case["questions"]["primary"]
    q2 = case["questions"]["secondary"]

    chosen_issue = st.radio(
        q1["question"],
        q1["options"],
        key=f"dd_issue_{case_id}",
        disabled=ss.dd_checked,
    )

    chosen_fix = st.radio(
        q2["question"],
        q2["options"],
        key=f"dd_fix_{case_id}",
        disabled=ss.dd_checked,
    )

    action1, action2 = st.columns([1, 2])

    with action1:
        if st.button("Check!", key=f"dd_check_{case_id}", disabled=ss.dd_checked):
            result = _score_case(case, chosen_issue, chosen_fix)

            ss.dd_score += result["points_awarded"]
            ss.dd_results.append(result)
            ss.dd_checked = True
            st.rerun()

    with action2:
        if st.button("Next case", key=f"dd_next_{case_id}", disabled=not ss.dd_checked):
            ss.dd_idx += 1
            ss.dd_checked = False
            st.rerun()

    if ss.dd_checked:
        _render_feedback(case, ss.dd_results[-1], q1, q2)