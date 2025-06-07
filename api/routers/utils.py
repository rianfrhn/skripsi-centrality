
import os
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile


UPLOAD_DIR = "../uploads"


router = APIRouter(prefix="/utils", tags=["Utilities"])
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(500, detail="Failed to save file")

    url = f"{UPLOAD_DIR}/{unique_name}"
    return {"url": url}