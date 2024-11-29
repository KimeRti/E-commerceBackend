import shutil
from pathlib import Path
from sqlalchemy import select
from uuid import UUID
from fastapi import UploadFile

from src.users.schemas import UserCreate, UserUpdate, UserView, UserMiniView
from src.users.models import User

from src.utils.single_psql_db import get_db
from src.utils.pagination import get_pagination_info
from src.utils.exceptions import NotFoundError
from src.utils.schemas import GeneralResponse, PaginationGet, ListView


UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class UserService:

    @staticmethod
    async def create(user: UserCreate):
        await User.create(user)
        return GeneralResponse(status=201, message="User created successfully.")

    @staticmethod
    async def get_users(pagination_data: PaginationGet):
        async with get_db() as db:
            where_query = None
            if pagination_data.search:
                where_query = (
                        (User.email.like(f"%{pagination_data.search}%"))
                )
            if where_query is not None:
                query = select(User).where(where_query)
            else:
                query = select(User)
            if pagination_data.paginate:
                query = query.limit(pagination_data.pageSize).offset(
                    (pagination_data.page - 1) * pagination_data.pageSize
                )
            if pagination_data.order:
                query = query.order_by(User.updated_at.desc())

            users = await db.scalars(query)
            users = users.all()

            count = await User.get_count(where_query)
            pagination_info = get_pagination_info(total_items=count, current_page=pagination_data.page,
                                                  page_size=pagination_data.pageSize)

            return GeneralResponse(status=200, message="Users listed.",
                                   details=ListView[UserMiniView](info=pagination_info, items=users))

    @staticmethod
    async def get_user(user_id: UUID):
        async with get_db() as db:
            user = await User.get(user_id)
            if not user:
                raise NotFoundError("User not found.")
            return GeneralResponse(status=200, message="User found.", details=UserView.model_validate(user))

    @staticmethod
    async def update(user_id: UUID, data: UserUpdate):
        async with get_db() as db:
            user = await User.get(user_id)
            if not user:
                raise NotFoundError("User not found.")
            await user.update(data)
            return GeneralResponse(status=200, message="User updated successfully.")

    @staticmethod
    async def delete(user_id: UUID):
        async with get_db() as db:
            user = await User.get(user_id)
            if not user:
                raise NotFoundError("User not found.")
            await user.delete()
            return GeneralResponse(status=200, message="User deleted successfully.")

    @staticmethod
    async def upload_avatar(user_id: UUID, file: UploadFile):
        file_path = UPLOAD_DIR / f"{user_id}_{file.filename}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        await User.add_avatar(user_id=user_id, avatar=str(file_path))
        return GeneralResponse(message="Fotoğraf Yüklendi", status=200, details=str({"file_path": str(file_path)}))


