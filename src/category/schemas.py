from uuid import UUID

from pydantic import BaseModel
from typing import Optional

from src.utils.schemas import UUIDView


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str]
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        from_attributes = True


class CategoryView(BaseModel, UUIDView):
    id: UUID
    name: str
    description: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        from_attributes = True


class CategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        from_attributes = True