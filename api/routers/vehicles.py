from math import floor
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from api.schemas import(
    vehicle as vehicle_schema
)
from api.crud.crud_vehicle import vehicle as vehicles
from api.core.dependencies import get_db, get_current_active_agent

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/", response_model=List[vehicle_schema.VehicleRead])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return vehicles.get_multi(db, skip=skip, limit=limit)
@router.get("/paged", response_model=vehicle_schema.VehiclePagination)
def list_vehicles_paged(
    page: int = 0,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    total = vehicles.get_multi(db, limit=9999).__len__()
    skip = (page-1) * page_size
    return vehicle_schema.VehiclePagination(total=total, page_content=vehicles.get_multi(db, skip=skip, limit=page_size))

@router.get("/available", response_model=List[vehicle_schema.VehicleRead])
def list_available_vehicle(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return vehicles.get_available(db, skip=skip, limit=limit)

@router.get("/random", response_model=List[vehicle_schema.VehicleRead])
def list_random_vehicle(amount: int, db: Session = Depends(get_db)):
    return vehicles.get_random_available(db, amount=amount)


@router.get("/{vehicle_id}", response_model=vehicle_schema.VehicleRead)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = vehicles.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.post("/", response_model=vehicle_schema.VehicleRead)
def create_vehicle(
    obj_in: vehicle_schema.VehicleCreate,
    #current=Depends(get_current_active_agent),
    db: Session = Depends(get_db)
):
    return vehicles.create(db, obj_in=obj_in)

@router.patch("/{vehicle_id}", response_model=vehicle_schema.VehicleRead)
def update_vehicle(
    vehicle_id: int,
    obj_in: vehicle_schema.VehicleUpdate,
    #current=Depends(get_current_active_agent),
    db: Session = Depends(get_db)
):
    vehicle = vehicles.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicles.update(db, db_obj=vehicle, obj_in=obj_in)

@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    #current=Depends(get_current_active_agent),
    db: Session = Depends(get_db)
):
    vehicles.remove(db, id=vehicle_id)
    return {"ok": True}