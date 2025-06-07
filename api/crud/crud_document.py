from sqlalchemy.orm import Session
from api import models
from api.schemas import document as document_schema
from .crud_base import CRUDBase

class CRUDDocument(CRUDBase[models.Document, document_schema.DocumentCreate, document_schema.DocumentUpdate]):
    def get_byagent(self, db: Session, *, agent_id: int):
        return db.query(self.model).get({'agent_id':agent_id})
document = CRUDDocument(models.Document)