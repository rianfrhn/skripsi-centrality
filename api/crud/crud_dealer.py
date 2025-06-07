from sqlalchemy.orm import Session
from api import models, schemas
from api.schemas.dealer import DealerCreate, DealerUpdate
from .crud_base import CRUDBase

dealer = CRUDBase[models.Dealer, DealerCreate, DealerUpdate](models.Dealer)