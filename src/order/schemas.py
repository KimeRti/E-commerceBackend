from decimal import Decimal

from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from typing import List, Optional, Union
from datetime import datetime

from src.cart.schemas import CartItemView
from src.utils.schemas import UUIDView


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderCreate(BaseModel):
    address: UUID
    items: list[UUID]
    total_amount: Decimal
    status: OrderStatus.PENDING

    class Config:
        from_attributes = True


class OrderItemView(BaseModel):
    id: str
    product_id: str
    quantity: int
    price: float
    title: str


class OrderView(BaseModel, UUIDView):
    user_id: Optional[Union[UUID, str]] = None
    session_token: Optional[str] = None
    order_number: str
    address: str
    total_amount: float
    status: OrderStatus
    items: List[OrderItemView]

    class Config:
        from_attributes = True


class UpdateOrderStatus(BaseModel):
    status: OrderStatus

    class Config:
        from_attributes = True

