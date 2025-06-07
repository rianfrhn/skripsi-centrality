#FOR API
# main.py
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.database import engine, SessionLocal, Base
from api.models import initialize
from sqlalchemy.orm import Session

from api.management.users import create_user
from api.routers import (
    auth, agents, vehicles,
    installments, payments, 
    documents, dealers,
    centrality,
    utils
)
from api.routers.test import seeding

app = FastAPI()
#Base.metadata.create_all(bind=engine)
origins_env = os.getenv("CORS_ORIGINS", "")
origins = [url.strip() for url in origins_env.split(",") if url.strip()]
print("INITIALIZED WITH ORIGINS:"+origins)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
UPLOADS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../uploads"))

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOADS_DIR),
    name="uploads"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # or ["*"] to allow any
    allow_credentials=True,
    allow_methods=["*"],           # GET, POST, PATCH, etc.
    allow_headers=["*"],
)
initialize(Base, engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#app.mount("/static", StaticFiles(directory="static"), name="static")



app.include_router(auth.router)
app.include_router(agents.router)
#app.include_router(dealers.router)
app.include_router(vehicles.router)
app.include_router(installments.router)
app.include_router(payments.router)
app.include_router(payments.router2)
app.include_router(documents.router)
app.include_router(dealers.router)
app.include_router(seeding.router)
app.include_router(centrality.router)
app.include_router(utils.router)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}
