from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr, field_validator
from typing import Optional, Union
import bcrypt

from src.utils.schemas import UUIDView


class UserPassHashMixin:
    @field_validator("password")
    def password_validator(cls, v):
        if v:
            return bcrypt.hashpw(v.get_secret_value().encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return v


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class UserCreate(BaseModel, UserPassHashMixin):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    country: str
    identity_number: str
    password: SecretStr


class UserUpdate(BaseModel, UserPassHashMixin):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None


class UserView(BaseModel, UUIDView):
    email: EmailStr
    username: str
    is_active: bool
    phone: str
    avatar: Optional[str] = None

    class Config:
        orm_mode = True


class UserMeView(BaseModel, UUIDView):
    email: EmailStr
    username: str
    phone: str
    is_active: bool
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserMiniView(BaseModel, UUIDView):
    id: UUID
    username: str
    email: EmailStr
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserMeUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None


class PhotoResponse(BaseModel):
    url: str

    class Config:
        from_attributes = True
