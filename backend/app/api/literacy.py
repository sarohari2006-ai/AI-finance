import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, LiteracyQuestion, LiteracyAttempt, LiteracyLevel
from app.schemas.schemas import LiteracyQuestionOut, LiteracySubmit, LiteracyResultOut
from app.auth.deps import get_current_user

router = APIRouter(prefix="/literacy", tags=["literacy"])


def _classify_level(pct: float) -> LiteracyLevel:
    if pct >= 85:
        return LiteracyLevel.advanced
    if pct >= 65:
        return LiteracyLevel.intermediate
    if pct >= 40:
        return LiteracyLevel.basic
    return LiteracyLevel.beginner


@router.get("/questions", response_model=List[LiteracyQuestionOut])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(LiteracyQuestion).all()
    return [
        LiteracyQuestionOut(id=q.id, question=q.question, options=json.loads(q.options), topic=q.topic)
        for q in questions
    ]


@router.post("/submit", response_model=LiteracyResultOut)
def submit_answers(payload: LiteracySubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.answers:
        raise HTTPException(status_code=400, detail="No answers submitted")

    questions = db.query(LiteracyQuestion).filter(LiteracyQuestion.id.in_(payload.answers.keys())).all()
    if not questions:
        raise HTTPException(status_code=400, detail="No matching questions found")

    correct_count = 0
    breakdown = []
    for q in questions:
        user_answer = payload.answers.get(q.id)
        is_correct = user_answer == q.correct_answer
        if is_correct:
            correct_count += 1
        breakdown.append({
            "question_id": q.id,
            "question": q.question,
            "your_answer": user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "explanation": q.explanation,
        })

    total = len(questions)
    pct = round((correct_count / total) * 100, 2) if total else 0.0
    level = _classify_level(pct)

    attempt = LiteracyAttempt(
        user_id=current_user.id,
        score_percentage=pct,
        level=level,
        answers=json.dumps({str(k): v for k, v in payload.answers.items()}),
        total_questions=total,
        correct_count=correct_count,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return LiteracyResultOut(
        id=attempt.id,
        score_percentage=attempt.score_percentage,
        level=attempt.level.value,
        total_questions=attempt.total_questions,
        correct_count=attempt.correct_count,
        created_at=attempt.created_at,
        breakdown=breakdown,
    )


@router.get("/result", response_model=LiteracyResultOut)
def get_latest_result(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attempt = (
        db.query(LiteracyAttempt)
        .filter(LiteracyAttempt.user_id == current_user.id)
        .order_by(LiteracyAttempt.created_at.desc())
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="No literacy assessment found")
    return LiteracyResultOut(
        id=attempt.id,
        score_percentage=attempt.score_percentage,
        level=attempt.level.value,
        total_questions=attempt.total_questions,
        correct_count=attempt.correct_count,
        created_at=attempt.created_at,
    )
