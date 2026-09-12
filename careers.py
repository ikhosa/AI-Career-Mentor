"""
careers.py
-----------
Predefined career profiles for the AI Career Mentor app.

Each career defines:
- interest_weights: how much each interest category contributes to this
  career's suitability (weights should roughly sum to 1.0)
- aptitude_weights: how much each aptitude domain contributes to this
  career's suitability (weights should roughly sum to 1.0)
- context: short Pakistan-specific framing used both in the UI and as
  grounding context for the LLM explanations.

These weights are intentionally simple and transparent (a weighted-average
model) so the whole scoring pipeline stays explainable — there is no
hidden ML model deciding the outcome.
"""

CAREER_PROFILES = {
    "software_engineering": {
        "name": "Software Engineering",
        "category": "Technology",
        "interest_weights": {"software": 0.60, "ai_data": 0.15, "cybersecurity": 0.15, "creative": 0.10},
        "aptitude_weights": {"logic": 0.35, "math": 0.25, "problem_solving": 0.25, "english": 0.15},
        "demand_note": "One of Pakistan's highest-demand, highest-export-earning fields, with strong local (Karachi/Lahore/Islamabad tech hubs) and remote/international opportunities.",
        "typical_roles": ["Web/Mobile App Developer", "Backend Engineer", "DevOps Engineer", "QA/Automation Engineer"],
    },
    "ai_data_science": {
        "name": "AI / Data Science",
        "category": "Technology",
        "interest_weights": {"ai_data": 0.55, "statistics": 0.25, "software": 0.10, "engineering": 0.10},
        "aptitude_weights": {"math": 0.35, "logic": 0.25, "analytical": 0.25, "problem_solving": 0.15},
        "demand_note": "Fast-growing globally and in Pakistan's tech sector; strong remote-work and freelance demand for ML/AI skills.",
        "typical_roles": ["Machine Learning Engineer", "Data Scientist", "AI Research Assistant", "NLP/Computer Vision Engineer"],
    },
    "cybersecurity": {
        "name": "Cybersecurity",
        "category": "Technology",
        "interest_weights": {"cybersecurity": 0.60, "software": 0.20, "engineering": 0.10, "ai_data": 0.10},
        "aptitude_weights": {"logic": 0.35, "analytical": 0.30, "problem_solving": 0.20, "english": 0.15},
        "demand_note": "Rising demand in Pakistan's banking, telecom and government sectors as digital services grow, plus international remote roles.",
        "typical_roles": ["Security Analyst", "Penetration Tester", "SOC Engineer", "Security Consultant"],
    },
    "engineering": {
        "name": "Engineering (Electrical/Mechanical/Civil)",
        "category": "Engineering",
        "interest_weights": {"engineering": 0.60, "software": 0.15, "ai_data": 0.10, "creative": 0.15},
        "aptitude_weights": {"math": 0.40, "science": 0.30, "problem_solving": 0.20, "logic": 0.10},
        "demand_note": "Consistently strong, stable demand across Pakistan's energy, construction, manufacturing and telecom sectors.",
        "typical_roles": ["Design Engineer", "Site/Project Engineer", "Electrical/Power Engineer", "Automation Engineer"],
    },
    "medicine_healthcare": {
        "name": "Medicine / Healthcare",
        "category": "Healthcare",
        "interest_weights": {"medicine": 0.70, "biotech": 0.15, "education": 0.15},
        "aptitude_weights": {"science": 0.40, "analytical": 0.25, "english": 0.20, "logic": 0.15},
        "demand_note": "Consistently high social respect and demand in Pakistan; growing need for specialists, and telemedicine is opening new formats.",
        "typical_roles": ["Doctor (MBBS path)", "Dentist (BDS path)", "Physiotherapist", "Healthcare Administrator"],
    },
    "biotechnology": {
        "name": "Biotechnology",
        "category": "Science",
        "interest_weights": {"biotech": 0.60, "medicine": 0.20, "ai_data": 0.10, "statistics": 0.10},
        "aptitude_weights": {"science": 0.40, "math": 0.20, "analytical": 0.25, "problem_solving": 0.15},
        "demand_note": "Emerging field in Pakistan tied to agriculture, pharmaceuticals and food science, with growing research funding.",
        "typical_roles": ["Biotech Researcher", "Lab Scientist", "Agri-Biotech Specialist", "Pharma R&D Associate"],
    },
    "finance_economics": {
        "name": "Finance / Economics",
        "category": "Business",
        "interest_weights": {"finance": 0.65, "statistics": 0.20, "education": 0.15},
        "aptitude_weights": {"math": 0.35, "analytical": 0.30, "logic": 0.20, "english": 0.15},
        "demand_note": "High-income potential in Pakistan's banking, investment, and corporate finance sectors, plus fintech growth.",
        "typical_roles": ["Financial Analyst", "Investment Banker", "Chartered Accountant path", "Economist"],
    },
    "statistics_analytics": {
        "name": "Statistics / Data Analytics",
        "category": "Technology",
        "interest_weights": {"statistics": 0.55, "ai_data": 0.25, "finance": 0.20},
        "aptitude_weights": {"math": 0.40, "analytical": 0.30, "logic": 0.20, "problem_solving": 0.10},
        "demand_note": "Growing demand as Pakistani companies and multinationals invest in data-driven decision-making.",
        "typical_roles": ["Data Analyst", "Business Intelligence Analyst", "Research Analyst", "Actuarial Analyst"],
    },
    "education_research": {
        "name": "Education / Research",
        "category": "Academia",
        "interest_weights": {"education": 0.60, "creative": 0.15, "medicine": 0.10, "statistics": 0.15},
        "aptitude_weights": {"english": 0.30, "analytical": 0.25, "logic": 0.25, "science": 0.20},
        "demand_note": "Steady demand across Pakistan's growing private education sector, ed-tech platforms, and research institutions.",
        "typical_roles": ["Subject Teacher/Lecturer", "Curriculum Designer", "Academic Researcher", "Ed-Tech Content Specialist"],
    },
    "creative_digital": {
        "name": "Creative / Digital Careers",
        "category": "Creative",
        "interest_weights": {"creative": 0.65, "software": 0.15, "freelance": 0.20},
        "aptitude_weights": {"english": 0.30, "problem_solving": 0.25, "analytical": 0.25, "logic": 0.20},
        "demand_note": "Booming in Pakistan via YouTube, social media, gaming, animation and design agencies serving global clients.",
        "typical_roles": ["Graphic/UI Designer", "Video Editor/Animator", "Content Creator", "Digital Marketer"],
    },
    "freelancing_remote": {
        "name": "Freelancing / Remote Digital Careers",
        "category": "Independent",
        "interest_weights": {"freelance": 0.50, "creative": 0.25, "software": 0.15, "ai_data": 0.10},
        "aptitude_weights": {"problem_solving": 0.30, "english": 0.25, "analytical": 0.25, "logic": 0.20},
        "demand_note": "Pakistan is consistently ranked among the top freelance-earning countries globally (Upwork/Fiverr/Payoneer data); strong option alongside or instead of traditional jobs.",
        "typical_roles": ["Freelance Developer", "Freelance Designer/Writer", "Virtual Assistant/Consultant", "Independent Digital Marketer"],
    },
}

INTEREST_CATEGORIES = [
    "software", "ai_data", "cybersecurity", "engineering", "medicine",
    "biotech", "finance", "statistics", "education", "creative", "freelance",
]

APTITUDE_DOMAINS = ["math", "logic", "english", "science", "analytical", "problem_solving"]

CATEGORY_LABELS = {
    "software": "Software & Technology",
    "ai_data": "AI & Data",
    "cybersecurity": "Cybersecurity",
    "engineering": "Engineering",
    "medicine": "Medicine & Healthcare",
    "biotech": "Biotechnology",
    "finance": "Finance & Business",
    "statistics": "Statistics & Analytics",
    "education": "Education & Research",
    "creative": "Creative & Digital Media",
    "freelance": "Independent/Freelance Work",
}

DOMAIN_LABELS = {
    "math": "Mathematics",
    "logic": "Logical Reasoning",
    "english": "English/Communication",
    "science": "Science",
    "analytical": "Analytical Thinking",
    "problem_solving": "Problem Solving",
}
