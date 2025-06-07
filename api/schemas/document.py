from pydantic import BaseModel
from typing import Optional

class DocumentBase(BaseModel):
    national_id_url: Optional[str] = None
    self_portrait_url: Optional[str] = None
    partner_portrait_url: Optional[str] = None
    family_card_url: Optional[str] = None
    agent_id: int

class DocumentCreate(DocumentBase):
    pass
class DocumentUpdate(DocumentBase):
    pass
class DocumentRead(DocumentBase):
    pass

    class Config:
        from_attributes = True