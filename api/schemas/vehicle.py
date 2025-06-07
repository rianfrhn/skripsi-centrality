from pydantic import BaseModel
from typing import List, Optional

class VehicleBase(BaseModel):
    name: str
    quantity: int
    price: float
    display_image: Optional[str]
    description: Optional[str]
    dealer_id: int

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    name: Optional[str]
    quantity: Optional[int]
    price: Optional[float]
    display_image: Optional[str]
    description: Optional[str]
    dealer_id: Optional[int]

class VehicleRead(VehicleBase):
    id: int

    class Config:
        from_attributes = True

class VehiclePagination(BaseModel):
    total:Optional[int] = 0
    page_content: List[VehicleRead] = list()
    class Config:
        from_attributes = True