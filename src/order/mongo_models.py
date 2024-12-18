from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field
from src.utils.schemas import StrObjectId


class OrderProductDetail(BaseModel):
    product_id: str
    title: str
    description: str
    price: float
    quantity: int
    total_price: float


class OrderAddressDetail(BaseModel):
    address_id: str
    name: str
    title: str
    country: str
    city: str
    district: str
    phone: str
    address: str
    zip_code: str


class OrderUserDetail(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    is_anonymous: bool = False


class MongoOrder(BaseModel):
    id: StrObjectId = Field(default_factory=StrObjectId, alias="_id")
    order_id: str
    order_number: str
    user: OrderUserDetail
    address: OrderAddressDetail
    items: List[OrderProductDetail]
    total_amount: float
    total_items: int
    status: str
    session_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    cancel_reason: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp() * 1000)
        } 