import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, Transaction, BehaviorAnalysis, RiskAssessment, LiteracyAttempt, Notification
from app.schemas.schemas import DashboardOut, GoalOut, RecommendationOut, BehaviorAnalysisOut, NotificationOut
from app.auth.deps import get_current_user
from app.services.pipeline import build_context, compute_health_score, refresh_recommendations
from app.services.calculations import spending_by_category, monthly_series
from app.services.notifications import generate_alerts
from app.analytics.behavior import generate_insights, FEATURE_NAMES

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    context = build_context(db, current_user)
    health = compute_health_score(context)

    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    spend_by_cat = spending_by_category(transactions)
    trend = monthly_series(transactions, months=6)

    savings_trend = [{"month": m["month"], "savings": m["savings"]} for m in trend]

    from app.models.models import Investment
    investments = db.query(Investment).filter(Investment.user_id == current_user.id).order_by(Investment.start_date).all()
    investment_trend = []
    running_total = 0.0
    for inv in investments:
        running_total += inv.current_value
        investment_trend.append({
            "date": inv.start_date.isoformat() if inv.start_date else None,
            "cumulative_value": round(running_total, 2),
        })

    recommendations = refresh_recommendations(db, current_user)
    top_recs = recommendations[:5]

    rec_out = [
        RecommendationOut(
            id=r.id, title=r.title, category=r.category, recommendation=r.recommendation,
            priority=r.priority, reason=r.reason,
            supporting_metrics=json.loads(r.supporting_metrics) if r.supporting_metrics else None,
            expected_benefit=r.expected_benefit, action=r.action,
            explanation_type=r.explanation_type, is_read=r.is_read, created_at=r.created_at,
        ) for r in top_recs
    ]

    latest_behavior = db.query(BehaviorAnalysis).filter(BehaviorAnalysis.user_id == current_user.id).order_by(BehaviorAnalysis.created_at.desc()).first()
    behavior_out = None
    if latest_behavior:
        features = {name: getattr(latest_behavior, name) for name in FEATURE_NAMES}
        insights = generate_insights(features, latest_behavior.cluster_label)
        behavior_out = BehaviorAnalysisOut(
            id=latest_behavior.id,
            avg_monthly_spending=latest_behavior.avg_monthly_spending,
            spending_volatility=latest_behavior.spending_volatility,
            savings_consistency=latest_behavior.savings_consistency,
            discretionary_ratio=latest_behavior.discretionary_ratio,
            essential_ratio=latest_behavior.essential_ratio,
            investment_consistency=latest_behavior.investment_consistency,
            debt_burden=latest_behavior.debt_burden,
            savings_rate=latest_behavior.savings_rate,
            recurring_expense_ratio=latest_behavior.recurring_expense_ratio,
            category_concentration=latest_behavior.category_concentration,
            cluster_label=latest_behavior.cluster_label,
            created_at=latest_behavior.created_at,
            insights=insights,
        )

    alerts = generate_alerts(db, current_user, context)
    recent_alerts = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )

    goals_out = [GoalOut(**{k: v for k, v in g.items() if k != "months_remaining"}) for g in context["goals"]]

    return DashboardOut(
        financial_health=health,
        monthly_income=context["monthly_income"],
        monthly_expenses=context["monthly_expenses"],
        monthly_savings=round(context["monthly_income"] - context["monthly_expenses"], 2),
        savings_rate=context["savings_rate_pct"],
        spending_by_category=spend_by_cat,
        income_vs_expense_trend=trend,
        savings_trend=savings_trend,
        investment_trend=investment_trend,
        goals=goals_out,
        top_recommendations=rec_out,
        behavior_profile=behavior_out,
        risk_level=context["risk_level"],
        literacy_level=context["literacy_level"],
        alerts=recent_alerts,
    )
