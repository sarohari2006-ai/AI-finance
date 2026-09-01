import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, RiskQuestion, RiskAssessment, RiskLevel
from app.schemas.schemas import RiskQuestionOut, RiskSubmit, RiskResultOut
from app.auth.deps import get_current_user

router = APIRouter(prefix="/risk", tags=["risk"])


def _classify_risk(avg_score: float) -> RiskLevel:
    if avg_score >= 3.25:
        return RiskLevel.high
    if avg_score >= 2.25:
        return RiskLevel.moderate
    return RiskLevel.low


@router.get("/questions", response_model=List[RiskQuestionOut])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(RiskQuestion).all()
    return [
        RiskQuestionOut(id=q.id, question=q.question, options=json.loads(q.options), factor=q.factor)
        for q in questions
    ]


@router.post("/submit", response_model=RiskResultOut)
def submit_answers(payload: RiskSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.answers:
        raise HTTPException(status_code=400, detail="No answers submitted")

    questions = db.query(RiskQuestion).filter(RiskQuestion.id.in_(payload.answers.keys())).all()
    if not questions:
        raise HTTPException(status_code=400, detail="No matching questions found")

    total_score = 0
    count = 0
    for q in questions:
        options = json.loads(q.options)
        idx = payload.answers.get(q.id)
        if idx is None or idx < 0 or idx >= len(options):
            continue
        total_score += options[idx]["score"]
        count += 1

    if count == 0:
        raise HTTPException(status_code=400, detail="No valid answers submitted")

    avg_score = total_score / count
    risk_level = _classify_risk(avg_score)

    assessment = RiskAssessment(
        user_id=current_user.id,
        total_score=round(total_score, 2),
        risk_level=risk_level,
        answers=json.dumps({str(k): v for k, v in payload.answers.items()}),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return RiskResultOut(
        id=assessment.id,
        total_score=assessment.total_score,
        risk_level=assessment.risk_level.value,
        created_at=assessment.created_at,
    )


@router.get("/result", response_model=RiskResultOut)
def get_latest_result(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.user_id == current_user.id)
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="No risk assessment found")
    return RiskResultOut(
        id=assessment.id,
        total_score=assessment.total_score,
        risk_level=assessment.risk_level.value,
        created_at=assessment.created_at,
    )
