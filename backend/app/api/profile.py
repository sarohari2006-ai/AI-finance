from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.schemas.schemas import FinancialProfileOut, FinancialProfileUpdate
from app.auth.deps import get_current_user
from app.services.pipeline import get_or_create_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=FinancialProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_or_create_profile(db, current_user)


@router.put("", response_model=FinancialProfileOut)
def update_profile(
    payload: FinancialProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
