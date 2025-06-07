from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class AdminBase(BaseModel):
    username: str

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    username: Optional[str] = None

class AdminRead(AdminBase):
    id: int

    class Config:
        from_attributes = True