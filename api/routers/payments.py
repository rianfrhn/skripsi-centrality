from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from schemas import(
    payment as payment_schema
)
from crud.crud_payment import payment as payments
from core.dependencies import get_db, get_current_active_agent

router = APIRouter(prefix="/installments/{inst_id}/payments", tags=["payments"])
router2 = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=List[payment_schema.PaymentRead])
def list_payments(inst_id: int, db: Session = Depends(get_db)):
    return payments.get_multi(db, skip=0, limit=100)

@router.post("/", response_model=payment_schema.PaymentRead)
def create_payment(
    inst_id: int,
    obj_in: payment_schema.PaymentCreate,
    current=Depends(get_current_active_agent),
    db: Session = Depends(get_db)
):
    return payments.create(db, obj_in=obj_in, installment_id=inst_id)

@router2.get("/recent", response_model=list[payment_schema.PaymentRead])
def recent_payments(limit: int = Query(5, ge=1, le=20), db: Session = Depends(get_db)):
    return payments.recent_payments(db=db, limit=limit)


