from typing import Generic, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.database import Base

Model = TypeVar("Model", bound=Base) # type: ignore
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)

class CRUDBase(Generic[Model, CreateSchema, UpdateSchema]):
    def __init__(self, model: Type[Model]):
        self.model = model

    def get(self, db: Session, id: int) -> Model | None:
        return db.query(self.model).get(id)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchema) -> Model:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Model, obj_in: UpdateSchema) -> Model:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Model:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj