from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from api.schemas.installment import InstallmentRead

class PaymentBase(BaseModel):
    amount: float

class PaymentCreate(PaymentBase):
    installment_id: Optional[int] = None

class PaymentRead(PaymentBase):
    installment_id: int
    payment_date: Optional[datetime]
    installment : Optional[InstallmentRead] = None

    class Config:
        from_attributes = True

class DueResponse(BaseModel):
    installment_id: int
    days_elapsed: int
    total_required_to_date: int
    total_paid_to_date: int
    owed_today: int

    class Config:
        from_attributes = True

class RevenueTotal(BaseModel):
    total : int

class TrendPoint(BaseModel):
    date: str
    amount: int