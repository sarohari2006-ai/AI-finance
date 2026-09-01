from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, Insurance
from app.schemas.schemas import InsuranceCreate, InsuranceOut
from app.auth.deps import get_current_user

router = APIRouter(prefix="/insurance", tags=["insurance"])


@router.get("", response_model=List[InsuranceOut])
def list_insurance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Insurance).filter(Insurance.user_id == current_user.id).all()


@router.post("", response_model=InsuranceOut, status_code=status.HTTP_201_CREATED)
def create_insurance(payload: InsuranceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    policy = Insurance(user_id=current_user.id, **payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{insurance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_insurance(insurance_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    policy = db.query(Insurance).filter(Insurance.id == insurance_id, Insurance.user_id == current_user.id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Insurance policy not found")
    db.delete(policy)
    db.commit()
    return None
