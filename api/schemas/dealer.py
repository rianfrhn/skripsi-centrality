from pydantic import BaseModel
from typing import Optional

class DealerBase(BaseModel):
    name: str
    phone_number: int
    address: str

class DealerCreate(DealerBase):
    pass

class DealerUpdate(BaseModel):
    name: Optional[str]
    phone_number: Optional[int]
    address: Optional[str]

class DealerRead(DealerBase):
    id: int

    class Config:
        from_attributes = True