from beanie import Document, before_event, Replace, Insert
from uuid import UUID
from datetime import datetime, UTC
from pydantic import Field

from src.complaint.schemas import ComplaintFeature, ComplaintStatus


def datetime_utc_now():
    return datetime.now(UTC)


class Complaint(Document):
    reason: str
    details: dict
    feature: ComplaintFeature
    status: ComplaintStatus
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime_utc_now)
    updated_at: datetime = Field(default_factory=datetime_utc_now)

    @before_event([Replace, Insert])
    def update_update_at(self):
        self.updated_at = datetime.now(UTC)
