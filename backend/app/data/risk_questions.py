"""Static risk-tolerance question bank used to seed the database."""

RISK_QUESTIONS = [
    {
        "question": "How would you describe your investment experience?",
        "options": [
            {"text": "None — I'm new to investing", "score": 1},
            {"text": "Some experience with savings accounts / fixed deposits", "score": 2},
            {"text": "Moderate — I've invested in mutual funds or stocks", "score": 3},
            {"text": "Extensive — I actively manage a diverse portfolio", "score": 4},
        ],
        "factor": "investment_experience",
    },
    {
        "question": "How stable is your current income?",
        "options": [
            {"text": "Very unstable / irregular", "score": 1},
            {"text": "Somewhat variable", "score": 2},
            {"text": "Mostly stable", "score": 3},
            {"text": "Very stable (e.g. secure salaried job)", "score": 4},
        ],
        "factor": "income_stability",
    },
    {
        "question": "How many months of expenses does your emergency fund cover?",
        "options": [
            {"text": "None", "score": 1},
            {"text": "Less than 3 months", "score": 2},
            {"text": "3-6 months", "score": 3},
            {"text": "More than 6 months", "score": 4},
        ],
        "factor": "emergency_savings",
    },
    {
        "question": "What is your investment time horizon for most of your goals?",
        "options": [
            {"text": "Less than 1 year", "score": 1},
            {"text": "1-3 years", "score": 2},
            {"text": "3-7 years", "score": 3},
            {"text": "More than 7 years", "score": 4},
        ],
        "factor": "investment_horizon",
    },
    {
        "question": "If your investment portfolio dropped 20% in value in a month, what would you do?",
        "options": [
            {"text": "Sell everything immediately to avoid further loss", "score": 1},
            {"text": "Sell a portion to reduce risk", "score": 2},
            {"text": "Hold and wait it out", "score": 3},
            {"text": "Buy more while prices are lower", "score": 4},
        ],
        "factor": "loss_reaction",
    },
    {
        "question": "How comfortable are you with your investment value fluctuating significantly in the short term for potentially higher long-term returns?",
        "options": [
            {"text": "Not comfortable at all", "score": 1},
            {"text": "Slightly comfortable", "score": 2},
            {"text": "Moderately comfortable", "score": 3},
            {"text": "Very comfortable", "score": 4},
        ],
        "factor": "volatility_tolerance",
    },
    {
        "question": "How would you describe your current financial obligations (loans, dependents, EMIs)?",
        "options": [
            {"text": "Very high — most of my income is committed", "score": 1},
            {"text": "High", "score": 2},
            {"text": "Moderate", "score": 3},
            {"text": "Low or none", "score": 4},
        ],
        "factor": "financial_obligations",
    },
]
