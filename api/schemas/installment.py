from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.agent import AgentRead
from schemas.vehicle import VehicleRead

class InstallmentBase(BaseModel):
    vehicle_id: int
    installment_duration: int

class InstallmentCreate(InstallmentBase):
    pass

class InstallmentUpdate(BaseModel):
    status: Optional[str] = None
    total_paid : Optional[int] = None

class InstallmentRead(InstallmentBase):
    id: int
    agent_id: int
    remaining_duration: int
    status: str
    applied_at: datetime
    accepted_at: Optional[datetime]
    vehicle: Optional[VehicleRead] = None
    agent: Optional[AgentRead] = None
    total_paid : Optional[int] = None

    class Config:
        from_attributes = True