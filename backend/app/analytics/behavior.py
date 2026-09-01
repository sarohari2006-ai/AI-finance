"""
Behavioral analytics: feature engineering over transaction history plus
K-Means clustering to segment users into behavioral archetypes.

This is the ML layer of the pipeline. Feature definitions are deterministic
(pandas/numpy); the segmentation label itself comes from an unsupervised
K-Means model refit against reference archetype centroids so a single user's
data can still be classified meaningfully without a large training set.
"""
from collections import defaultdict
from datetime import date
from typing import List, Dict, Any

import numpy as np
from sklearn.cluster import KMeans

from app.models.models import Transaction, TransactionType, Loan, FinancialProfile
from app.services.calculations import ESSENTIAL_CATEGORIES

FEATURE_NAMES = [
    "savings_rate",
    "discretionary_ratio",
    "essential_ratio",
    "spending_volatility",
    "savings_consistency",
    "debt_burden",
    "investment_consistency",
    "recurring_expense_ratio",
    "category_concentration",
]

# Reference archetype centroids in the same feature space (hand-defined from
# domain knowledge, used to seed/label the K-Means clusters deterministically).
ARCHETYPES = {
    "Disciplined Saver": [0.30, 0.25, 0.75, 0.15, 0.85, 0.10, 0.70, 0.30, 0.25],
    "High Discretionary Spender": [0.05, 0.55, 0.45, 0.35, 0.30, 0.15, 0.20, 0.25, 0.35],
    "Inconsistent Saver": [0.10, 0.35, 0.65, 0.55, 0.20, 0.20, 0.15, 0.30, 0.30],
    "Debt-Heavy": [0.02, 0.30, 0.70, 0.30, 0.40, 0.55, 0.10, 0.40, 0.30],
    "Balanced Planner": [0.20, 0.30, 0.70, 0.20, 0.70, 0.15, 0.55, 0.35, 0.20],
}
ARCHETYPE_NAMES = list(ARCHETYPES.keys())
ARCHETYPE_MATRIX = np.array(list(ARCHETYPES.values()))


def _monthly_buckets(transactions: List[Transaction]) -> Dict[str, Dict[str, float]]:
    buckets: Dict[str, Dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in transactions:
        key = f"{t.date.year:04d}-{t.date.month:02d}"
        if t.type == TransactionType.income:
            buckets[key]["income"] += t.amount
        else:
            buckets[key]["expense"] += t.amount
    return buckets


def compute_features(
    transactions: List[Transaction],
    loans: List[Loan],
    profile: FinancialProfile,
    investment_months_active: int = 0,
    total_months_tracked: int = 1,
) -> Dict[str, float]:
    """Compute the 9 behavioral features used for clustering and display."""
    expense_txns = [t for t in transactions if t.type == TransactionType.expense]
    income_txns = [t for t in transactions if t.type == TransactionType.income]

    total_expense = sum(t.amount for t in expense_txns)
    total_income_amt = sum(t.amount for t in income_txns)

    essential = sum(t.amount for t in expense_txns if t.category in ESSENTIAL_CATEGORIES)
    discretionary = total_expense - essential

    essential_ratio = essential / total_expense if total_expense > 0 else 0.0
    discretionary_ratio = discretionary / total_expense if total_expense > 0 else 0.0

    monthly = _monthly_buckets(transactions)
    monthly_expenses = np.array([v["expense"] for v in monthly.values()]) if monthly else np.array([0.0])
    monthly_income = np.array([v["income"] for v in monthly.values()]) if monthly else np.array([0.0])
    monthly_savings = monthly_income - monthly_expenses

    avg_monthly_spending = float(np.mean(monthly_expenses)) if len(monthly_expenses) else 0.0
    spending_volatility = float(np.std(monthly_expenses) / avg_monthly_spending) if avg_monthly_spending > 0 else 0.0
    spending_volatility = min(spending_volatility, 1.0)

    positive_months = int(np.sum(monthly_savings > 0))
    savings_consistency = positive_months / len(monthly_savings) if len(monthly_savings) else 0.0

    savings_rate_val = (total_income_amt - total_expense) / total_income_amt if total_income_amt > 0 else 0.0
    savings_rate_val = max(min(savings_rate_val, 1.0), -1.0)

    total_emi = sum(l.emi for l in loans)
    debt_burden = total_emi / profile.monthly_income if profile and profile.monthly_income > 0 else 0.0
    debt_burden = min(debt_burden, 1.0)

    investment_consistency = min(investment_months_active / total_months_tracked, 1.0) if total_months_tracked else 0.0

    category_totals: Dict[str, float] = defaultdict(float)
    for t in expense_txns:
        category_totals[t.category] += t.amount
    if total_expense > 0 and category_totals:
        shares = np.array(list(category_totals.values())) / total_expense
        category_concentration = float(np.sum(shares ** 2))  # Herfindahl index
    else:
        category_concentration = 0.0

    recurring_categories = {"rent", "utilities", "subscriptions", "insurance"}
    recurring_amount = sum(t.amount for t in expense_txns if t.category in recurring_categories)
    recurring_expense_ratio = recurring_amount / total_expense if total_expense > 0 else 0.0

    return {
        "avg_monthly_spending": round(avg_monthly_spending, 2),
        "spending_volatility": round(spending_volatility, 4),
        "savings_consistency": round(savings_consistency, 4),
        "discretionary_ratio": round(discretionary_ratio, 4),
        "essential_ratio": round(essential_ratio, 4),
        "investment_consistency": round(investment_consistency, 4),
        "debt_burden": round(debt_burden, 4),
        "savings_rate": round(savings_rate_val, 4),
        "recurring_expense_ratio": round(recurring_expense_ratio, 4),
        "category_concentration": round(category_concentration, 4),
    }


def classify_behavior(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Assign a behavioral archetype by fitting a K-Means model over the
    reference archetype centroids plus the user's feature vector, then
    picking the nearest cluster centroid to the user's point.
    """
    vector = np.array([[features[name] for name in FEATURE_NAMES]])

    data = np.vstack([ARCHETYPE_MATRIX, vector])
    n_clusters = len(ARCHETYPE_NAMES)
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = kmeans.fit_predict(data)

    user_cluster = int(labels[-1])

    # Map each cluster id to the archetype name whose reference point falls in it
    cluster_to_archetype = {}
    for idx, name in enumerate(ARCHETYPE_NAMES):
        cluster_to_archetype[int(labels[idx])] = name

    label = cluster_to_archetype.get(user_cluster, "Balanced Planner")

    return {"cluster_id": user_cluster, "cluster_label": label}


def generate_insights(features: Dict[str, float], label: str) -> List[str]:
    insights = []
    insights.append(
        f"Discretionary spending represents {features['discretionary_ratio'] * 100:.0f}% of your monthly expenses."
    )
    insights.append(
        f"Essential spending represents {features['essential_ratio'] * 100:.0f}% of your monthly expenses."
    )
    insights.append(
        f"Your savings rate is {features['savings_rate'] * 100:.0f}%."
    )
    if features["debt_burden"] > 0:
        insights.append(f"Loan EMIs consume {features['debt_burden'] * 100:.0f}% of your monthly income.")
    if features["spending_volatility"] > 0.3:
        insights.append("Your month-to-month spending varies significantly, which can make budgeting harder.")
    if features["savings_consistency"] < 0.5:
        insights.append("You save in fewer than half of tracked months — consistency could improve.")
    return insights
