"""
questions.py
------------
Question bank for the AI Career Mentor assessment.

INTEREST_QUESTION_POOL
    A pool of scenario-based (indirect) questions. Each question's options map
    to one or more interest categories with a point value. The pool has more
    questions (13) than the number actually asked (10) so that the app can
    adaptively pick the next most-informative question based on the
    categories that are currently leading in the student's running profile
    (see scoring.select_next_interest_question). This is what makes the
    interest section "adapt" question-to-question without needing a live LLM
    call for every question (fast, deterministic, hackathon-friendly).

APTITUDE_QUESTIONS
    A fixed set of 10 multiple-choice aptitude questions spanning six
    domains: math, logic, english, science, analytical thinking and
    problem solving. These are graded objectively (correct/incorrect).
"""

INTEREST_QUESTIONS_TARGET = 10
APTITUDE_QUESTIONS_TARGET = 10

# ---------------------------------------------------------------------------
# INTEREST QUESTION POOL (13 questions; 10 are dynamically selected)
# ---------------------------------------------------------------------------
INTEREST_QUESTION_POOL = [
    {
        "id": "int_01",
        "text": "It's a free Saturday with zero obligations. What are you most likely doing?",
        "options": [
            {"text": "Tinkering with a coding project or building something on the computer",
             "scores": {"software": 3, "ai_data": 1}},
            {"text": "Watching a documentary about diseases or medical breakthroughs",
             "scores": {"medicine": 3, "biotech": 1}},
            {"text": "Editing videos/photos or designing something for social media",
             "scores": {"creative": 3, "freelance": 1}},
            {"text": "Reading about the stock market, business news, or a side-hustle idea",
             "scores": {"finance": 3, "freelance": 1}},
        ],
    },
    {
        "id": "int_02",
        "text": "Your class gets a group project with a vague, open-ended topic. What role do you naturally take?",
        "options": [
            {"text": "The one who organizes the data, makes charts, and crunches numbers",
             "scores": {"statistics": 3, "ai_data": 1}},
            {"text": "The one who researches deeply and writes up the explanations",
             "scores": {"education": 3, "biotech": 1}},
            {"text": "The one who builds or designs the actual prototype or presentation",
             "scores": {"engineering": 3, "creative": 1}},
            {"text": "The one who worries about protecting the group's shared files and accounts",
             "scores": {"cybersecurity": 3, "software": 1}},
        ],
    },
    {
        "id": "int_03",
        "text": "A relative's laptop gets infected with a virus after a scam email. What's your honest reaction?",
        "options": [
            {"text": "Excited — I want to figure out exactly how the attack happened",
             "scores": {"cybersecurity": 3, "software": 1}},
            {"text": "I'd Google a quick fix and move on, not that fascinated by it",
             "scores": {"software": 2, "freelance": 1}},
            {"text": "I'm more curious why people fall for online scams in the first place",
             "scores": {"education": 2, "finance": 1}},
            {"text": "Not really my thing — I'd rather be doing something creative",
             "scores": {"creative": 2}},
        ],
    },
    {
        "id": "int_04",
        "text": "You see a news report about a new disease outbreak. What's your first instinct?",
        "options": [
            {"text": "I want to understand how the illness spreads and how it's treated",
             "scores": {"medicine": 3, "biotech": 2}},
            {"text": "I wonder how data scientists are tracking and forecasting the spread",
             "scores": {"ai_data": 2, "statistics": 2}},
            {"text": "I think about how this will affect businesses and the economy",
             "scores": {"finance": 3}},
            {"text": "I start imagining an awareness campaign or poster design about it",
             "scores": {"creative": 3, "education": 1}},
        ],
    },
    {
        "id": "int_05",
        "text": "Your phone's battery has started draining unusually fast. What's your approach?",
        "options": [
            {"text": "Dig into settings and apps to diagnose exactly what's draining it",
             "scores": {"software": 3, "engineering": 1}},
            {"text": "Get curious about the actual engineering/chemistry of why batteries degrade",
             "scores": {"engineering": 3, "biotech": 1}},
            {"text": "Calculate whether it's cheaper to replace the battery or upgrade the phone",
             "scores": {"finance": 3, "statistics": 1}},
            {"text": "Make a light-hearted post about it and see who else relates",
             "scores": {"creative": 3, "freelance": 1}},
        ],
    },
    {
        "id": "int_06",
        "text": "A family friend wants help selling homemade products online. What excites you most about helping?",
        "options": [
            {"text": "Building them a simple website or order-taking app",
             "scores": {"software": 3, "freelance": 1}},
            {"text": "Designing their logo, packaging, and social media posts",
             "scores": {"creative": 3, "freelance": 1}},
            {"text": "Figuring out pricing, profit margins, and how to grow revenue",
             "scores": {"finance": 3, "statistics": 1}},
            {"text": "Honestly, I'd rather help with something scientific instead",
             "scores": {"biotech": 1, "medicine": 1}},
        ],
    },
    {
        "id": "int_07",
        "text": "In science class, which topic genuinely fascinates you rather than just being 'okay'?",
        "options": [
            {"text": "How the human body fights off disease",
             "scores": {"medicine": 3}},
            {"text": "How genes and DNA determine traits",
             "scores": {"biotech": 3}},
            {"text": "How machines and structures are engineered to not fail",
             "scores": {"engineering": 3}},
            {"text": "How computers process information and 'make decisions'",
             "scores": {"ai_data": 3, "software": 1}},
        ],
    },
    {
        "id": "int_08",
        "text": "Your teacher offers an optional extra-credit mini-project. Which do you choose?",
        "options": [
            {"text": "Build a small app or automate a repetitive task",
             "scores": {"software": 3}},
            {"text": "Survey classmates and analyze the results with charts",
             "scores": {"statistics": 3, "ai_data": 1}},
            {"text": "Write and design a short e-book or creative portfolio piece",
             "scores": {"creative": 3, "freelance": 1}},
            {"text": "Research a local health/education/environment problem and propose a fix",
             "scores": {"education": 2, "medicine": 1}},
        ],
    },
    {
        "id": "int_09",
        "text": "If you had to earn money this month without a fixed 9-to-5 job, what sounds most appealing?",
        "options": [
            {"text": "Taking on freelance gigs (design, writing, coding) from online platforms",
             "scores": {"freelance": 3, "creative": 1}},
            {"text": "Tutoring younger students in subjects you're strong in",
             "scores": {"education": 3}},
            {"text": "Investing small savings and tracking how the market moves",
             "scores": {"finance": 3}},
            {"text": "Honestly, I'd rather have one stable, secure job than freelance",
             "scores": {"engineering": 1, "medicine": 1}},
        ],
    },
    {
        "id": "int_10",
        "text": "Which achievement would make you proudest, ten years from now?",
        "options": [
            {"text": "Building an app or product that thousands of people rely on",
             "scores": {"software": 3, "ai_data": 1}},
            {"text": "Contributing research that helps solve a real health problem",
             "scores": {"medicine": 2, "biotech": 2}},
            {"text": "Being a respected, in-demand freelancer/consultant known worldwide",
             "scores": {"freelance": 3}},
            {"text": "Designing something so visually striking it goes viral",
             "scores": {"creative": 3}},
        ],
    },
    {
        "id": "int_11",
        "text": "A well-known Pakistani bank suffers a cyberattack. What's your honest reaction?",
        "options": [
            {"text": "I want to know exactly how the hackers got in",
             "scores": {"cybersecurity": 3}},
            {"text": "I wonder how this affects the stock market and customer trust",
             "scores": {"finance": 3}},
            {"text": "I think about how the bank should communicate this to the public",
             "scores": {"education": 2, "creative": 1}},
            {"text": "I'm curious about the technical/encryption systems involved",
             "scores": {"software": 2, "cybersecurity": 1}},
        ],
    },
    {
        "id": "int_12",
        "text": "You're handed a messy spreadsheet of survey data with zero instructions. What's your instinct?",
        "options": [
            {"text": "Clean it up and hunt for patterns or trends in it",
             "scores": {"statistics": 3, "ai_data": 1}},
            {"text": "Write a small script to process it automatically",
             "scores": {"software": 2, "ai_data": 1}},
            {"text": "Ignore the raw numbers — ask what story it's really telling",
             "scores": {"education": 1, "creative": 1}},
            {"text": "Check whether this data could inform a business/pricing decision",
             "scores": {"finance": 3}},
        ],
    },
    {
        "id": "int_13",
        "text": "At a university open day, which stall would you spend the most time at?",
        "options": [
            {"text": "Robotics & engineering demos",
             "scores": {"engineering": 3}},
            {"text": "Hospital / medical simulation stall",
             "scores": {"medicine": 3}},
            {"text": "Startup & freelancing stall",
             "scores": {"freelance": 3, "finance": 1}},
            {"text": "Design, media & animation stall",
             "scores": {"creative": 3}},
        ],
    },
]

# ---------------------------------------------------------------------------
# APTITUDE QUESTIONS (fixed, 10 total across 6 domains)
# ---------------------------------------------------------------------------
APTITUDE_QUESTIONS = [
    {
        "id": "apt_01",
        "domain": "math",
        "text": "A shopkeeper buys an item for Rs. 800 and sells it for Rs. 1000. What is his profit percentage?",
        "options": ["20%", "25%", "15%", "30%"],
        "correct_index": 1,
    },
    {
        "id": "apt_02",
        "domain": "math",
        "text": "What comes next in the sequence: 2, 6, 12, 20, 30, ?",
        "options": ["36", "40", "42", "48"],
        "correct_index": 2,
    },
    {
        "id": "apt_03",
        "domain": "logic",
        "text": "All engineers are analytical. Ali is an engineer. Which statement must be true?",
        "options": ["Ali is analytical", "Ali is creative", "Ali is not analytical", "Cannot be determined"],
        "correct_index": 0,
    },
    {
        "id": "apt_04",
        "domain": "logic",
        "text": "Complete the pattern: AB, BC, CD, DE, ?",
        "options": ["EF", "FE", "DF", "EG"],
        "correct_index": 0,
    },
    {
        "id": "apt_05",
        "domain": "english",
        "text": "Choose the word closest in meaning to 'Meticulous'.",
        "options": ["Careless", "Detailed and careful", "Fast", "Lazy"],
        "correct_index": 1,
    },
    {
        "id": "apt_06",
        "domain": "english",
        "text": "Which sentence is correctly punctuated?",
        "options": [
            "Its a beautiful day, isnt it",
            "It's a beautiful day, isn't it?",
            "Its a beautiful day isnt it?",
            "It is a beautiful day isnt' it",
        ],
        "correct_index": 1,
    },
    {
        "id": "apt_07",
        "domain": "science",
        "text": "Which organ is primarily responsible for pumping blood through the human body?",
        "options": ["Lungs", "Heart", "Liver", "Kidney"],
        "correct_index": 1,
    },
    {
        "id": "apt_08",
        "domain": "science",
        "text": "Which gas do plants primarily absorb from the atmosphere for photosynthesis?",
        "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        "correct_index": 2,
    },
    {
        "id": "apt_09",
        "domain": "analytical",
        "text": "A train travels 60 km in 45 minutes. What is its speed in km/h?",
        "options": ["60 km/h", "80 km/h", "90 km/h", "75 km/h"],
        "correct_index": 1,
    },
    {
        "id": "apt_10",
        "domain": "problem_solving",
        "text": (
            "You have 3 boxes: one has only apples, one has only oranges, one is mixed — "
            "but ALL three labels are wrong. You may pick ONE fruit from ONE box to correctly "
            "relabel all three boxes. Which box should you pick from?"
        ),
        "options": ["The box labeled 'Apples'", "The box labeled 'Oranges'", "The box labeled 'Mixed'", "It doesn't matter which box"],
        "correct_index": 2,
    },
]
