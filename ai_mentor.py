"""
ai_mentor.py
------------
Uses the Groq API (Llama 3.3 70B by default) to turn the already-computed,
transparent scoring results into warm, personalized, student-friendly
explanations.

IMPORTANT: The LLM never chooses or reorders the careers, and never invents
scores. It is given the exact numbers computed by scoring.py and instructed
to explain them. If no API key is configured, or the call fails for any
reason, generate_recommendations() falls back to a rule-based template so
the app still works end-to-end (important for demo reliability).

The API key is read only from st.secrets["GROQ_API_KEY"] -- it is never
hard-coded.
"""

import json
import re

import streamlit as st

from careers import CATEGORY_LABELS, DOMAIN_LABELS

MODEL_NAME = "llama-3.3-70b-versatile"


def _get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception:
        return None


def _build_prompt(student_name, interest_profile, aptitude_profile, top_careers):
    interest_readable = {
        CATEGORY_LABELS.get(cat, cat): val
        for cat, val in sorted(interest_profile.items(), key=lambda kv: -kv[1])
        if val > 0
    }
    domain_readable = {
        DOMAIN_LABELS.get(dom, dom): val
        for dom, val in aptitude_profile["domains"].items()
    }

    careers_payload = []
    for c in top_careers:
        careers_payload.append({
            "name": c["name"],
            "category": c["category"],
            "suitability_score": c["suitability"],
            "interest_match_pct": c["interest_match"],
            "aptitude_match_pct": c["aptitude_match"],
            "leading_interest_drivers": [CATEGORY_LABELS.get(x, x) for x in c["top_interest_drivers"]],
            "leading_aptitude_drivers": [DOMAIN_LABELS.get(x, x) for x in c["top_aptitude_drivers"]],
            "demand_note_pakistan": c["career"]["demand_note"],
            "typical_roles": c["career"]["typical_roles"],
        })

    name_part = f"The student's name is {student_name}. " if student_name else ""

    instructions = f"""
You are a warm, encouraging career-guidance assistant for a Pakistani high-school/college
student named via an assessment app called "AI Career Mentor". {name_part}
A scoring engine (NOT you) has already calculated the student's interest profile, aptitude
profile, and exactly 3 recommended careers with fixed numeric scores. Your ONLY job is to
explain WHY these already-chosen careers fit, in plain, motivating language a student in
Pakistan would relate to. You must NOT change the ranking, invent new careers, invent new
scores, or claim any medical/psychological diagnosis.

STUDENT'S INTEREST PROFILE (0-100 scale, higher = stronger interest signal):
{json.dumps(interest_readable, indent=2)}

STUDENT'S APTITUDE PROFILE (0-100 scale, based on a 10-question objective quiz):
Overall aptitude score: {aptitude_profile['overall']} ({aptitude_profile['correct_count']}/{aptitude_profile['total_count']} correct)
By domain: {json.dumps(domain_readable, indent=2)}

TOP 3 RECOMMENDED CAREERS (already ranked, do not reorder):
{json.dumps(careers_payload, indent=2)}

Return ONLY a valid JSON array (no markdown fences, no extra commentary) with exactly 3
objects, one per career IN THE SAME ORDER given above, each with these exact keys:
- "career": the exact career name given above
- "why_interest": 2-3 sentences on why this matches their interest profile, referencing the
   leading interest drivers in relatable, scenario-style language (not just repeating labels)
- "why_aptitude": 2-3 sentences on why this matches their aptitude, referencing the leading
   aptitude drivers
- "key_strengths": an array of exactly 3 short strength phrases (3-6 words each)
- "next_steps": an array of exactly 3 concrete, Pakistan-relevant next steps a student could
   take this year (e.g. specific subjects to pick, local exams/entry tests like MDCAT/ECAT/NTS,
   free online courses, local competitions, freelancing platforms, relevant societies/clubs)

Keep tone encouraging but honest, avoid guaranteeing outcomes, and keep each explanation concise.
"""
    return instructions.strip()


def _safe_json_parse(text):
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned.strip())
    cleaned = re.sub(r"```$", "", cleaned.strip())
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return None
        return None


def _fallback_explanations(top_careers):
    """Rule-based explanation generator used when the Groq API is unavailable."""
    results = []
    for c in top_careers:
        interest_labels = [CATEGORY_LABELS.get(x, x) for x in c["top_interest_drivers"]]
        aptitude_labels = [DOMAIN_LABELS.get(x, x) for x in c["top_aptitude_drivers"]]
        results.append({
            "career": c["name"],
            "why_interest": (
                f"Your responses consistently leaned toward {', '.join(interest_labels) or 'this field'}, "
                f"which lines up closely with what {c['name']} actually involves day-to-day."
            ),
            "why_aptitude": (
                f"Your aptitude quiz showed particular strength in {', '.join(aptitude_labels) or 'core reasoning skills'}, "
                f"which are exactly the skills this field tends to reward."
            ),
            "key_strengths": [
                f"Strong {aptitude_labels[0]}" if aptitude_labels else "Solid reasoning skills",
                f"Genuine interest in {interest_labels[0]}" if interest_labels else "Clear career interest",
                "Good overall problem-solving foundation",
            ],
            "next_steps": [
                "Take a free intro course on this field to confirm your interest",
                "Talk to someone already working in this field (senior, relative, or LinkedIn contact)",
                "Look into relevant entry tests, degree programs, or online certifications in Pakistan",
            ],
        })
    return results


def generate_recommendations(student_name, interest_profile, aptitude_profile, top_careers):
    """
    Main entry point. Returns a list of 3 explanation dicts (same order as
    top_careers). Tries Groq first; falls back to a template if unavailable.
    """
    client = _get_groq_client()
    if client is None:
        return _fallback_explanations(top_careers), False

    prompt = _build_prompt(student_name, interest_profile, aptitude_profile, top_careers)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise, encouraging career-guidance explainer. Always return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1800,
        )
        text = response.choices[0].message.content
        parsed = _safe_json_parse(text)
        if not parsed or not isinstance(parsed, list) or len(parsed) != 3:
            return _fallback_explanations(top_careers), False
        return parsed, True
    except Exception:
        return _fallback_explanations(top_careers), False
