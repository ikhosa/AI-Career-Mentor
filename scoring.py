"""
scoring.py
----------
The transparent scoring engine for AI Career Mentor.

Nothing here is a black box: every number shown to the student can be
traced back to (a) which options they picked and (b) the fixed weights
in careers.py. There is no hidden ML model deciding the outcome — the
LLM (see ai_mentor.py) is used only to *explain* these already-computed
numbers in natural language, never to invent or reorder them.

Pipeline:
    1. select_next_interest_question()  -> adaptive question picker
    2. compute_interest_profile()       -> 0-100 score per interest category
    3. compute_aptitude_profile()       -> 0-100 score per aptitude domain + overall
    4. rank_careers()                   -> weighted match against CAREER_PROFILES
"""

from careers import CAREER_PROFILES, INTEREST_CATEGORIES, APTITUDE_DOMAINS
from questions import APTITUDE_QUESTIONS


# ---------------------------------------------------------------------------
# 1. Adaptive interest-question selection
# ---------------------------------------------------------------------------
def select_next_interest_question(pool, asked_ids, category_scores):
    """
    Pick the next interest question from the pool.

    The first question is fixed (no signal yet). After that, we look at the
    top-scoring categories so far and prefer whichever remaining question
    touches those categories the most -- this is what makes later questions
    "adapt" to earlier answers instead of being a static, non-responsive form.
    """
    remaining = [q for q in pool if q["id"] not in asked_ids]
    if not remaining:
        return None
    if not asked_ids:
        return remaining[0]

    # Current leading categories (top 3 with non-zero signal)
    ranked = sorted(category_scores.items(), key=lambda kv: -kv[1])
    top_categories = {cat for cat, val in ranked[:3] if val > 0}

    if not top_categories:
        return remaining[0]

    def relevance(q):
        cats_touched = set()
        for opt in q["options"]:
            cats_touched.update(opt["scores"].keys())
        return len(cats_touched & top_categories)

    remaining.sort(key=lambda q: -relevance(q))
    return remaining[0]


# ---------------------------------------------------------------------------
# 2. Interest profile
# ---------------------------------------------------------------------------
def compute_interest_profile(asked_questions, answers_by_qid):
    """
    asked_questions: list of question dicts (from the pool) that were shown
    answers_by_qid: dict {question_id: option_index chosen}

    Returns dict {category: percentage 0-100}, normalized against the
    maximum points that category *could* have earned given the questions
    that were actually asked (so a category that only appeared in 2
    questions is judged fairly against those 2, not against all 10).
    """
    raw = {cat: 0 for cat in INTEREST_CATEGORIES}
    max_possible = {cat: 0 for cat in INTEREST_CATEGORIES}

    for q in asked_questions:
        # track the max points any single option offers per category, for this question
        per_cat_max_this_q = {}
        for opt in q["options"]:
            for cat, pts in opt["scores"].items():
                per_cat_max_this_q[cat] = max(per_cat_max_this_q.get(cat, 0), pts)
        for cat, pts in per_cat_max_this_q.items():
            max_possible[cat] += pts

        chosen_idx = answers_by_qid.get(q["id"])
        if chosen_idx is None:
            continue
        chosen_scores = q["options"][chosen_idx]["scores"]
        for cat, pts in chosen_scores.items():
            raw[cat] += pts

    profile = {}
    for cat in INTEREST_CATEGORIES:
        if max_possible[cat] > 0:
            profile[cat] = round(100 * raw[cat] / max_possible[cat], 1)
        else:
            profile[cat] = 0.0
    return profile


# ---------------------------------------------------------------------------
# 3. Aptitude profile
# ---------------------------------------------------------------------------
def compute_aptitude_profile(answers_by_qid):
    """
    answers_by_qid: dict {question_id: option_index chosen}
    Returns {"overall": 0-100, "domains": {domain: 0-100}}
    """
    domain_correct = {d: 0 for d in APTITUDE_DOMAINS}
    domain_total = {d: 0 for d in APTITUDE_DOMAINS}
    total_correct = 0

    for q in APTITUDE_QUESTIONS:
        domain_total[q["domain"]] += 1
        chosen_idx = answers_by_qid.get(q["id"])
        if chosen_idx is not None and chosen_idx == q["correct_index"]:
            domain_correct[q["domain"]] += 1
            total_correct += 1

    domains = {}
    for d in APTITUDE_DOMAINS:
        if domain_total[d] > 0:
            domains[d] = round(100 * domain_correct[d] / domain_total[d], 1)
        else:
            domains[d] = 0.0

    overall = round(100 * total_correct / len(APTITUDE_QUESTIONS), 1) if APTITUDE_QUESTIONS else 0.0
    return {"overall": overall, "domains": domains, "correct_count": total_correct, "total_count": len(APTITUDE_QUESTIONS)}


# ---------------------------------------------------------------------------
# 4. Career ranking
# ---------------------------------------------------------------------------
INTEREST_WEIGHT = 0.55
APTITUDE_WEIGHT = 0.45


def rank_careers(interest_profile, aptitude_profile, top_n=3):
    """
    Returns a list of dicts (sorted, best first) with:
        key, name, category, suitability, interest_match, aptitude_match,
        top_interest_drivers, top_aptitude_drivers, career (full profile dict)
    """
    domains = aptitude_profile["domains"]
    results = []

    for key, career in CAREER_PROFILES.items():
        interest_match = sum(
            weight * interest_profile.get(cat, 0)
            for cat, weight in career["interest_weights"].items()
        )
        aptitude_match = sum(
            weight * domains.get(dom, 0)
            for dom, weight in career["aptitude_weights"].items()
        )
        suitability = round(INTEREST_WEIGHT * interest_match + APTITUDE_WEIGHT * aptitude_match, 1)

        # Which specific categories/domains drove this score the most (for transparency + LLM grounding)
        interest_drivers = sorted(
            career["interest_weights"].items(),
            key=lambda kv: -(kv[1] * interest_profile.get(kv[0], 0)),
        )[:2]
        aptitude_drivers = sorted(
            career["aptitude_weights"].items(),
            key=lambda kv: -(kv[1] * domains.get(kv[0], 0)),
        )[:2]

        results.append({
            "key": key,
            "name": career["name"],
            "category": career["category"],
            "suitability": suitability,
            "interest_match": round(interest_match, 1),
            "aptitude_match": round(aptitude_match, 1),
            "top_interest_drivers": [d[0] for d in interest_drivers],
            "top_aptitude_drivers": [d[0] for d in aptitude_drivers],
            "career": career,
        })

    results.sort(key=lambda r: (-r["suitability"], -r["interest_match"], r["name"]))
    return results[:top_n]
