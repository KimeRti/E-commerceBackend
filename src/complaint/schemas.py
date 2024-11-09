from pydantic import BaseModel, field_validator, model_validator
from typing import List, Union, Optional
from uuid import UUID
from enum import Enum
from datetime import datetime
from beanie import PydanticObjectId

from src.utils.schemas import UUIDView, Id, transform_list, PaginationInfo, AtView


class ComplaintFeature(str, Enum):
    NEW_QUESTION_ANSWER = "NEW_QUESTION"
    LIVE_STREAM = "LIVE_STREAM"
    LIVE_CHAT = "LIVE_CHAT"
    PROFILE = "PROFILE"
    PAYMENT = "PAYMENT"
    OTHER = "OTHER"


class ComplaintStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELED = "CANCELED"


class ComplaintCreate(BaseModel):
    reason: str
    details: dict
    feature: ComplaintFeature


class ComplaintView(BaseModel, AtView):
    id: PydanticObjectId
    reason: str
    details: dict
    feature: ComplaintFeature
    user_id: Union[UUID, str]

    class Config:
        from_attributes = True

    @field_validator("user_id")
    def validate_user_id(cls, value):
        return str(value) if isinstance(value, UUID) else value
