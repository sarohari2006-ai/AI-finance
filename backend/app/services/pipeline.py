"""
Orchestrates the full data pipeline for a user:

  raw data -> validation (schemas) -> calculations -> behavioral analysis ->
  financial health -> recommendation engine -> persistence

Documented in docs/architecture.md.
"""
from datetime import date
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.models import (
    User, Transaction, FinancialGoal, Loan, Insurance, Investment,
    BehaviorAnalysis, Recommendation, RiskAssessment, LiteracyAttempt,
)
from app.services import calculations as calc
from app.services.financial_health import compute_financial_health
from app.analytics.behavior import compute_features, classify_behavior, generate_insights
from app.ml.recommendation_engine import generate_recommendations


def get_or_create_profile(db: Session, user: User):
    from app.models.models import FinancialProfile
    if user.profile:
        return user.profile
    profile = FinancialProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def run_behavior_analysis(db: Session, user: User) -> BehaviorAnalysis:
    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    loans = db.query(Loan).filter(Loan.user_id == user.id).all()
    investments = db.query(Investment).filter(Investment.user_id == user.id).all()
    profile = get_or_create_profile(db, user)

    months_tracked = len({f"{t.date.year}-{t.date.month}" for t in transactions}) or 1
    investment_months_active = min(len(investments), months_tracked)

    features = compute_features(
        transactions=transactions,
        loans=loans,
        profile=profile,
        investment_months_active=investment_months_active,
        total_months_tracked=months_tracked,
    )
    cluster = classify_behavior(features)

    analysis = BehaviorAnalysis(
        user_id=user.id,
        cluster_label=cluster["cluster_label"],
        cluster_id=cluster["cluster_id"],
        **features,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def build_context(db: Session, user: User) -> Dict[str, Any]:
    """Assemble the full context dict used by financial health + recommendation engine."""
    profile = get_or_create_profile(db, user)
    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    loans = db.query(Loan).filter(Loan.user_id == user.id).all()
    insurances = db.query(Insurance).filter(Insurance.user_id == user.id).all()
    investments = db.query(Investment).filter(Investment.user_id == user.id).all()
    goals = db.query(FinancialGoal).filter(FinancialGoal.user_id == user.id).all()

    income = calc.total_income(transactions) or profile.monthly_income
    expenses = calc.total_expenses(transactions) or profile.monthly_expenses
    # Prefer profile monthly figures if transaction history is sparse
    monthly_income = profile.monthly_income if profile.monthly_income > 0 else income
    monthly_expenses = profile.monthly_expenses if profile.monthly_expenses > 0 else expenses

    savings_rate_pct = calc.savings_rate(monthly_income, monthly_expenses)
    ev_d = calc.essential_vs_discretionary(transactions)
    emergency_months = calc.emergency_fund_months(profile.emergency_fund, monthly_expenses)
    total_emi = calc.total_monthly_emi(loans)
    dti = calc.debt_to_income_ratio(total_emi, monthly_income)
    inv_totals = calc.total_investment_value(investments)

    goal_dicts = []
    for g in goals:
        gp = calc.goal_progress(g)
        goal_dicts.append({
            "id": g.id,
            "user_id": g.user_id,
            "name": g.name,
            "goal_type": g.goal_type,
            "target_amount": g.target_amount,
            "current_amount": g.current_amount,
            "target_date": g.target_date.isoformat(),
            "priority": g.priority.value if hasattr(g.priority, "value") else g.priority,
            "status": g.status.value if hasattr(g.status, "value") else g.status,
            **gp,
        })

    avg_goal_progress = sum(g["progress_percentage"] for g in goal_dicts) / len(goal_dicts) if goal_dicts else 100.0

    latest_risk = db.query(RiskAssessment).filter(RiskAssessment.user_id == user.id).order_by(RiskAssessment.created_at.desc()).first()
    latest_literacy = db.query(LiteracyAttempt).filter(LiteracyAttempt.user_id == user.id).order_by(LiteracyAttempt.created_at.desc()).first()
    latest_behavior = db.query(BehaviorAnalysis).filter(BehaviorAnalysis.user_id == user.id).order_by(BehaviorAnalysis.created_at.desc()).first()

    has_health = any(i.insurance_type == "health" for i in insurances)
    has_life = any(i.insurance_type == "life" for i in insurances)

    context = {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "savings_rate_pct": savings_rate_pct,
        "emergency_fund": profile.emergency_fund,
        "emergency_fund_months": emergency_months,
        "discretionary_ratio": ev_d["discretionary_ratio"],
        "discretionary_amount": ev_d["discretionary"],
        "total_emi": total_emi,
        "debt_to_income_pct": dti,
        "loans": [{"loan_type": l.loan_type, "interest_rate": l.interest_rate, "emi": l.emi, "outstanding_amount": l.outstanding_amount} for l in loans],
        "investments": [{"investment_type": i.investment_type, "invested_amount": i.invested_amount, "current_value": i.current_value} for i in investments],
        "investment_total": inv_totals["current_value"],
        "investment_contribution": profile.monthly_investment_contribution,
        "risk_level": latest_risk.risk_level.value if latest_risk and hasattr(latest_risk.risk_level, "value") else (latest_risk.risk_level if latest_risk else None),
        "literacy_level": latest_literacy.level.value if latest_literacy and hasattr(latest_literacy.level, "value") else (latest_literacy.level if latest_literacy else None),
        "goals": goal_dicts,
        "behavior_label": latest_behavior.cluster_label if latest_behavior else None,
        "has_health_insurance": has_health,
        "has_life_insurance": has_life,
        "avg_goal_progress_pct": avg_goal_progress,
    }
    return context


def compute_health_score(context: Dict[str, Any]) -> Dict[str, Any]:
    return compute_financial_health(
        savings_rate_pct=context["savings_rate_pct"],
        debt_to_income_pct=context["debt_to_income_pct"],
        emergency_fund_months=context["emergency_fund_months"],
        avg_goal_progress_pct=context["avg_goal_progress_pct"],
        discretionary_ratio=context["discretionary_ratio"],
        investment_consistency=min(context["investment_contribution"] / context["monthly_income"], 1.0) if context["monthly_income"] > 0 else 0.0,
        has_health_insurance=context["has_health_insurance"],
        has_life_insurance=context["has_life_insurance"],
    )


def refresh_recommendations(db: Session, user: User) -> List[Recommendation]:
    context = build_context(db, user)
    health = compute_health_score(context)
    context["financial_health_score"] = health["score"]

    rec_dicts = generate_recommendations(context)

    # Replace existing recommendations with freshly computed ones
    db.query(Recommendation).filter(Recommendation.user_id == user.id).delete()

    import json
    records = []
    for r in rec_dicts:
        rec = Recommendation(
            user_id=user.id,
            title=r["title"],
            category=r["category"],
            recommendation=r["recommendation"],
            priority=r["priority"],
            reason=r["reason"],
            supporting_metrics=json.dumps(r.get("supporting_metrics", {}), default=str),
            expected_benefit=r.get("expected_benefit"),
            action=r["action"],
            explanation_type=r.get("explanation_type", "rule_based"),
        )
        db.add(rec)
        records.append(rec)

    db.commit()
    for r in records:
        db.refresh(r)
    return records
