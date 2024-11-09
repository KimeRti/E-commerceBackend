from src.utils.pagination import get_pagination_info
from src.utils.exceptions import *
from src.utils.schemas import GeneralResponse, PaginationGet, ListView
from src.auth.access.service import need_role
from src.users.models import User
from src.users.schemas import UserRole
from typing import Optional
from uuid import UUID

from bson import ObjectId

from src.complaint.models import Complaint
from src.complaint.schemas import ComplaintCreate, ComplaintView, ComplaintStatus


class ComplaintService:

    @staticmethod
    async def create(data: ComplaintCreate, actor: User):
        new_complaint = Complaint(**data.model_dump(), user_id=actor.id, status=ComplaintStatus.NEW)
        await new_complaint.insert()
        return GeneralResponse(message="Şikayetiniz oluşturuldu.", status=201)

    @staticmethod
    async def get_complaints(pagination: PaginationGet, actor: User, author_id: Optional[UUID] = None):
        if author_id != actor.id:
            need_role(actor, [UserRole.ADMIN])
        stmt = Complaint.find()
        if author_id is not None:
            stmt = stmt.find(user_id=author_id)
        if pagination.order:
            stmt = stmt.sort("-created_at")
        if pagination.search:
            stmt = stmt.find({"$text": {"$search": pagination.search}})
        count = await stmt.count()
        if pagination.paginate:
            stmt = stmt.skip((pagination.page - 1) * pagination.pageSize).limit(pagination.pageSize)

        complaints = await stmt.to_list()
        pagination_info = get_pagination_info(total_items=count, current_page=pagination.page,
                                              page_size=pagination.pageSize)
        return GeneralResponse(status=200, message="Şikayetler getirildi",
                               details=ListView[ComplaintView](items=complaints,
                                                               info=pagination_info)
                               )

    @staticmethod
    async def get_complaint(complaint_id: ObjectId, actor: User):
        complaint = await Complaint.get(complaint_id)
        if complaint is None:
            raise NotFoundError("Şikayet bulunamadı.")
        if complaint.user_id != actor.id:
            need_role(actor, [UserRole.ADMIN], "Bu şikayeti görüntülemek için yetkiniz yok.")
        return GeneralResponse(status=200, message="Şikayet getirildi", details=ComplaintView.model_validate(complaint))

    @staticmethod
    async def update_complaint_status(complaint_id: ObjectId, status: ComplaintStatus, actor: User):
        need_role(actor, [UserRole.ADMIN])
        complaint = await Complaint.get(complaint_id)
        if complaint is None:
            raise NotFoundError("Şikayet bulunamadı.")
        complaint.status = status
        await complaint.replace()
        return GeneralResponse(status=200, message="Şikayet güncellendi.")

    @staticmethod
    async def delete_complaint(complaint_id: ObjectId, actor: User):
        # no need for now
        pass
