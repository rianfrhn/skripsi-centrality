from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from api.crud import(
    crud_agent,
    crud_admin
)
from api.models import SpecialKeys
from api.schemas import (
    agent as agent_schema,
    admin as admin_schema,
    auth as auth_schema
)
from api.core.security import create_access_token
from api.core.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=agent_schema.AgentRead)
def register(
    credentials: auth_schema.UserRegister,
    db: Session = Depends(get_db)
):
    existing = db.query(crud_agent.agent.model).filter(
        (crud_agent.agent.model.username == credentials.username) |
        (crud_agent.agent.model.email == credentials.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    agent = crud_agent.agent.create(db, obj_in=credentials)
    return agent

@router.post("/login", response_model=auth_schema.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    agent = crud_agent.agent.authenticate(db, username=form_data.username, password=form_data.password)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": agent.username})
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/register_admin", response_model=admin_schema.AdminRead)
def register_admin(
    credentials: auth_schema.AdminRegister,
    db: Session = Depends(get_db)
):
    admin_key = db.query(SpecialKeys).filter_by(key="admin_key", value=credentials.admin_key)
    if not admin_key:
        raise HTTPException(status_code=400, detail="Admin key invalid")

    existing = db.query(crud_admin.admin.model).filter(
        (crud_admin.admin.model.username == credentials.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    admin = crud_admin.admin.create(db, obj_in=credentials)
    return admin

@router.post("/login_admin", response_model=auth_schema.Token)
def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = crud_admin.admin.authenticate(db, username=form_data.username, password=form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}