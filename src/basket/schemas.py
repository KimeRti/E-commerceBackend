import typing
from typing import List

from pydantic import BaseModel, field_validator
from uuid import UUID


class BasketItemValidator:
    id: typing.Union[UUID, str]
    product_id: typing.Union[UUID, str]

    @field_validator('id')
    def str_id(cls, v):
        return str(v)

    @field_validator('product_id')
    def str_id(cls, v):
        return str(v)


class BasketValidator:
    id: typing.Union[UUID, str]
    user_id: typing.Union[UUID, str]

    @field_validator('id')
    def str_id(cls, v):
        return str(v)

    @field_validator('user_id')
    def str_id(cls, v):
        return str(v)


class BasketItemCreate(BaseModel):
    product_id: UUID
    quantity: int

    class Config:
        from_attributes = True


class BasketItemView(BaseModel, BasketItemValidator):
    quantity: int
    price: float

    class Config:
        from_attributes = True


class BasketCreate(BaseModel):
    user_id: UUID
    basket_items: List[BasketItemCreate]

    class Config:
        from_attributes = True


class BasketView(BaseModel, BasketValidator):
    basket_items: List[BasketItemView]
    total_amount: float

    class Config:
        from_attributes = True


class BasketUpdate(BaseModel):
    product_id: UUID
    quantity: int

    class Config:
        from_attributes = True