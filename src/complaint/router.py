from fastapi import APIRouter, Depends, BackgroundTasks, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from src.auth.current_user import get_current_user
from src.users.user.models import User
from src.utils.schemas import PaginationGet

from uuid import UUID
from typing import Optional
from beanie import PydanticObjectId

from src.complaint.schemas import ComplaintCreate, ComplaintView, ComplaintFeature, ComplaintStatus
from src.complaint.service import ComplaintService

complaints = APIRouter(
    prefix="/complaints",
    tags=["complaint"],
)


@complaints.get("")
async def get_complaints(
        pagination: PaginationGet = Depends(),
        author_id: Optional[UUID] = None,
        current_user: User = Depends(get_current_user),
):
    content = await ComplaintService.get_complaints(pagination, current_user, author_id)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@complaints.get("/{complaint_id}")
async def get_complaint(
        complaint_id: PydanticObjectId,
        current_user: User = Depends(get_current_user),
):
    content = await ComplaintService.get_complaint(complaint_id, current_user)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@complaints.post("")
async def create_complaint(
        data: ComplaintCreate,
        current_user: User = Depends(get_current_user),
):
    resp = await ComplaintService.create(data, current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@complaints.patch("/{complaint_id}/status")
async def update_complaint_status(
        complaint_id: PydanticObjectId,
        status: ComplaintStatus,
        current_user: User = Depends(get_current_user),
):
    resp = await ComplaintService.update_complaint_status(complaint_id, status, current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())
