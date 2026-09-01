import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, Recommendation
from app.schemas.schemas import RecommendationOut
from app.auth.deps import get_current_user
from app.services.pipeline import refresh_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _to_out(rec: Recommendation) -> RecommendationOut:
    return RecommendationOut(
        id=rec.id,
        title=rec.title,
        category=rec.category,
        recommendation=rec.recommendation,
        priority=rec.priority,
        reason=rec.reason,
        supporting_metrics=json.loads(rec.supporting_metrics) if rec.supporting_metrics else None,
        expected_benefit=rec.expected_benefit,
        action=rec.action,
        explanation_type=rec.explanation_type,
        is_read=rec.is_read,
        created_at=rec.created_at,
    )


@router.get("", response_model=List[RecommendationOut])
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = refresh_recommendations(db, current_user)
    return [_to_out(r) for r in records]


@router.get("/{recommendation_id}", response_model=RecommendationOut)
def get_recommendation(recommendation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id, Recommendation.user_id == current_user.id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.is_read = True
    db.commit()
    db.refresh(rec)
    return _to_out(rec)
