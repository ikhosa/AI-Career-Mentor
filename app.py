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
        --navy: #10192E;
        --navy-soft: #1E2E4F;
        --gold: #F2B134;
        --gold-dark: #B9820A;
        --teal: #0B5E5C;
        --bg: #EEF2F8;
        --ink: #14213D;
        --ink-soft: #3A4A6B;
    }

    html, body { color-scheme: light; }

    /* Force a light, high-contrast base regardless of the visitor's OS/browser theme */
    .stApp {
        background-color: var(--bg) !important;
        color: var(--ink) !important;
    }
    .stApp, .stApp p, .stApp li, .stApp span, .stApp label, .stApp div {
        color: var(--ink);
    }
    section.main .block-container { padding-top: 1.6rem; }

    /* ---------------- HEADER ---------------- */
    .amc-header {
        background: linear-gradient(135deg, #0B1226 0%, #0B5E5C 100%);
        padding: 30px 32px;
        border-radius: 16px;
        margin-bottom: 22px;
        box-shadow: 0 6px 18px rgba(10, 20, 40, 0.35);
    }
    .amc-header h1 { margin: 0; font-size: 2rem; font-weight: 800; color: ##FFD700 !important; }
    .amc-header p { margin: 8px 0 0 0; font-size: 1rem; color: #F3F6FB !important; opacity: 1; }
    .amc-badge {
        display: inline-block; background: var(--gold);
        padding: 5px 14px; border-radius: 999px; font-size: 0.75rem;
        margin-top: 12px; letter-spacing: 0.05em; font-weight: 800;
        color: #1A1300 !important;
    }

    /* ---------------- GENERIC CARD ---------------- */
    .amc-card, .amc-card * {
        color: var(--ink) !important;
    }
    .amc-card {
        background: #FFFFFF; border-radius: 14px; padding: 22px 24px;
        box-shadow: 0 2px 10px rgba(16,25,46,0.10); margin-bottom: 18px;
        border-left: 6px solid var(--teal);
        font-size: 1.02rem; line-height: 1.6;
    }
    .amc-card b { color: var(--navy) !important; }

    /* ---------------- QUESTION CARD ---------------- */
    .amc-question-card {
        background: #FFFFFF; border-radius: 16px; padding: 30px 28px 12px 28px;
        box-shadow: 0 4px 18px rgba(16,25,46,0.14); margin: 10px 0 4px 0;
        border-top: 6px solid var(--gold);
        border-left: 1px solid #E3E8F2; border-right: 1px solid #E3E8F2; border-bottom: 1px solid #E3E8F2;
    }
    .amc-question-card h3, .amc-question-card h3 * {
        color: var(--navy) !important; margin-top: 0; font-size: 1.4rem;
        font-weight: 750; line-height: 1.45;
    }

    /* Radio options rendered inside the question card: force dark, larger, readable text */
    .amc-question-card .stRadio [role="radiogroup"] label,
    .amc-question-card .stRadio [role="radiogroup"] label p,
    .amc-question-card .stRadio [role="radiogroup"] label div {
        color: var(--ink) !important;
        font-size: 1.08rem !important;
        opacity: 1 !important;
    }
    .amc-question-card .stRadio [role="radiogroup"] label {
        background: #F7F9FD;
        border: 1.5px solid #DCE3F0;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        transition: all 0.15s ease-in-out;
    }
    .amc-question-card .stRadio [role="radiogroup"] label:hover {
        border-color: var(--teal);
        background: #EFF7F6;
    }
    .amc-question-card .stRadio [role="radiogroup"] label[data-checked="true"],
    .amc-question-card .stRadio [role="radiogroup"] label:has(input:checked) {
        border-color: var(--gold-dark);
        background: #FFF6E3;
    }

    /* ---------------- CAREER RESULT CARDS ---------------- */
    .amc-career-card, .amc-career-card p, .amc-career-card div, .amc-career-card li, .amc-career-card ul {
        color: var(--ink) !important;
    }
    .amc-career-card {
        background: #FFFFFF; border-radius: 16px; padding: 24px 26px;
        box-shadow: 0 4px 18px rgba(16,25,46,0.14); margin-bottom: 22px;
        border-top: 6px solid var(--gold);
        font-size: 1.0rem; line-height: 1.65;
    }
    .amc-rank-badge {
        display: inline-block; background: var(--navy);
        font-weight: 700; border-radius: 999px; padding: 5px 15px;
        font-size: 0.8rem; margin-bottom: 10px;
    }
    .amc-career-card .amc-rank-badge, .amc-career-card div.amc-rank-badge {
        color: #FFFFFF !important;
    }
    .amc-score-pill {
        display: inline-block; background: var(--teal); color: #FFFFFF !important;
        font-weight: 700; border-radius: 999px; padding: 5px 15px;
        font-size: 0.88rem; float: right;
    }
    .amc-career-card h2, .amc-career-card h2 * { color: var(--navy) !important; margin: 6px 0 2px 0; font-size: 1.4rem; }
    .amc-career-cat { color: var(--teal) !important; font-weight: 700; font-size: 0.88rem; margin-bottom: 14px; }
    .amc-section-label { font-weight: 800; color: var(--navy) !important; margin-top: 16px; margin-bottom: 4px; font-size: 0.94rem; }
    .amc-career-card ul { margin-top: 4px; padding-left: 22px; }
    .amc-career-card li { margin-bottom: 4px; }

    /* ---------------- DISCLAIMER ---------------- */
    .amc-disclaimer, .amc-disclaimer * {
        color: #5A3D00 !important;
    }
    .amc-disclaimer {
        background: #FFF3D6; border: 1.5px solid var(--gold-dark); border-radius: 12px;
        padding: 14px 18px; font-size: 0.88rem; margin-top: 26px; line-height: 1.55;
    }

    /* ---------------- BUTTONS ---------------- */
    .stButton > button[kind="primary"] {
        background: #87CEEB !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.4rem !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #6EC1E4 !important;
        color: #000000 !important;
    }
    .stButton > button[kind="primary"]:disabled {
        background: #C7E7F5 !important;
        color: #4A4A4A !important;
    }
    .stButton > button:not([kind="primary"]) {
        background: #87CEEB !important;
        color: #000000 !important;
        border: 1.5px solid #87CEEB !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* ---------------- PROGRESS BAR ---------------- */
    div[data-testid="stProgress"] > div > div { background-color: var(--gold-dark) !important; }
    div[data-testid="stProgress"] p { color: var(--ink) !important; font-weight: 600; }

    /* Text input label readability on the welcome screen */
    .stTextInput label p { color: var(--ink) !important; font-weight: 600; }

    /* ---------------- BAR CHARTS ---------------- */
    .amc-chart-wrap {
        background: #FFFFFF !important;
        border-radius: 12px;
        padding: 10px;
    }
    [data-testid="stArrowVegaLiteChart"] svg,
    [data-testid="stVegaLiteChart"] svg,
    .amc-chart-wrap .vega-embed {
        background-color: #FFFFFF !important;
    }
    [data-testid="stArrowVegaLiteChart"] text,
    [data-testid="stVegaLiteChart"] text {
        fill: #000000 !important;
    }
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

    if st.button("🚀 Discover your Career", type="primary", use_container_width=True):
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
            st.markdown('<div class="amc-chart-wrap">', unsafe_allow_html=True)
            st.bar_chart(interest_df, height=320)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("**Aptitude Profile**")
            domains = aptitude_profile["domains"]
            aptitude_df = pd.DataFrame(
                {"Domain": [DOMAIN_LABELS.get(k, k) for k in domains.keys()],
                 "Score": list(domains.values())}
            ).sort_values("Score", ascending=False).set_index("Domain")
            st.markdown('<div class="amc-chart-wrap">', unsafe_allow_html=True)
            st.bar_chart(aptitude_df, height=320)
            st.markdown('</div>', unsafe_allow_html=True)
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
