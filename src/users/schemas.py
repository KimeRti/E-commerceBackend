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
    password: SecretStr


class UserUpdate(BaseModel, UserPassHashMixin):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserView(BaseModel, UUIDView):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    is_active: bool
    role: UserRole

    class Config:
        from_attributes = True


class UserMeView(BaseModel, UUIDView):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool

    class Config:
        from_attributes = True


class UserMiniView(BaseModel, UUIDView):
    id: UUID
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserMeUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AddressCreate(BaseModel):
    name: str
    title: str
    country: str
    city: str
    district: str
    zip_code: str
    phone: str
    identity_number: str
    address: str

    @field_validator("identity_number")
    def identity_number_validator(cls, v):
        if len(str(v)) != 11:
            raise ValueError("T.C Kimlik Numarası 11 karakter olmalıdır !")
        return v

    @field_validator("phone")
    def phone_validator(cls, v):
        if len(str(v)) != 11:
            raise ValueError("Telefon Numarası 11 karakter olmalıdır !")
        return v

    @field_validator("zip_code")
    def post_code_validator(cls, v):
        if len(str(v)) != 5:
            raise ValueError("Posta Kodu 5 karakter olmalıdır !")
        return v

    @field_validator("country")
    def country_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Ülke Adı en az 2 karakter olmalıdır !")
        return v

    @field_validator("city")
    def city_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Şehir Adı en az 2 karakter olmalıdır !")
        return v

    @field_validator("district")
    def district_validator(cls, v):
        if len(v) < 2:
            raise ValueError("İlçe Adı en az 2 karakter olmalıdır !")
        return v

    @field_validator("address")
    def address_validator(cls, v):
        if len(v) < 10:
            raise ValueError("Adres en az 10 karakter olmalıdır !")
        return v

    @field_validator("title")
    def title_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Başlık en az 2 karakter olmalıdır !")
        return v

    @field_validator("name")
    def name_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Ad Soyad en az 2 karakter olmalıdır !")
        return v


class AddressUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    identity_number: Optional[str] = None
    address: Optional[str] = None

    @field_validator("identity_number")
    def identity_number_validator(cls, v):
        if len(str(v)) != 11:
            raise ValueError("T.C Kimlik Numarası 11 karakter olmalıdır !")
        return v

    @field_validator("phone")
    def phone_validator(cls, v):
        if len(str(v)) != 11:
            raise ValueError("Telefon Numarası 11 karakter olmalıdır !")
        return v

    @field_validator("zip_code")
    def post_code_validator(cls, v):
        if len(str(v)) != 5:
            raise ValueError("Posta Kodu 5 karakter olmalıdır !")
        return v

    @field_validator("country")
    def country_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Ülke Adı en az 2 karakter olmalıdır !")
        return v

    @field_validator("city")
    def city_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Şehir Adı en az 2 karakter olmalıdır !")
        return v

    @field_validator("district")
    def district_validator(cls, v):
        if len(v) < 2:
            raise ValueError("İlçe Adı en az 2 karakter olmalıdır !")
        return v

    @field_validator("address")
    def address_validator(cls, v):
        if len(v) < 10:
            raise ValueError("Adres en az 10 karakter olmalıdır !")
        return v

    @field_validator("title")
    def title_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Başlık en az 2 karakter olmalıdır !")
        return v

    @field_validator("name")
    def name_validator(cls, v):
        if len(v) < 2:
            raise ValueError("Ad Soyad en az 2 karakter olmalıdır !")


class AddressView(BaseModel, UUIDView):
    name: str
    title: str
    country: str
    city: str
    district: str
    zip_code: str
    phone: str
    identity_number: str
    address: str

    class Config:
        from_attributes = True


