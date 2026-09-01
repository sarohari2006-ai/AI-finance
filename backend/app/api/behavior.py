from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.schemas.schemas import BehaviorAnalysisOut
from app.auth.deps import get_current_user
from app.services.pipeline import run_behavior_analysis
from app.analytics.behavior import generate_insights, FEATURE_NAMES

router = APIRouter(prefix="/behavior-analysis", tags=["behavior"])


@router.get("", response_model=BehaviorAnalysisOut)
def get_behavior_analysis(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = run_behavior_analysis(db, current_user)
    features = {name: getattr(analysis, name) for name in FEATURE_NAMES}
    insights = generate_insights(features, analysis.cluster_label)
    return BehaviorAnalysisOut(
        id=analysis.id,
        avg_monthly_spending=analysis.avg_monthly_spending,
        spending_volatility=analysis.spending_volatility,
        savings_consistency=analysis.savings_consistency,
        discretionary_ratio=analysis.discretionary_ratio,
        essential_ratio=analysis.essential_ratio,
        investment_consistency=analysis.investment_consistency,
        debt_burden=analysis.debt_burden,
        savings_rate=analysis.savings_rate,
        recurring_expense_ratio=analysis.recurring_expense_ratio,
        category_concentration=analysis.category_concentration,
        cluster_label=analysis.cluster_label,
        created_at=analysis.created_at,
        insights=insights,
    )
