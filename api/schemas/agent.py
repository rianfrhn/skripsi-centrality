from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime



class AgentBase(BaseModel):
    username: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gov_address: Optional[str] = None
    email: Optional[EmailStr] = None
    marriage_status: Optional[str] = None
    settlement_status: Optional[str] = None
    installment_status: Optional[bool] = None
    reference_key: Optional[str] = None
    verified : Optional[bool] = None
    class Config:
        from_attributes = True

class AgentCreate(AgentBase):
    password: str
    referral_key: Optional[str]

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[int] = None
    address: Optional[str] = None
    gov_address: Optional[str] = None
    email: Optional[EmailStr] = None
    marriage_status: Optional[str] = None
    settlement_status: Optional[str] = None
    installment_status: Optional[bool] = None
    reference_key: Optional[str] = None
    verified : Optional[bool] = None
    verified_at : Optional[datetime] = None

class AgentRead(AgentBase):
    id: int
    referred_by_id: Optional[int] = None
    referred_by: Optional[AgentBase] = None
    created_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgentPagination(BaseModel):
    total:int = 0
    page_content:List[AgentRead] = list()