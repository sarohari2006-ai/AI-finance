from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.schemas.schemas import FinancialHealthOut
from app.auth.deps import get_current_user
from app.services.pipeline import build_context, compute_health_score

router = APIRouter(prefix="/financial-health", tags=["financial-health"])


@router.get("", response_model=FinancialHealthOut)
def get_financial_health(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    context = build_context(db, current_user)
    health = compute_health_score(context)
    return FinancialHealthOut(**health)
