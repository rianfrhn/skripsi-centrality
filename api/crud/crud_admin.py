from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
from schemas import(
    admin as admin_schema
)
from .crud_base import CRUDBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CRUDAdmin(CRUDBase[models.Admin, admin_schema.AdminCreate, admin_schema.AdminUpdate]):
    def create(self, db: Session, *, obj_in: admin_schema.AdminCreate) -> models.Admin:
        hashed_password = pwd_context.hash(obj_in.password)
        db_obj = models.Admin(
            username=obj_in.username,
            hashed_password=hashed_password,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, username: str, password: str) -> models.Admin | None:
        admin = db.query(models.Admin).filter(models.Admin.username == username).first()
        if admin and pwd_context.verify(password, admin.hashed_password):
            return admin
        return None


admin = CRUDAdmin(models.Admin)