from typing import List
from sqlalchemy.orm import Session
import models, schemas
from .crud_base import CRUDBase
from schemas import vehicle

class CRUDVehicle(CRUDBase[models.Vehicle, vehicle.VehicleCreate, vehicle.VehicleUpdate]):
    def decrement_stock(self, db: Session, *, vehicle_id: int, amount: int = 1):
        vehicle = db.query(models.Vehicle).get(vehicle_id)
        if vehicle.quantity < amount:
            raise ValueError("Insufficient stock")
        vehicle.quantity -= amount
        db.add(vehicle)
        db.commit()
        return vehicle
    
    def get_available(
        self,
        db:Session, *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.Vehicle]:
        q = (
            db.query(models.Vehicle)
            .outerjoin(
                models.Installment,
                models.Vehicle.id == models.Installment.vehicle_id
            )
            .filter(models.Installment.id == None) 
            .offset(skip)
            .limit(limit)
        )
        return q.all()
    def get_random_available(self, db:Session, *, amount: int = 3):
        q = (
            db.query(models.Vehicle)
            .outerjoin(
                models.Installment,
                models.Vehicle.id == models.Installment.vehicle_id
            )
            .filter(models.Installment.id == None)
            .order_by(models.func.random())   # random order (PostgreSQL / SQLite)
            .limit(amount)
        )
        return q.all()

vehicle = CRUDVehicle(models.Vehicle)