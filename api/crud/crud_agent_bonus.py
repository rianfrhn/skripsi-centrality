from sqlalchemy.orm import Session
from api import models, schemas
from .crud_base import CRUDBase

bonus = CRUDBase[models.AgentBonus, schemas.PaymentCreate, schemas.PaymentBase](models.AgentBonus)