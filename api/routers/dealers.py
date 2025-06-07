from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
import crud
from schemas import(
    dealer as dealer_schema
)
from crud.crud_dealer import dealer as dealers
from core.dependencies import get_db

router = APIRouter(prefix="/dealers", tags=["dealers"])

@router.get("/", response_model=List[dealer_schema.DealerRead])
def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return dealers.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{dealer_id}", response_model=dealer_schema.DealerRead)
def get_dealer(dealer_id: int, db: Session = Depends(get_db)):
    dealer = dealers.get(db=db, id=dealer_id)
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealer
@router.post("/", response_model=dealer_schema.DealerRead)
def create_dealer(
    obj_in: dealer_schema.DealerCreate,
    db: Session = Depends(get_db)
):
    return dealers.create(db, obj_in=obj_in)
@router.patch("/{dealer_id}", response_model=dealer_schema.DealerRead)
def update_dealer(
    dealer_id: int,
    obj_in: dealer_schema.DealerUpdate,
    db: Session = Depends(get_db)
):
    dealer = dealers.get(db=db, id=dealer_id)
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealers.update(db=db, db_obj=dealer, obj_in=obj_in)

@router.delete("/{dealer_id}")
def delete_dealer(
    dealer_id: int,
    db: Session = Depends(get_db)
):
    dealers.remove(db=db, id=dealer_id)
    return {"ok": True}