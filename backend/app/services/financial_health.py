"""
Financial Health Score (0-100), a transparent weighted composite.

Weights (documented in docs/ai-recommendation.md):
  Savings behavior       25%
  Debt burden             20%
  Emergency fund          15%
  Goal progress           15%
  Spending discipline     10%
  Investment consistency  10%
  Insurance coverage       5%

Each component is scored 0-100 independently using a deterministic rule,
then combined via the fixed weights above. No ML/black-box element here —
this score must be fully explainable.
"""
from typing import Dict, Any, List

WEIGHTS = {
    "savings": 0.25,
    "debt": 0.20,
    "emergency_fund": 0.15,
    "goals": 0.15,
    "spending": 0.10,
    "investment": 0.10,
    "insurance": 0.05,
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def score_savings(savings_rate_pct: float) -> float:
    """20%+ savings rate -> 100. 0% or negative -> 0. Linear in between."""
    return _clamp((savings_rate_pct / 20.0) * 100)


def score_debt(debt_to_income_pct: float) -> float:
    """0% DTI -> 100. 40%+ DTI -> 0. Linear in between."""
    if debt_to_income_pct <= 0:
        return 100.0
    return _clamp(100 - (debt_to_income_pct / 40.0) * 100)


def score_emergency_fund(months_covered: float) -> float:
    """6 months of expenses covered -> 100. 0 months -> 0."""
    return _clamp((months_covered / 6.0) * 100)


def score_goals(avg_goal_progress_pct: float) -> float:
    return _clamp(avg_goal_progress_pct)


def score_spending(discretionary_ratio: float) -> float:
    """30% discretionary spending or lower -> 100. 70%+ -> 0."""
    if discretionary_ratio <= 0.3:
        return 100.0
    if discretionary_ratio >= 0.7:
        return 0.0
    return _clamp(100 - ((discretionary_ratio - 0.3) / 0.4) * 100)


def score_investment(investment_consistency: float) -> float:
    return _clamp(investment_consistency * 100)


def score_insurance(has_health: bool, has_life: bool) -> float:
    if has_health and has_life:
        return 100.0
    if has_health or has_life:
        return 50.0
    return 0.0


def category_label(score: float) -> str:
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Needs Attention"


def compute_financial_health(
    savings_rate_pct: float,
    debt_to_income_pct: float,
    emergency_fund_months: float,
    avg_goal_progress_pct: float,
    discretionary_ratio: float,
    investment_consistency: float,
    has_health_insurance: bool,
    has_life_insurance: bool,
) -> Dict[str, Any]:
    components = {
        "savings": round(score_savings(savings_rate_pct), 1),
        "debt": round(score_debt(debt_to_income_pct), 1),
        "emergency_fund": round(score_emergency_fund(emergency_fund_months), 1),
        "goals": round(score_goals(avg_goal_progress_pct), 1),
        "spending": round(score_spending(discretionary_ratio), 1),
        "investment": round(score_investment(investment_consistency), 1),
        "insurance": round(score_insurance(has_health_insurance, has_life_insurance), 1),
    }

    total = sum(components[k] * WEIGHTS[k] for k in WEIGHTS)
    total = round(_clamp(total), 1)

    explanation = {
        "savings": f"Savings rate of {savings_rate_pct:.1f}% (weight 25%).",
        "debt": f"Debt-to-income ratio of {debt_to_income_pct:.1f}% (weight 20%).",
        "emergency_fund": f"Emergency fund covers {emergency_fund_months:.1f} months of expenses (weight 15%).",
        "goals": f"Average goal progress is {avg_goal_progress_pct:.1f}% (weight 15%).",
        "spending": f"Discretionary spending is {discretionary_ratio * 100:.1f}% of expenses (weight 10%).",
        "investment": f"Investment contribution consistency is {investment_consistency * 100:.1f}% (weight 10%).",
        "insurance": "Based on whether health and life insurance policies are on file (weight 5%).",
    }

    return {
        "score": total,
        "category": category_label(total),
        "components": components,
        "explanation": explanation,
    }
