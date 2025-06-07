
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from core.security import get_current_agent


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_active_agent(current_agent = Depends(get_current_agent)):
    if not current_agent.installment_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive agent")
    return current_agent
