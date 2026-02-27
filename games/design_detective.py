import json
import random
from pathlib import Path
import streamlit as st

DATA_PATH = Path("data/design_detective_cases.json")

DIFFICULTY_POINTS = {"easy": 2, "medium": 4, "hard": 6}
HINT_PENALTY = 1

# Session format
CASES_PER_ROUND = 5  # <-- rounds of 5 cases


def load_cases():
    if not DATA_PATH.exists():
        st.error("Design Detective data file not found: data/design_detective_cases.json")
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _init_dd_state():
    ss = st.session_state
    ss.setdefault("dd_in_session", False)
    ss.setdefault("dd_cases", [])
    ss.setdefault("dd_idx", 0)
    ss.setdefault("dd_score", 0)
    ss.setdefault("dd_streak", 0)
    ss.setdefault("dd_results", [])  # list of dicts per case
    ss.setdefault("dd_hint_used", False)
    ss.setdefault("dd_checked", False)
    ss.setdefault("dd_last_feedback", None)


def reset_design_detective():
    ss = st.session_state
    for k in [
        "dd_in_session",
        "dd_cases",
        "dd_idx",
        "dd_score",
        "dd_streak",
        "dd_results",
        "dd_hint_used",
        "dd_checked",
        "dd_last_feedback",
    ]:
        ss.pop(k, None)
    _init_dd_state()


def _shuffle_case_options(case: dict) -> dict:
    """
    Return a copy of case with shuffled options for primary & secondary questions.
    Answers remain as strings; we simply shuffle the options lists.
    """
    c = dict(case)
    c["questions"] = dict(case["questions"])

    primary = dict(case["questions"]["primary"])
    secondary = dict(case["questions"]["secondary"])

    p_opts = list(primary["options"])
    s_opts = list(secondary["options"])

    random.shuffle(p_opts)
    random.shuffle(s_opts)

    primary["options"] = p_opts
    secondary["options"] = s_opts

    c["questions"]["primary"] = primary
    c["questions"]["secondary"] = secondary
    return c


def start_new_round(all_cases, n=CASES_PER_ROUND):
    """
    Start a new round of n cases, randomly sampled from the full dataset,
    and shuffle answer options for each case.
    """
    reset_design_detective()
    _init_dd_state()
    ss = st.session_state

    if len(all_cases) < n:
        chosen = all_cases[:]
        random.shuffle(chosen)
    else:
        chosen = random.sample(all_cases, n)

    # Shuffle answer options so correct isn't always first
    chosen = [_shuffle_case_options(c) for c in chosen]

    ss.dd_cases = chosen
    ss.dd_in_session = True
    ss.dd_idx = 0
    ss.dd_score = 0
    ss.dd_streak = 0
    ss.dd_results = []
    ss.dd_hint_used = False
    ss.dd_checked = False
    ss.dd_last_feedback = None


def _current_case():
    ss = st.session_state
    if not ss.dd_cases:
        return None
    if ss.dd_idx < 0 or ss.dd_idx >= len(ss.dd_cases):
        return None
    return ss.dd_cases[ss.dd_idx]


def _evidence_tabs(case):
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

    t_i = 1

    if evidence.get("requirements"):
        with tabs[t_i]:
            st.markdown("**Requirements (evidence)**")
            for r in evidence["requirements"]:
                st.write(f"• {r}")
        t_i += 1

    if evidence.get("diagram_text"):
        with tabs[t_i]:
            st.markdown("**Model / Diagram (text)**")
            st.code(evidence["diagram_text"], language="text")
        t_i += 1

    if evidence.get("snippet"):
        with tabs[t_i]:
            st.markdown("**Snippet (evidence)**")
            st.code(evidence["snippet"], language="python")
        t_i += 1


def _score_case(case, chosen_issue, chosen_fix, hint_used):
    difficulty = case.get("difficulty", "easy").lower()
    base = DIFFICULTY_POINTS.get(difficulty, 2)

    q1 = case["questions"]["primary"]
    q2 = case["questions"]["secondary"]

    issue_correct = (chosen_issue == q1["answer"])
    fix_correct = (chosen_fix == q2["answer"])

    # Split base points across two questions
    per_question = max(1, base // 2)  # easy=1, medium=2, hard=3
    points = 0
    points += per_question if issue_correct else 0
    points += per_question if fix_correct else 0

    # Hint penalty
    if hint_used:
        points = max(0, points - HINT_PENALTY)

    return {
        "difficulty": difficulty,
        "category": case.get("category", "General"),
        "issue_correct": issue_correct,
        "fix_correct": fix_correct,
        "hint_used": hint_used,
        "points_awarded": points,
    }


def _build_improvement_tips(results):
    """
    Generate improvement suggestions based on category performance.
    """
    if not results:
        return ["Complete at least one round to see personalised tips."]

    # Category stats
    stats = {}
    for r in results:
        cat = r["category"]
        stats.setdefault(cat, {"cases": 0, "q_correct": 0, "q_total": 0})
        stats[cat]["cases"] += 1
        stats[cat]["q_total"] += 2
        stats[cat]["q_correct"] += (1 if r["issue_correct"] else 0) + (1 if r["fix_correct"] else 0)

    # Compute accuracies
    ranked = []
    for cat, s in stats.items():
        acc = s["q_correct"] / s["q_total"] if s["q_total"] else 0
        ranked.append((acc, cat, s))
    ranked.sort()  # lowest first

    tips = []
    weakest = ranked[:2]  # focus on weakest 2 categories
    for acc, cat, s in weakest:
        pct = int(round(acc * 100))
        if cat == "Requirements":
            tips.append(f"**Requirements ({pct}%):** practise writing testable requirements (avoid vague words) and include security/non-functional constraints.")
        elif cat == "Modelling":
            tips.append(f"**Modelling ({pct}%):** revise multiplicities and how relationships reflect real-world constraints (1..*, 0..*, ownership).")
        elif cat == "OO Design":
            tips.append(f"**OO Design ({pct}%):** revisit associations vs composition/aggregation and when lifecycles imply ownership.")
        elif cat == "Design":
            tips.append(f"**Design ({pct}%):** focus on modularity: separate concerns, high cohesion, low coupling, and clear interfaces.")
        elif cat == "Testing":
            tips.append(f"**Testing ({pct}%):** review verification vs validation and choose appropriate test types (unit/integration/system, regression).")
        elif cat == "Project Management":
            tips.append(f"**Project Management ({pct}%):** revisit risk planning and estimation concepts (what changes effort, what increases risk).")
        else:
            tips.append(f"**{cat} ({pct}%):** practise more cases in this category to strengthen your understanding.")

    # Always include a general tip
    tips.append("**General:** Try to answer without hints first. If you use a hint, read the explanation and replay a new round to reinforce the concept.")
    return tips


def _summary_screen():
    ss = st.session_state
    st.title("Design Detective — Round Summary 🧾")

    total_cases = len(ss.dd_results)
    if total_cases == 0:
        st.info("No cases completed yet.")
        return

    total_score = ss.dd_score
    perfect_cases = sum(1 for r in ss.dd_results if r["issue_correct"] and r["fix_correct"] and not r["hint_used"])
    both_correct = sum(1 for r in ss.dd_results if r["issue_correct"] and r["fix_correct"])
    any_correct = sum(1 for r in ss.dd_results if r["issue_correct"] or r["fix_correct"])
    hints = sum(1 for r in ss.dd_results if r["hint_used"])

    st.markdown("### Results")
    st.write(f"**Total score:** {total_score}")
    st.write(f"**Cases completed:** {total_cases}")
    st.write(f"**Perfect cases (both correct, no hint):** {perfect_cases} / {total_cases}")
    st.write(f"**Both correct (hint allowed):** {both_correct} / {total_cases}")
    st.write(f"**At least one correct answer:** {any_correct} / {total_cases}")
    st.write(f"**Hints used:** {hints}")

    # Category breakdown
    st.markdown("### Category breakdown")
    categories = {}
    for r in ss.dd_results:
        cat = r["category"]
        categories.setdefault(cat, {"cases": 0, "points": 0, "q_correct": 0, "q_total": 0})
        categories[cat]["cases"] += 1
        categories[cat]["points"] += r["points_awarded"]
        categories[cat]["q_total"] += 2
        categories[cat]["q_correct"] += (1 if r["issue_correct"] else 0) + (1 if r["fix_correct"] else 0)

    for cat, info in categories.items():
        acc = int(round((info["q_correct"] / info["q_total"]) * 100)) if info["q_total"] else 0
        st.write(f"**{cat}** — {info['points']} pts, accuracy: {acc}% ({info['cases']} case(s))")

    st.markdown("### Suggested improvements")
    for tip in _build_improvement_tips(ss.dd_results):
        st.write(f"• {tip}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Play another round 🔁", use_container_width=True):
            all_cases = load_cases()
            start_new_round(all_cases, CASES_PER_ROUND)
            st.rerun()
    with c2:
        if st.button("Back to Games Hub 🏠", use_container_width=True):
            st.session_state.view = "hub"
            st.rerun()


def play_design_detective():
    _init_dd_state()
    ss = st.session_state

    # Back button (always available)
    top_left, _ = st.columns([1, 5])
    with top_left:
        if st.button("← Back", key="dd_back"):
            ss.view = "hub"
            st.rerun()

    all_cases = load_cases()
    if not all_cases:
        return

    # Start round if not in one yet
    if not ss.dd_in_session:
        st.title("Design Detective 🕵️")
        st.caption("A case-based game to strengthen your software engineering judgement.")

        st.markdown("### How to play")
        st.write("1) Start a round (you’ll receive **5 random cases**).")
        st.write("2) For each case, read the **case file** and check the evidence tabs.")
        st.write("3) Answer two questions:")
        st.write("   • **What’s the issue?** (diagnosis)")
        st.write("   • **What’s the best fix?** (improvement)")
        st.write("4) Use **Hint** only if needed (it reduces points for that case).")
        st.write("5) Build a **streak** by getting both answers correct without a hint.")

        st.markdown("### Purpose")
        st.write(
            "Design Detective helps you practise analysing realistic scenarios by connecting requirements, modelling, design decisions, "
            "and testing choices. Instead of memorising definitions, you train the skill of identifying problems and selecting good solutions."
        )

        st.markdown("### Scoring")
        st.write("• Difficulty affects points: Easy 2, Medium 4, Hard 6 (split across the two questions).")
        st.write(f"• Hint costs {HINT_PENALTY} point on that case.")
        st.write("• Streak rewards consistent, confident answers (no hint).")

        if st.button("Start round ▶", use_container_width=True):
            start_new_round(all_cases, CASES_PER_ROUND)
            st.rerun()
        return

    # If finished
    if ss.dd_idx >= len(ss.dd_cases):
        _summary_screen()
        return

    case = _current_case()
    if not case:
        st.error("Could not load current case.")
        return

    difficulty = case.get("difficulty", "easy").lower()
    category = case.get("category", "General")

    st.title("Design Detective 🕵️")
    st.markdown(
        f"**Case {ss.dd_idx + 1} of {len(ss.dd_cases)}** — **{case.get('title', 'Untitled Case')}**"
    )

    s1, s2, s3 = st.columns(3)
    s1.metric("Score", ss.dd_score)
    s2.metric("Streak", ss.dd_streak)
    s3.metric("Difficulty", difficulty.capitalize())
    st.caption(f"Category: {category}")

    st.markdown("---")
    _evidence_tabs(case)
    st.markdown("---")

    q1 = case["questions"]["primary"]
    q2 = case["questions"]["secondary"]
    case_id = case.get("id", f"idx_{ss.dd_idx}")

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

    a1, a2, a3 = st.columns([1, 1, 2])

    with a1:
        if st.button("💡 Hint", key=f"dd_hint_{case_id}", disabled=ss.dd_hint_used or ss.dd_checked):
            ss.dd_hint_used = True
            st.rerun()

    with a2:
        if st.button("✅ Check", key=f"dd_check_{case_id}", disabled=ss.dd_checked):
            result = _score_case(case, chosen_issue, chosen_fix, ss.dd_hint_used)

            # Perfect streak: both correct AND no hint
            perfect = result["issue_correct"] and result["fix_correct"] and (not result["hint_used"])
            if perfect:
                ss.dd_streak += 1
            else:
                ss.dd_streak = 0

            # Simple streak bonus every 3 perfect cases (within the round)
            bonus = 0
            if perfect and ss.dd_streak > 0 and ss.dd_streak % 3 == 0:
                bonus = 2

            ss.dd_score += result["points_awarded"] + bonus
            result["streak_bonus"] = bonus

            ss.dd_results.append(result)
            ss.dd_checked = True
            ss.dd_last_feedback = {"chosen_issue": chosen_issue, "chosen_fix": chosen_fix}
            st.rerun()

    with a3:
        if st.button("⏭ Next case", key=f"dd_next_{case_id}", disabled=not ss.dd_checked):
            ss.dd_idx += 1
            ss.dd_hint_used = False
            ss.dd_checked = False
            ss.dd_last_feedback = None
            st.rerun()

    if ss.dd_hint_used and not ss.dd_checked:
        st.info(f"Hint: {case.get('hint', 'No hint available.')}\n\n(Using a hint costs 1 point on this case.)")

    if ss.dd_checked and ss.dd_last_feedback:
        st.markdown("---")
        res = ss.dd_results[-1]
        st.subheader("Feedback")

        if res["issue_correct"] and res["fix_correct"]:
            if res["hint_used"]:
                st.success("Both answers are correct ✅ (Hint used: -1 point)")
            else:
                st.success("Perfect! Both answers are correct ✅")
        elif res["issue_correct"] or res["fix_correct"]:
            st.warning("Partially correct ⚠️ — review the explanation below.")
        else:
            st.error("Not quite ❌ — review the explanation below.")

        pts_line = f"**Points awarded:** {res['points_awarded']}"
        if res.get("streak_bonus", 0):
            pts_line += f"  |  **Streak bonus:** +{res['streak_bonus']}"
        st.write(pts_line)

        with st.expander("Show explanation"):
            st.write(case.get("explanation", "—"))

        with st.expander("Show correct answers"):
            st.write(f"**Issue (correct):** {q1['answer']}")
            st.write(f"**Best fix (correct):** {q2['answer']}")