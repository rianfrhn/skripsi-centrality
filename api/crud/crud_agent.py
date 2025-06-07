from datetime import date, datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from schemas.misc import SimpleCount
import models
from schemas import(
    agent as agent_schema,
    misc as misc_schema
)
from .crud_base import CRUDBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CRUDAgent(CRUDBase[models.Agent, agent_schema.AgentCreate, agent_schema.AgentUpdate]):
    def create(self, db: Session, *, obj_in: agent_schema.AgentCreate) -> models.Agent:
        hashed_password = pwd_context.hash(obj_in.password)
        if obj_in.reference_key is not None:
            ref_key = obj_in.reference_key
        else:
            ref_key = self._generate_ref_key()
        db_obj = models.Agent(
            username=obj_in.username,
            email=obj_in.email,
            name=obj_in.name,
            phone=obj_in.phone,
            address=obj_in.address,
            gov_address=obj_in.gov_address,
            marriage_status=obj_in.marriage_status,
            settlement_status=obj_in.settlement_status,
            installment_status=obj_in.installment_status,
            reference_key= ref_key,
            hashed_password=hashed_password,
        )
        print(type(obj_in))
        if obj_in.referral_key:
            referred = db.query(models.Agent).filter_by(reference_key=obj_in.referral_key).first()
            if referred:
                db_obj.referred_by_id = referred.id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, username: str, password: str) -> models.Agent | None:
        agent = db.query(models.Agent).filter(models.Agent.username == username).first()
        if agent and pwd_context.verify(password, agent.hashed_password):
            return agent
        return None

    def _generate_ref_key(self) -> str:
        import uuid
        return uuid.uuid4().hex[:8]
    def get_pending_verifications(self, db: Session):
        cnt = db.query(func.count()).select_from(models.Agent).filter(models.Agent.verified == False).scalar()
        return SimpleCount(count= cnt or 0)
    
    
    def agent_approvals(self, db: Session, * , weeks: int):
        """
        For each of the last `weeks` weeks, return { week: 'Wk1', registered: int, approved: int }.
        """
        today = date.today()
        result = []
        for i in range(weeks):
            # week starting Monday
            week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=(weeks - 1 - i))
            week_end = week_start + timedelta(days=7)
            reg_count = (
                db.query(func.count())
                .select_from(models.Agent)
                .filter(
                    models.Agent.id != None,
                    models.Agent.created_at >= datetime.combine(week_start, datetime.min.time()),
                    models.Agent.created_at < datetime.combine(week_end, datetime.min.time()),
                )
                .scalar()
            )
            appr_count = (
                db.query(func.count())
                .select_from(models.Agent)
                .filter(
                    models.Agent.verified == True,
                    models.Agent.verified_at >= datetime.combine(week_start, datetime.min.time()),
                    models.Agent.verified_at < datetime.combine(week_end, datetime.min.time()),
                )
                .scalar()
            )
            result.append(
                misc_schema.ApprovalPoint(
                    week= f"Wk{ i + 1 }",
                    registered= reg_count or 0,
                    approved= appr_count or 0,

                )
            )
        return result

agent = CRUDAgent(models.Agent)