# 🧭 AI Career Mentor

An interactive Streamlit web app that recommends the **top 3 customized career options**
for students in Pakistan by combining **interest discovery** and **aptitude assessment** —
covering high-demand, high-income fields (Software Engineering, AI/Data Science,
Cybersecurity, Engineering, Medicine, Biotechnology, Finance, Statistics, Education,
Creative/Digital careers) **and freelancing**.

Built for a hackathon-friendly stack: **Python + Streamlit + Groq API**, deployable
straight from GitHub to Streamlit Community Cloud — no backend server, no database.

---

## ✨ Features

- **20-question adaptive assessment**
  - 10 **indirect, scenario-based interest questions** (never "which career do you want?").
    Later questions are chosen dynamically based on which interest categories are
    currently leading in the student's profile.
  - 10 **objective aptitude questions** across math, logical reasoning, English, science,
    analytical thinking, and problem solving.
  - One question at a time, with a live progress indicator (`7/20`) and smooth transitions.
- **Transparent scoring engine** (`scoring.py`) — every score is a traceable weighted
  combination of interest-category and aptitude-domain matches against a predefined set
  of 11 Pakistan-relevant career profiles. No hidden ML model decides the outcome.
- **AI-generated explanations** via the **Groq API** (Llama 3.3 70B) — the LLM explains
  the *already-computed* recommendations in warm, student-friendly language; it never
  invents or reorders the results. If the API is unavailable, a rule-based fallback
  keeps the app fully functional.
- **Results dashboard** with interest/aptitude summary charts and 3 detailed career cards
  (suitability score, why it fits your interests, why it fits your aptitude, key strengths,
  next steps, typical roles in Pakistan).
- Clear disclaimer throughout: **educational guidance only, not a diagnosis.**

---

## 🗂️ Repository Structure

```
ai-career-mentor/
├── app.py                       # Streamlit UI & session-state orchestration
├── questions.py                 # Interest question pool + fixed aptitude questions
├── scoring.py                   # Adaptive question selection + scoring engine
├── careers.py                   # Predefined career profiles (Pakistan context)
├── ai_mentor.py                 # Groq API integration + offline fallback
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    ├── config.toml              # App theme
    └── secrets.toml.example     # Template — copy to secrets.toml locally
```

---

## 🚀 Running Locally

1. **Clone and install dependencies**
   ```bash
   git clone <your-repo-url>
   cd ai-career-mentor
   pip install -r requirements.txt
   ```

2. **Add your Groq API key** (get one free at [console.groq.com](https://console.groq.com))
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # then edit .streamlit/secrets.toml and paste your real key
   ```
   > The app still works without a key — it falls back to built-in explanation
   > templates — but the Groq key enables fully personalized AI explanations.

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this repository to GitHub (make sure `.streamlit/secrets.toml` is **not** committed —
   it's already in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app pointing at
   your repo and `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
4. Deploy. That's it — no server, no database, no extra infrastructure.

---

## 🧠 How the Scoring Works

1. **Interest profile** — each of the 10 asked scenario questions contributes points to one
   or two of 11 interest categories (e.g. Software, AI/Data, Medicine, Freelance). Each
   category is normalized to a 0–100 score based only on the questions actually asked,
   so the comparison stays fair.
2. **Aptitude profile** — each of the 10 fixed quiz questions is graded correct/incorrect
   and rolled up into 6 domain scores (math, logic, English, science, analytical,
   problem solving) plus an overall aptitude score.
3. **Career suitability** — for each of the 11 predefined careers:
   ```
   suitability = 0.55 × (weighted interest match) + 0.45 × (weighted aptitude match)
   ```
   where the weights come from `careers.py` and are specific to each career (e.g.
   Cybersecurity weighs logical reasoning and analytical thinking heavily; Medicine
   weighs science heavily).
4. The **top 3 careers** by suitability score are shown, each with the specific interest
   categories and aptitude domains that drove the match — this is what gets passed to
   Groq so the AI explanation stays grounded in real numbers instead of guessing.

---

## ⚠️ Disclaimer

AI Career Mentor is an **educational career-guidance tool**. It is not a psychological,
medical, or diagnostic assessment and does not guarantee any career outcome. Results
should be treated as a starting point for further exploration with teachers, counselors,
and family.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Groq API** (Llama 3.3 70B) — personalized explanation generation
- **Pandas** — lightweight data shaping for the summary charts
- **GitHub + Streamlit Community Cloud** — version control & one-click deployment
