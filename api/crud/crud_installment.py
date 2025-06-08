from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from api.schemas.misc import SimpleCount
from api import models
from api.schemas import(
    installment as installment_schema,
    payment as payment_schema
)
from .crud_payment import payment as payments
from .crud_base import CRUDBase
DAILY_REQUIRED = 50000
class CRUDInstallment(CRUDBase[models.Installment, installment_schema.InstallmentCreate, installment_schema.InstallmentUpdate]):
    def apply(self, db: Session, *, agent_id: int, obj_in: installment_schema.InstallmentCreate):
        inst = models.Installment(
            agent_id=agent_id,
            vehicle_id=obj_in.vehicle_id,
            installment_duration=obj_in.installment_duration,
            remaining_duration=obj_in.installment_duration,
            status="Pending",
        )
        db.add(inst)
        db.commit()
        db.refresh(inst)
        return inst

    def set_status(self, db: Session, *, db_obj: models.Installment, status: str):
        db_obj.status = status
        if status == "Accepted":
            db_obj.accepted_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def installment_paid(self, db:Session, *, db_obj: models.Installment, paid_amount : int):
        if(db_obj.total_paid == None): db_obj.total_paid = 0
        
        db_obj.total_paid += paid_amount
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    
    def get_active(self, db: Session, *, agent_id: int):
        return db.query(self.model).filter(
            and_(self.model.agent_id == agent_id, or_(self.model.status == "Pending", self.model.status == "Accepted"))
        ).one_or_none()
    
    def apply_for_installment(
        self,
        db: Session,
        *,
        payload: installment_schema.InstallmentCreate,
        current_agent: models.Agent,
    ):
        # 1) Make sure the vehicle exists and has stock, if you want:
        vehicle = db.query(models.Vehicle).get(payload.vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # 2) Create the installment
        inst = models.Installment(
            agent_id=current_agent.id,
            vehicle_id=payload.vehicle_id,
            total_paid=0,
            installment_duration=payload.installment_duration,
            remaining_duration=payload.installment_duration,
            status="Pending",
            applied_at=datetime.utcnow(),
        )
        db.add(inst)
        db.commit()
        db.refresh(inst)

        return inst
    

    def pay_installment(
        self,
        db: Session,
        installment_id: int,
        pay_in: int
    ) -> installment_schema:
        inst = self.get(db, installment_id)

        if inst.status != "Accepted":
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Cannot pay: installment is not active."
            )
        if(inst.vehicle == None):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Vehicle not found."
            )
        if pay_in >= inst.vehicle.price:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Cannot pay: installment is fully paid."
            )
        if(inst.total_paid == None): inst.total_paid = pay_in
        else:
            inst.total_paid += pay_in
            if(inst.total_paid >= inst.vehicle.price): inst.status = "Completed"
        """
        # Subtract either 1 or the provided `days`
        to_subtract = pay_in.days if pay_in.days and pay_in.days > 0 else 1

        if to_subtract > inst.remaining_duration:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Cannot subtract {to_subtract} days: only {inst.remaining_duration} remaining."
            )

        inst.remaining_duration -= to_subtract

        # Optionally: if remaining_duration becomes zero, you could auto‐update status to “Completed”
        if inst.remaining_duration == 0:
            inst.status = "Completed"
        """
        db.add(inst)
        payments.create(db, obj_in=payment_schema.PaymentCreate(amount=pay_in), installment_id=inst.id)



        db.commit()
        db.refresh(inst)
        return inst
    
    def compute_due(self, db: Session, installment_id: int) -> payment_schema.DueResponse:
        inst = self.get(db, installment_id)

        if not inst.accepted_at:
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail="Cicilan belum diterima / belum ada waktu penerimaan")

        # 1) Determine how many days have elapsed (inclusive of accepted_at date)
        start_date = inst.accepted_at.date()
        today_date = date.today()
        days_elapsed = (today_date - start_date).days + 1
        if days_elapsed < 1:
            days_elapsed = 1

        # 2) Total required up to today
        total_required_to_date = days_elapsed * DAILY_REQUIRED

        # 3) Sum all payments up to end of today (we include payments whose payment_date < tomorrow midnight)
        tomorrow = datetime.combine(today_date + timedelta(days=1), datetime.min.time())
        paid_to_date = db.query(func.coalesce(func.sum(models.InstallmentPayment.amount), 0)).filter(
            models.InstallmentPayment.installment_id == installment_id,
            models.InstallmentPayment.payment_date < tomorrow
        ).scalar() or 0

        # 4) Compute owed (if negative, clamp to zero)
        owed_today = total_required_to_date - paid_to_date
        if owed_today < 0:
            owed_today = 0

        return payment_schema.DueResponse(
            installment_id=installment_id,
            days_elapsed=days_elapsed,
            total_required_to_date=total_required_to_date,
            total_paid_to_date=paid_to_date,
            owed_today=owed_today
        )
    def pending_installments(self, db : Session):
        cnt = db.query(func.count()).select_from(models.Installment).filter(models.Installment.status == "Pending").scalar()
        return SimpleCount(count=cnt or 0)
    
    
    def overdue_payments(self, db):
        
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Step 1: For each installment, sum today’s payments
        pay_sum_subq = (
            db.query(
                models.InstallmentPayment.installment_id.label("inst_id"),
                func.coalesce(func.sum(models.InstallmentPayment.amount), 0).label("paid_today")
            )
            .filter(
                models.InstallmentPayment.payment_date >= datetime.combine(today, datetime.min.time()),
                models.InstallmentPayment.payment_date <  datetime.combine(tomorrow, datetime.min.time()),
            )
            .group_by(models.InstallmentPayment.installment_id)
            .subquery()
        )

        # Step 2: Left‐join installments to that subquery, defaulting paid_today=0
        # and count those where paid_today < DAILY_REQUIRED
        cnt = (
            db.query(func.count())
            .select_from(models.Installment)
            .outerjoin(
                pay_sum_subq,
                models.Installment.id == pay_sum_subq.c.inst_id
            )
            .filter(
                models.Installment.status == "Accepted",
                # If no row in subq, paid_today will be NULL → coalesce to 0
                func.coalesce(pay_sum_subq.c.paid_today, 0) < DAILY_REQUIRED
            )
            .scalar()
        )
        return SimpleCount(count=cnt or 0)
    
    
    def revenue_today(self, db):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        total = (
            db.query(func.coalesce(func.sum(models.InstallmentPayment.amount), 0))
            .filter(
                models.InstallmentPayment.payment_date >= datetime.combine(today, datetime.min.time()),
                models.InstallmentPayment.payment_date < datetime.combine(tomorrow, datetime.min.time()),
            )
            .scalar()
        )
        return {"total": total or 0}



installment = CRUDInstallment(models.Installment)