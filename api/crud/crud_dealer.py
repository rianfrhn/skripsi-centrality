from sqlalchemy.orm import Session
import models, schemas
from schemas.dealer import DealerCreate, DealerUpdate
from .crud_base import CRUDBase

dealer = CRUDBase[models.Dealer, DealerCreate, DealerUpdate](models.Dealer)