from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import models
from schemas import payment as payment_schema
from .crud_base import CRUDBase

class CRUDPayment(CRUDBase[models.InstallmentPayment, payment_schema.PaymentCreate, payment_schema.PaymentBase]):
    def create(self, db: Session, *, obj_in: payment_schema.PaymentCreate, installment_id: int):
        payment = models.InstallmentPayment(
            installment_id=installment_id,
            amount=obj_in.amount,
            payment_date=datetime.utcnow(),
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    
    def payment_trend(self, db: Session, *, days: int):
        """
        Daily total payments for the last `days` days.
        """
        end = date.today()
        start = end - timedelta(days=days - 1)
        # grouping by date
        rows = (
            db.query(
                func.date(models.InstallmentPayment.payment_date).label("date"),
                func.coalesce(func.sum(models.InstallmentPayment.amount), 0).label("amount"),
            )
            .filter(
                models.InstallmentPayment.payment_date >= datetime.combine(start, datetime.min.time()),
                models.InstallmentPayment.payment_date < datetime.combine(end + timedelta(days=1), datetime.min.time()),
            )
            .group_by(func.date(models.InstallmentPayment.payment_date))
            .order_by(func.date(models.InstallmentPayment.payment_date))
            .all()
        )
        data = {r.date: r.amount for r in rows}
        result = []
        for i in range(days):
            d = start + timedelta(days=i)
            result.append({"date": d.isoformat(), "amount": data.get(d, 0)})
        return result
    
    def recent_payments(self, db, *, limit: int):
        return db.query(models.InstallmentPayment).order_by(models.InstallmentPayment.payment_date.desc()).limit(limit)
    """
        rows = (
            db.query(
                models.InstallmentPayment.payment_date,
                models.Installment.agent_id,
                models.InstallmentPayment.amount,
                models.InstallmentPayment.installment_id,
            )
            .join(models.Installment, models.Installment.id == models.InstallmentPayment.installment_id)
            .order_by(models.InstallmentPayment.payment_date.desc())
            .limit(limit)
            .all()
        )
        return [
            payment_schema.PaymentRead(amount=r.amount, installment_id=r.installment_id, payment_date=r.payment_date.isoformat())
            for r in rows
        ]
        """

payment = CRUDPayment(models.InstallmentPayment)