import os
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import models
from core.security import get_current_agent
import crud
from schemas import(
    document as document_schema
)
from crud.crud_document import document as documents
from core.dependencies import get_db, get_current_active_agent

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/me", response_model=document_schema.DocumentRead)
def get_my_documents(
    current: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    
    doc = documents.get_byagent(db, agent_id=current.id)
    if not doc:
        return document_schema.DocumentRead(agent_id=current.id)
    return doc


UPLOAD_DIR = "../uploads"
UPLOAD_DIR_DB = "/uploads"
def save_one(file: UploadFile) -> str:
    if not file:
        return ""
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    with open(path, "wb") as buffer:
        buffer.write(file.file.read())
    return f"{UPLOAD_DIR_DB}/{unique_name}"  
@router.post("/me", response_model=document_schema.DocumentRead)
async def upload_my_documents(
    national_id: UploadFile = File(None),
    self_portrait: UploadFile = File(None),
    partner_portrait: UploadFile = File(None),
    family_card: UploadFile = File(None),
    current: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    urls = {
        "national_id_url": save_one(national_id),
        "self_portrait_url": save_one(self_portrait),
        "partner_portrait_url": save_one(partner_portrait),
        "family_card_url": save_one(family_card),
    }

    existing = documents.get_byagent(db, agent_id=current.id)
    if existing:
        updated = documents.update(
            db,
            db_obj=existing,
            obj_in=document_schema.DocumentUpdate(**urls),
        )
        return updated

    created = documents.create(
        db,
        obj_in=document_schema.DocumentCreate(
            agent_id=current.id, **urls
        ),
    )
    return created

@router.get("/{agent_id}", response_model=document_schema.DocumentRead)
def get_documents(agent_id: int, db: Session = Depends(get_db)):
    doc = documents.get_byagent(db, agent_id=agent_id)
    if not doc:
        return document_schema.DocumentRead(agent_id=agent_id)
    return doc

@router.post("/{agent_id}", response_model=document_schema.DocumentRead)
def upload_documents(
    agent_id: int,
    national_id: UploadFile = File(None),
    self_portrait: UploadFile = File(None),
    partner_portrait: UploadFile = File(None),
    family_card: UploadFile = File(None),
    #current=Depends(get_current_active_agent),
    db: Session = Depends(get_db)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Stub: save files and get URLs
    urls = {
        "national_id_url": save_one(national_id),
        "self_portrait_url": save_one(self_portrait),
        "partner_portrait_url": save_one(partner_portrait),
        "family_card_url": save_one(family_card),
    }
    existing = documents.get_byagent(db, agent_id=agent_id)
    if existing:
        updated = documents.update(
            db,
            db_obj=existing,
            obj_in=document_schema.DocumentUpdate(**urls),
        )
        return updated

    created = documents.create(
        db,
        obj_in=document_schema.DocumentCreate(
            agent_id=agent_id, **urls
        ),
    )
    return created

