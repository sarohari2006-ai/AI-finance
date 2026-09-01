"""
Seed the database with:
  - financial literacy question bank
  - risk tolerance question bank
  - 3 demo users with distinct financial profiles, transactions, goals,
    loans, insurance, and investments, so the recommendation engine
    visibly produces different output per user.

Run with: py scripts/seed.py   (from the backend/ directory)
"""
import sys
import os
import json
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import Base, engine, SessionLocal
from app.models.models import (
    User, FinancialProfile, Transaction, TransactionType, FinancialGoal, GoalPriority,
    Loan, Insurance, Investment, LiteracyQuestion, RiskQuestion,
)
from app.data.literacy_questions import LITERACY_QUESTIONS
from app.data.risk_questions import RISK_QUESTIONS
from app.auth.security import hash_password

random.seed(42)

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed_questions():
    if db.query(LiteracyQuestion).count() == 0:
        for q in LITERACY_QUESTIONS:
            db.add(LiteracyQuestion(
                question=q["question"],
                options=json.dumps(q["options"]),
                correct_answer=q["correct_answer"],
                explanation=q["explanation"],
                topic=q["topic"],
            ))
        db.commit()
        print(f"Seeded {len(LITERACY_QUESTIONS)} literacy questions.")
    else:
        print("Literacy questions already seeded.")

    if db.query(RiskQuestion).count() == 0:
        for q in RISK_QUESTIONS:
            db.add(RiskQuestion(
                question=q["question"],
                options=json.dumps(q["options"]),
                factor=q["factor"],
            ))
        db.commit()
        print(f"Seeded {len(RISK_QUESTIONS)} risk questions.")
    else:
        print("Risk questions already seeded.")


def gen_transactions(user_id, months, income, income_category, expense_profile):
    """expense_profile: dict of category -> (min, max) monthly amount"""
    txns = []
    today = date.today()
    for m in range(months):
        month_date = today.replace(day=1) - timedelta(days=30 * m)
        txns.append(Transaction(
            user_id=user_id,
            date=month_date.replace(day=1),
            category=income_category,
            amount=round(income * random.uniform(0.95, 1.05), 2),
            type=TransactionType.income,
            description="Monthly salary",
        ))
        for cat, (lo, hi) in expense_profile.items():
            day = random.randint(1, 28)
            try:
                txn_date = month_date.replace(day=day)
            except ValueError:
                txn_date = month_date.replace(day=28)
            txns.append(Transaction(
                user_id=user_id,
                date=txn_date,
                category=cat,
                amount=round(random.uniform(lo, hi), 2),
                type=TransactionType.expense,
                description=f"{cat.capitalize()} expense",
            ))
    return txns


def create_user(name, email, age, occupation, profile_kwargs, months, income, expense_profile,
                 goals, loans, insurances, investments):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"User {email} already exists, skipping.")
        return existing

    user = User(
        name=name, email=email, hashed_password=hash_password("password123"),
        age=age, occupation=occupation,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = FinancialProfile(user_id=user.id, **profile_kwargs)
    db.add(profile)

    for txn in gen_transactions(user.id, months, income, "salary", expense_profile):
        db.add(txn)

    for g in goals:
        db.add(FinancialGoal(user_id=user.id, **g))

    for l in loans:
        db.add(Loan(user_id=user.id, **l))

    for i in insurances:
        db.add(Insurance(user_id=user.id, **i))

    for inv in investments:
        db.add(Investment(user_id=user.id, **inv))

    db.commit()
    print(f"Created user: {name} ({email})")
    return user


def seed_users():
    today = date.today()

    # User A: low income, high expenses, low savings, low risk
    create_user(
        name="Asha Kumar", email="asha@example.com", age=26, occupation="Retail Associate",
        profile_kwargs=dict(
            education_level="undergraduate", monthly_income=28000, monthly_expenses=26000,
            current_savings=15000, monthly_investment_contribution=500, emergency_fund=8000,
        ),
        months=6, income=28000,
        expense_profile={
            "rent": (9000, 9500), "food": (5000, 6500), "transport": (1500, 2200),
            "shopping": (2500, 4500), "entertainment": (1000, 2000), "utilities": (1200, 1600),
            "subscriptions": (300, 500),
        },
        goals=[
            dict(name="Emergency Fund", goal_type="emergency_fund", target_amount=100000, current_amount=8000,
                 target_date=today.replace(year=today.year + 1), priority=GoalPriority.high),
            dict(name="Debt Reduction", goal_type="debt_reduction", target_amount=40000, current_amount=5000,
                 target_date=today.replace(year=today.year + 1), priority=GoalPriority.high),
        ],
        loans=[
            dict(loan_type="personal_loan", principal_amount=50000, outstanding_amount=38000,
                 interest_rate=16.5, emi=4200, start_date=today - timedelta(days=300), tenure_months=18),
        ],
        insurances=[],
        investments=[
            dict(investment_type="fd", name="Bank FD", invested_amount=10000, current_value=10600,
                 start_date=today - timedelta(days=200)),
        ],
    )

    # User B: moderate income, balanced expenses, moderate risk
    create_user(
        name="Rohan Verma", email="rohan@example.com", age=34, occupation="Software Engineer",
        profile_kwargs=dict(
            education_level="postgraduate", monthly_income=85000, monthly_expenses=52000,
            current_savings=180000, monthly_investment_contribution=12000, emergency_fund=150000,
        ),
        months=6, income=85000,
        expense_profile={
            "rent": (20000, 20000), "food": (8000, 10000), "transport": (3000, 4000),
            "shopping": (4000, 7000), "entertainment": (2500, 4000), "utilities": (2500, 3000),
            "healthcare": (1000, 2500), "subscriptions": (800, 1200), "travel": (0, 6000),
        },
        goals=[
            dict(name="Home Purchase", goal_type="home_purchase", target_amount=2000000, current_amount=350000,
                 target_date=today.replace(year=today.year + 5), priority=GoalPriority.high),
            dict(name="Retirement", goal_type="retirement", target_amount=15000000, current_amount=600000,
                 target_date=today.replace(year=today.year + 25), priority=GoalPriority.medium),
            dict(name="Vacation", goal_type="custom", target_amount=150000, current_amount=60000,
                 target_date=today.replace(year=today.year + 1), priority=GoalPriority.low),
        ],
        loans=[
            dict(loan_type="car_loan", principal_amount=600000, outstanding_amount=410000,
                 interest_rate=9.2, emi=11800, start_date=today - timedelta(days=500), tenure_months=60),
        ],
        insurances=[
            dict(insurance_type="health", provider="StarHealth", coverage_amount=500000, premium_amount=14000,
                 premium_frequency="yearly", start_date=today - timedelta(days=400)),
        ],
        investments=[
            dict(investment_type="mutual_funds", name="Index Fund SIP", invested_amount=300000, current_value=352000,
                 start_date=today - timedelta(days=700)),
            dict(investment_type="ppf", name="PPF Account", invested_amount=200000, current_value=224000,
                 start_date=today - timedelta(days=900)),
            dict(investment_type="stocks", name="Equity Portfolio", invested_amount=120000, current_value=138000,
                 start_date=today - timedelta(days=300)),
        ],
    )

    # User C: high income, strong savings, higher risk tolerance
    create_user(
        name="Priya Sharma", email="priya@example.com", age=41, occupation="Product Manager",
        profile_kwargs=dict(
            education_level="postgraduate", monthly_income=220000, monthly_expenses=95000,
            current_savings=900000, monthly_investment_contribution=60000, emergency_fund=600000,
        ),
        months=6, income=220000,
        expense_profile={
            "rent": (35000, 35000), "food": (12000, 15000), "transport": (5000, 7000),
            "shopping": (8000, 15000), "entertainment": (5000, 9000), "utilities": (4000, 5000),
            "healthcare": (2000, 3500), "subscriptions": (1500, 2000), "travel": (0, 20000),
            "education": (0, 8000),
        },
        goals=[
            dict(name="Child Education", goal_type="education", target_amount=3000000, current_amount=800000,
                 target_date=today.replace(year=today.year + 8), priority=GoalPriority.high),
            dict(name="Retirement", goal_type="retirement", target_amount=40000000, current_amount=5000000,
                 target_date=today.replace(year=today.year + 20), priority=GoalPriority.high),
            dict(name="Second Home", goal_type="home_purchase", target_amount=5000000, current_amount=1200000,
                 target_date=today.replace(year=today.year + 6), priority=GoalPriority.medium),
        ],
        loans=[
            dict(loan_type="home_loan", principal_amount=4000000, outstanding_amount=2800000,
                 interest_rate=8.1, emi=32000, start_date=today - timedelta(days=1200), tenure_months=240),
        ],
        insurances=[
            dict(insurance_type="health", provider="HDFC Ergo", coverage_amount=1000000, premium_amount=22000,
                 premium_frequency="yearly", start_date=today - timedelta(days=600)),
            dict(insurance_type="life", provider="LIC", coverage_amount=10000000, premium_amount=45000,
                 premium_frequency="yearly", start_date=today - timedelta(days=800)),
        ],
        investments=[
            dict(investment_type="stocks", name="Equity Portfolio", invested_amount=1500000, current_value=1850000,
                 start_date=today - timedelta(days=1000)),
            dict(investment_type="mutual_funds", name="Diversified SIP", invested_amount=900000, current_value=1080000,
                 start_date=today - timedelta(days=900)),
            dict(investment_type="gold", name="Sovereign Gold Bonds", invested_amount=200000, current_value=240000,
                 start_date=today - timedelta(days=500)),
            dict(investment_type="crypto", name="Crypto Allocation", invested_amount=100000, current_value=115000,
                 start_date=today - timedelta(days=250)),
        ],
    )


if __name__ == "__main__":
    seed_questions()
    seed_users()
    db.close()
    print("\nSeed complete. Demo credentials (password: password123 for all):")
    print("  asha@example.com   - low income, high expenses, low risk")
    print("  rohan@example.com  - moderate income, balanced, moderate risk")
    print("  priya@example.com  - high income, strong savings, high risk tolerance")
