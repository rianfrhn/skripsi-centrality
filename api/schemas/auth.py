from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCredentials(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    reference_key: Optional[str] = None
    referral_key: Optional[str] = None
    name : Optional[str] = None
    phone : Optional[str] = None
    address : Optional[str] = None
    gov_address : Optional[str] = None
    marriage_status : Optional[int] = None
    settlement_status : Optional[int] = None
    installment_status : Optional[int] = None

class AdminRegister(BaseModel):
    username: str
    password: str
    admin_key: str