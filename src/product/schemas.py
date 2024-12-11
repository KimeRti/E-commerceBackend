from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr, field_validator
from typing import Optional, Union
import bcrypt

from src.utils.schemas import UUIDView


class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    stock: int
    category_id: UUID

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

    @field_validator("price")
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Fiyat 0'ın altında olamaz.")
        return value

    @field_validator("stock")
    def validate_stock(cls, value):
        if value <= 0:
            raise ValueError("Stok 0'ın altında olamaz.")
        return value

    @field_validator("category_id")
    def validate_category_id(cls, value):
        if not value:
            raise ValueError("Kategori ID boş olamaz.")
        return value


class ProductMiniView(BaseModel, UUIDView):
    title: str
    category_id: UUID
    price: float

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        from_attributes = True


class ProductView(BaseModel, UUIDView):
    title: str
    price: float
    category_id: Union[UUID, str]
    stock: int
    is_active: bool

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        from_attributes = True


class ProductUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    category_id: Optional[UUID]
    price: Optional[float]
    stock: Optional[int]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        from_attributes = True


class PhotoResponse(BaseModel):
    id: Union[UUID, str]
    url: str

    class Config:
        from_attributes = True



