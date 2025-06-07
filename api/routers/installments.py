from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from api.schemas.misc import SimpleCount
from api.schemas.payment import PaymentCreate, RevenueTotal
from api.core.security import get_current_agent
from api.schemas import(
    installment as installment_schema,
    payment as payment_schema
)
from api.crud.crud_installment import installment as installments
from api.crud.crud_payment import payment as payments
from api.core.dependencies import get_db

router = APIRouter(prefix="/installments", tags=["installments"])




@router.get("/", response_model=List[installment_schema.InstallmentRead])
def list_installments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return installments.get_multi(db, skip=skip, limit=limit)


@router.get("/me", response_model=installment_schema.InstallmentRead)
def get_my_installment(
    db: Session = Depends(get_db),
    current=Depends(get_current_agent),
):
    return installments.get_active(db, agent_id=current.id)



@router.post("/", response_model=installment_schema.InstallmentRead)
def apply_installment(
    obj_in: installment_schema.InstallmentCreate,
    current=Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    return installments.apply(db, agent_id=current.id, obj_in=obj_in)

@router.patch("/{inst_id}/status", response_model=installment_schema.InstallmentRead)
def change_status(
    inst_id: int,
    obj_in: installment_schema.InstallmentUpdate,
    db: Session = Depends(get_db)
):
    inst = installments.get(db, id=inst_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Installment not found")
    return installments.set_status(db, db_obj=inst, status=obj_in.status)

@router.patch("/{inst_id}/pay", response_model=installment_schema.InstallmentRead)
def change_status(
    inst_id: int,
    amount: PaymentCreate,
    db: Session = Depends(get_db)
):
    inst = installments.get(db, id=inst_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Installment not found")
    return installments.pay_installment(db, installment_id=inst_id, pay_in=amount.amount)

@router.get("/{installment_id}/due", response_model=payment_schema.DueResponse)
def get_installment_due(
    installment_id: int,
    db: Session = Depends(get_db)
):
    due_info = installments.compute_due(db, installment_id)
    return due_info
@router.get("/pending", response_model=SimpleCount)
def pending_installments(db: Session = Depends(get_db)):
    return installments.pending_installments(db)


@router.get("/overdue-today", response_model=SimpleCount)
def overdue_payments(db: Session = Depends(get_db)):
    return installments.overdue_payments(db=db)

@router.get("/revenue-today", response_model=RevenueTotal)
def revenue_today(db: Session = Depends(get_db)):
    return installments.revenue_today(db=db)
@router.get("/payments/trend", response_model=list[payment_schema.TrendPoint])
def payment_trend(days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    
    return payments.payment_trend(db, days=days)