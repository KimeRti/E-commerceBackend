from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional, Union

from src.utils.schemas import UUIDView


class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0, description="Ürün miktarı en az 1 olmalıdır.")

    class Config:
        orm_mode = True
        from_attributes = True


class CartCreate(BaseModel):
    user_id: Optional[UUID] = None
    session_token: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class CartItemView(BaseModel, UUIDView):
    product_id: Union[UUID, str]
    quantity: int
    price: float
    title: str

    class Config:
        orm_mode = True
        from_attributes = True


class CartView(BaseModel, UUIDView):
    user_id: Optional[Union[UUID, str]] = None
    session_token: Optional[str] = None
    items: List[CartItemView] = []
    total_price: float

    class Config:
        orm_mode = True
        from_attributes = True
