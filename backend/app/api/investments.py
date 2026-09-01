from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, Investment
from app.schemas.schemas import InvestmentCreate, InvestmentOut
from app.auth.deps import get_current_user

router = APIRouter(prefix="/investments", tags=["investments"])


def _to_out(inv: Investment) -> InvestmentOut:
    returns_pct = ((inv.current_value - inv.invested_amount) / inv.invested_amount * 100) if inv.invested_amount > 0 else 0.0
    return InvestmentOut(
        id=inv.id,
        user_id=inv.user_id,
        investment_type=inv.investment_type,
        name=inv.name,
        invested_amount=inv.invested_amount,
        current_value=inv.current_value,
        start_date=inv.start_date,
        returns_percentage=round(returns_pct, 2),
    )


@router.get("", response_model=List[InvestmentOut])
def list_investments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    investments = db.query(Investment).filter(Investment.user_id == current_user.id).all()
    return [_to_out(i) for i in investments]


@router.post("", response_model=InvestmentOut, status_code=status.HTTP_201_CREATED)
def create_investment(payload: InvestmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = Investment(user_id=current_user.id, **payload.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return _to_out(inv)


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(investment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == current_user.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    db.delete(inv)
    db.commit()
    return None
