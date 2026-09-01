"""
Deterministic financial calculations.

These are pure functions over user financial data — no ML, no randomness.
Every formula here is documented in docs/ai-recommendation.md.
"""
from datetime import date
from typing import List, Dict, Any

from app.models.models import Transaction, FinancialGoal, Loan, TransactionType

ESSENTIAL_CATEGORIES = {"rent", "utilities", "healthcare", "transport", "education"}
DISCRETIONARY_CATEGORIES = {"shopping", "entertainment", "travel", "subscriptions", "other", "food"}


def total_income(transactions: List[Transaction]) -> float:
    return sum(t.amount for t in transactions if t.type == TransactionType.income)


def total_expenses(transactions: List[Transaction]) -> float:
    return sum(t.amount for t in transactions if t.type == TransactionType.expense)


def savings_rate(income: float, expenses: float) -> float:
    """(income - expenses) / income, as a percentage. 0 if income is 0."""
    if income <= 0:
        return 0.0
    return round(max((income - expenses) / income, -1.0) * 100, 2)


def spending_by_category(transactions: List[Transaction]) -> Dict[str, float]:
    result: Dict[str, float] = {}
    for t in transactions:
        if t.type == TransactionType.expense:
            result[t.category] = round(result.get(t.category, 0.0) + t.amount, 2)
    return result


def essential_vs_discretionary(transactions: List[Transaction]) -> Dict[str, float]:
    essential = sum(t.amount for t in transactions if t.type == TransactionType.expense and t.category in ESSENTIAL_CATEGORIES)
    discretionary = sum(t.amount for t in transactions if t.type == TransactionType.expense and t.category not in ESSENTIAL_CATEGORIES)
    total = essential + discretionary
    return {
        "essential": round(essential, 2),
        "discretionary": round(discretionary, 2),
        "essential_ratio": round(essential / total, 4) if total > 0 else 0.0,
        "discretionary_ratio": round(discretionary / total, 4) if total > 0 else 0.0,
    }


def emergency_fund_months(emergency_fund: float, monthly_expenses: float) -> float:
    if monthly_expenses <= 0:
        return 0.0
    return round(emergency_fund / monthly_expenses, 2)


def debt_to_income_ratio(total_emi: float, monthly_income: float) -> float:
    if monthly_income <= 0:
        return 0.0
    return round((total_emi / monthly_income) * 100, 2)


def goal_progress(goal: FinancialGoal) -> Dict[str, Any]:
    progress_pct = 0.0
    if goal.target_amount > 0:
        progress_pct = round(min(goal.current_amount / goal.target_amount, 1.0) * 100, 2)

    remaining = max(goal.target_amount - goal.current_amount, 0.0)

    today = date.today()
    months_remaining = max(
        (goal.target_date.year - today.year) * 12 + (goal.target_date.month - today.month), 1
    )
    recommended_monthly = round(remaining / months_remaining, 2) if months_remaining > 0 else remaining

    return {
        "progress_percentage": progress_pct,
        "remaining_amount": round(remaining, 2),
        "recommended_monthly_contribution": recommended_monthly,
        "months_remaining": months_remaining,
    }


def total_monthly_emi(loans: List[Loan]) -> float:
    return round(sum(l.emi for l in loans), 2)


def total_investment_value(investments) -> Dict[str, float]:
    invested = sum(i.invested_amount for i in investments)
    current = sum(i.current_value for i in investments)
    returns_pct = round(((current - invested) / invested) * 100, 2) if invested > 0 else 0.0
    return {"invested": round(invested, 2), "current_value": round(current, 2), "returns_percentage": returns_pct}


def monthly_series(transactions: List[Transaction], months: int = 6) -> List[Dict[str, Any]]:
    """Group income/expense totals by calendar month for the last `months` months."""
    from collections import defaultdict

    buckets: Dict[str, Dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in transactions:
        key = f"{t.date.year:04d}-{t.date.month:02d}"
        if t.type == TransactionType.income:
            buckets[key]["income"] += t.amount
        else:
            buckets[key]["expense"] += t.amount

    sorted_keys = sorted(buckets.keys())[-months:]
    return [
        {
            "month": k,
            "income": round(buckets[k]["income"], 2),
            "expense": round(buckets[k]["expense"], 2),
            "savings": round(buckets[k]["income"] - buckets[k]["expense"], 2),
        }
        for k in sorted_keys
    ]
