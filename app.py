"""
app.py
------
AI Career Mentor — Streamlit entry point.

A single-file UI layer that walks a student through:
    Welcome -> 10 adaptive interest questions -> 10 aptitude questions -> Results

All scoring logic lives in scoring.py, career data in careers.py, question
content in questions.py, and LLM explanation generation in ai_mentor.py --
this file is purely presentation + session-state orchestration.
"""

import streamlit as st
import pandas as pd

from questions import INTEREST_QUESTION_POOL, APTITUDE_QUESTIONS, INTEREST_QUESTIONS_TARGET, APTITUDE_QUESTIONS_TARGET
from careers import INTEREST_CATEGORIES, CATEGORY_LABELS, DOMAIN_LABELS
from scoring import select_next_interest_question, compute_interest_profile, compute_aptitude_profile, rank_careers
from ai_mentor import generate_recommendations

TOTAL_QUESTIONS = INTEREST_QUESTIONS_TARGET + APTITUDE_QUESTIONS_TARGET

# ---------------------------------------------------------------------------
# PAGE CONFIG + THEME
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Career Mentor",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    :root {
        --navy: #14213D;
        --gold: #F2B134;
        --teal: #0E7C7B;
        --bg: #F7F9FC;
    }
    .stApp { background-color: var(--bg); }

    .amc-header {
        background: linear-gradient(135deg, #14213D 0%, #0E7C7B 100%);
        padding: 28px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 6px 18px rgba(20, 33, 61, 0.25);
    }
    .amc-header h1 { margin: 0; font-size: 1.9rem; font-weight: 800; }
    .amc-header p { margin: 6px 0 0 0; opacity: 0.9; font-size: 0.95rem; }
    .amc-badge {
        display: inline-block; background: rgba(255,255,255,0.15);
        padding: 4px 12px; border-radius: 999px; font-size: 0.75rem;
        margin-top: 10px; letter-spacing: 0.04em;
    }

    .amc-card {
        background: white; border-radius: 14px; padding: 22px 24px;
        box-shadow: 0 2px 10px rgba(20,33,61,0.08); margin-bottom: 18px;
        border-left: 6px solid var(--teal);
    }
    .amc-question-card {
        background: white; border-radius: 16px; padding: 30px 28px;
        box-shadow: 0 4px 16px rgba(20,33,61,0.10); margin: 10px 0 20px 0;
        border-top: 5px solid var(--gold);
    }
    .amc-question-card h3 { color: var(--navy); margin-top: 0; }

    .amc-career-card {
        background: white; border-radius: 16px; padding: 24px 26px;
        box-shadow: 0 4px 16px rgba(20,33,61,0.10); margin-bottom: 22px;
        border-top: 6px solid var(--gold);
    }
    .amc-rank-badge {
        display: inline-block; background: var(--navy); color: white;
        font-weight: 700; border-radius: 999px; padding: 4px 14px;
        font-size: 0.8rem; margin-bottom: 8px;
    }
    .amc-score-pill {
        display: inline-block; background: var(--teal); color: white;
        font-weight: 700; border-radius: 999px; padding: 4px 14px;
        font-size: 0.85rem; float: right;
    }
    .amc-career-card h2 { color: var(--navy); margin: 6px 0 2px 0; font-size: 1.35rem; }
    .amc-career-cat { color: var(--teal); font-weight: 600; font-size: 0.85rem; margin-bottom: 12px; }
    .amc-section-label { font-weight: 700; color: var(--navy); margin-top: 14px; margin-bottom: 4px; font-size: 0.92rem; }

    .amc-disclaimer {
        background: #FFF7E6; border: 1px solid #F2B134; border-radius: 12px;
        padding: 14px 18px; font-size: 0.85rem; color: #6b4e00; margin-top: 26px;
    }
    div[data-testid="stProgress"] > div > div { background-color: var(--gold) !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DISCLAIMER_TEXT = (
    "⚠️ **Disclaimer:** AI Career Mentor is an educational career-guidance tool built for "
    "self-exploration. It is **not** a psychological, medical, or diagnostic assessment, and it "
    "does not guarantee any career outcome. Please treat these results as a starting point for "
    "further research and conversation with teachers, counselors, and family."
)


def render_header(subtitle):
    st.markdown(
        f"""
        <div class="amc-header">
            <h1>🧭 AI Career Mentor</h1>
            <p>{subtitle}</p>
            <span class="amc-badge">PAKISTAN CAREER GUIDANCE PLATFORM</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------------
def init_state():
    defaults = {
        "stage": "welcome",
        "student_name": "",
        "asked_interest_ids": [],
        "interest_answers": {},
        "category_scores": {cat: 0 for cat in INTEREST_CATEGORIES},
        "current_interest_q": None,
        "aptitude_index": 0,
        "aptitude_answers": {},
        "results": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def restart_assessment():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


init_state()


# ---------------------------------------------------------------------------
# STAGE: WELCOME
# ---------------------------------------------------------------------------
def render_welcome():
    render_header("Discover the top 3 careers in Pakistan that genuinely fit YOU — not a generic list.")

    st.markdown(
        """
        <div class="amc-card">
        <b>How it works</b><br><br>
        1️⃣ Answer 10 quick, scenario-based questions about how you naturally react to everyday situations
        (no boring "pick your dream job" questions).<br><br>
        2️⃣ Answer 10 short aptitude questions covering math, logical reasoning, English, science, and
        problem solving.<br><br>
        3️⃣ Get your top 3 personalized career recommendations — matched to Pakistan's high-demand,
        high-income fields, including freelancing — with a clear, transparent explanation of why each one fits.
        </div>
        """,
        unsafe_allow_html=True,
    )

    name = st.text_input("What should we call you? (optional)", value=st.session_state.student_name)
    st.session_state.student_name = name

    st.markdown(DISCLAIMER_TEXT)

    if st.button("🚀 Start Assessment", type="primary", use_container_width=True):
        st.session_state.stage = "interest"
        st.rerun()


# ---------------------------------------------------------------------------
# STAGE: INTEREST QUESTIONS
# ---------------------------------------------------------------------------
def render_interest_stage():
    render_header("Interest Discovery — answer honestly, there are no right or wrong answers.")

    asked = st.session_state.asked_interest_ids
    if st.session_state.current_interest_q is None:
        st.session_state.current_interest_q = select_next_interest_question(
            INTEREST_QUESTION_POOL, asked, st.session_state.category_scores
        )

    question = st.session_state.current_interest_q
    q_number = len(asked) + 1

    progress = (q_number - 1) / TOTAL_QUESTIONS
    st.progress(progress, text=f"Question {q_number} of {TOTAL_QUESTIONS}  •  Section: Interest Discovery")

    st.markdown('<div class="amc-question-card">', unsafe_allow_html=True)
    st.markdown(f"### {question['text']}")
    option_texts = [opt["text"] for opt in question["options"]]
    choice = st.radio(
        "Choose the option that feels most like you:",
        option_texts,
        index=None,
        key=f"radio_{question['id']}",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        next_clicked = st.button("Next ➜", type="primary", disabled=(choice is None))

    if next_clicked and choice is not None:
        chosen_idx = option_texts.index(choice)
        st.session_state.interest_answers[question["id"]] = chosen_idx
        for cat, pts in question["options"][chosen_idx]["scores"].items():
            st.session_state.category_scores[cat] += pts
        asked.append(question["id"])
        st.session_state.current_interest_q = None

        if len(asked) >= INTEREST_QUESTIONS_TARGET:
            st.session_state.stage = "aptitude"
        st.rerun()


# ---------------------------------------------------------------------------
# STAGE: APTITUDE QUESTIONS
# ---------------------------------------------------------------------------
def render_aptitude_stage():
    render_header("Aptitude Check — a quick mix of math, logic, English, science & problem solving.")

    idx = st.session_state.aptitude_index
    question = APTITUDE_QUESTIONS[idx]
    q_number = INTEREST_QUESTIONS_TARGET + idx + 1

    progress = (q_number - 1) / TOTAL_QUESTIONS
    domain_label = DOMAIN_LABELS.get(question["domain"], question["domain"].title())
    st.progress(progress, text=f"Question {q_number} of {TOTAL_QUESTIONS}  •  Section: Aptitude ({domain_label})")

    st.markdown('<div class="amc-question-card">', unsafe_allow_html=True)
    st.markdown(f"### {question['text']}")
    choice = st.radio(
        "Choose your answer:",
        question["options"],
        index=None,
        key=f"radio_{question['id']}",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        is_last = idx == len(APTITUDE_QUESTIONS) - 1
        button_label = "See My Results 🎉" if is_last else "Next ➜"
        next_clicked = st.button(button_label, type="primary", disabled=(choice is None))

    if next_clicked and choice is not None:
        chosen_idx = question["options"].index(choice)
        st.session_state.aptitude_answers[question["id"]] = chosen_idx

        if is_last:
            finalize_results()
            st.session_state.stage = "results"
        else:
            st.session_state.aptitude_index += 1
        st.rerun()


# ---------------------------------------------------------------------------
# FINALIZE: run scoring + LLM explanation generation
# ---------------------------------------------------------------------------
def finalize_results():
    asked_questions = [q for q in INTEREST_QUESTION_POOL if q["id"] in st.session_state.interest_answers]
    interest_profile = compute_interest_profile(asked_questions, st.session_state.interest_answers)
    aptitude_profile = compute_aptitude_profile(st.session_state.aptitude_answers)
    top_careers = rank_careers(interest_profile, aptitude_profile, top_n=3)

    with st.spinner("Your AI mentor is preparing your personalized guidance..."):
        explanations, used_llm = generate_recommendations(
            st.session_state.student_name, interest_profile, aptitude_profile, top_careers
        )

    st.session_state.results = {
        "interest_profile": interest_profile,
        "aptitude_profile": aptitude_profile,
        "top_careers": top_careers,
        "explanations": explanations,
        "used_llm": used_llm,
    }


# ---------------------------------------------------------------------------
# STAGE: RESULTS DASHBOARD
# ---------------------------------------------------------------------------
def render_results_stage():
    results = st.session_state.results
    name = st.session_state.student_name
    greeting = f"Here's what we found for {name} 🎯" if name else "Here's what we found for you 🎯"
    render_header(greeting)

    interest_profile = results["interest_profile"]
    aptitude_profile = results["aptitude_profile"]
    top_careers = results["top_careers"]
    explanations = results["explanations"]

    if results["used_llm"]:
        st.caption("✨ Personalized explanations generated by your AI mentor (Groq / Llama 3.3)")
    else:
        st.caption("⚙️ Showing guidance from built-in templates (AI service unavailable right now)")

    # --- Summary charts ---
    with st.expander("📊 Your Interest & Aptitude Summary", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Interest Profile**")
            interest_df = pd.DataFrame(
                {"Category": [CATEGORY_LABELS.get(k, k) for k in interest_profile.keys()],
                 "Score": list(interest_profile.values())}
            ).sort_values("Score", ascending=False).set_index("Category")
            st.bar_chart(interest_df, height=320)
        with c2:
            st.markdown("**Aptitude Profile**")
            domains = aptitude_profile["domains"]
            aptitude_df = pd.DataFrame(
                {"Domain": [DOMAIN_LABELS.get(k, k) for k in domains.keys()],
                 "Score": list(domains.values())}
            ).sort_values("Score", ascending=False).set_index("Domain")
            st.bar_chart(aptitude_df, height=320)
            st.metric("Overall Aptitude Score", f"{aptitude_profile['overall']}%",
                       help=f"{aptitude_profile['correct_count']}/{aptitude_profile['total_count']} correct")

    st.markdown("## 🏆 Your Top 3 Career Matches")

    medal = ["🥇", "🥈", "🥉"]
    for i, (career, explanation) in enumerate(zip(top_careers, explanations)):
        st.markdown(
            f"""
            <div class="amc-career-card">
                <span class="amc-score-pill">Suitability: {career['suitability']}%</span>
                <div class="amc-rank-badge">{medal[i]} #{i+1} MATCH — {career['category']}</div>
                <h2>{career['name']}</h2>
                <div class="amc-career-cat">Interest Match: {career['interest_match']}%  •  Aptitude Match: {career['aptitude_match']}%</div>
                <div class="amc-section-label">💡 Why it matches your interests</div>
                <div>{explanation.get('why_interest', '')}</div>
                <div class="amc-section-label">🧠 Why it matches your aptitude</div>
                <div>{explanation.get('why_aptitude', '')}</div>
                <div class="amc-section-label">⭐ Key strengths identified</div>
                <ul>{''.join(f"<li>{s}</li>" for s in explanation.get('key_strengths', []))}</ul>
                <div class="amc-section-label">🚀 Suggested next steps</div>
                <ul>{''.join(f"<li>{s}</li>" for s in explanation.get('next_steps', []))}</ul>
                <div class="amc-section-label">📌 Typical roles in Pakistan</div>
                <div>{', '.join(career['career']['typical_roles'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(DISCLAIMER_TEXT, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Retake Assessment", use_container_width=True):
        restart_assessment()
        st.rerun()


# ---------------------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------------------
if st.session_state.stage == "welcome":
    render_welcome()
elif st.session_state.stage == "interest":
    render_interest_stage()
elif st.session_state.stage == "aptitude":
    render_aptitude_stage()
elif st.session_state.stage == "results":
    render_results_stage()
