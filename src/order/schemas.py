from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.utils.schemas import UUIDView


class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"


class OrderItem(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0.0)

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    total_amount: float = Field(..., gt=0.0)
    order_items: List[OrderItem]
    status: Optional[OrderStatus] = OrderStatus.PENDING

    class Config:
        orm_mode = True


class OrderUpdate(BaseModel):
    total_amount: Optional[float] = Field(None, gt=0.0)
    status: Optional[OrderStatus]
    order_items: Optional[List[OrderItem]]

    class Config:
        orm_mode = True


class OrderView(UUIDView):
    user_id: UUID
    total_amount: float
    status: OrderStatus
    order_items: List[OrderItem]
    created_at: datetime

    class Config:
        orm_mode = True



