from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from typing import List, Optional, Union
from datetime import datetime

from src.utils.schemas import UUIDView


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderCreate(BaseModel):
    user_id: Union[UUID, str]
    order_number: str
    address: str
    total_amount: float
    status: OrderStatus

    class Config:
        from_attributes = True


class OrderView(BaseModel, UUIDView):
    user_id: Union[UUID, str]
    order_number: str
    address: str
    total_amount: float
    status: OrderStatus
    items: List[Union[UUID, str]]

    class Config:
        from_attributes = True

