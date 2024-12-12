from typing import Optional

from sqlalchemy import select
from uuid import UUID

from src.auth.access.service import need_role
from src.users.schemas import UserCreate, UserUpdate, UserView, UserRole, AddressCreate, AddressView
from src.users.models import User, Address

from src.utils.single_psql_db import get_db
from src.utils.pagination import get_pagination_info
from src.utils.exceptions import NotFoundError, BadRequestError
from src.utils.schemas import GeneralResponse, PaginationGet, ListView


class UserService:

    @staticmethod
    async def create(user: UserCreate, actor: User):
        need_role(actor, [UserRole.ADMIN])
        async with get_db() as db:
            await User.create(user=user)
            return GeneralResponse(status=201, message="User created successfully.")

    @staticmethod
    async def get_users(pagination_data: PaginationGet):
        async with get_db() as db:
            where_query = None
            if pagination_data.search:
                where_query = (
                    User.email.like(f"%{pagination_data.search}%")
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

            user_views = [UserView.from_orm(user) for user in users]

            count = await User.get_count(where_query)
            pagination_info = get_pagination_info(
                total_items=count,
                current_page=pagination_data.page,
                page_size=pagination_data.pageSize
            )

            return GeneralResponse(
                status=200,
                message="Users listed.",
                details=ListView[UserView](info=pagination_info, items=user_views)
            )

    @staticmethod
    async def get_user(user_id: UUID):
        async with get_db() as db:
            user = await User.get(user_id)
            if not user:
                raise NotFoundError("User not found.")
            return GeneralResponse(status=200, message="User found.", details=UserView.model_validate(user))

    @staticmethod
    async def update(user_id: UUID, data: UserUpdate, actor: User):
        need_role(actor, [UserRole.ADMIN])
        async with get_db() as db:
            try:
                user = await User.get(user_id)
                if not user:
                    raise NotFoundError("User not found.")

                update_data = data.dict(exclude_unset=True)
                for key, value in update_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)

                db.add(user)
                await db.commit()
                return GeneralResponse(status=200, message="User updated successfully.")
            except Exception as e:
                return GeneralResponse(status=500, message=str(e))

    @staticmethod
    async def delete(user_id: UUID, actor: User):
        need_role(actor, [UserRole.ADMIN])
        async with get_db() as db:
            try:
                user = await User.get(user_id)
                if not user:
                    raise NotFoundError("User not found.")
                await user.delete(user_id=user_id)
                return GeneralResponse(status=200, message="User deleted successfully.")
            except Exception as e:
                return GeneralResponse(status=500, message=str(e))

    @staticmethod
    async def create_address(address: AddressCreate, actor: Optional[User] = None, session_token: Optional[str] = None):
        address_data = address.dict()

        if actor:
            address_data['user_id'] = actor.id
        elif session_token:
            address_data['session_token'] = session_token
        else:
            raise BadRequestError("Bir actor veya session_token sağlanmalı.")

        created_address = await Address.create(address_data)

        return GeneralResponse(
            status=201,
            message="Address created successfully.",
            details=AddressView.from_orm(created_address)
        )

    @staticmethod
    async def get_address(actor: Optional[User] = None, session_token: Optional[str] = None):
        async with get_db() as db:
            if actor:
                user_id = actor.id
                address = await db.execute(select(Address).filter(Address.user_id == user_id))
                address = address.scalars().first()
            elif session_token:
                address = await db.execute(select(Address).filter(Address.session_token == session_token))
                address = address.scalars().first()

                if not address:
                    raise BadRequestError("Geçersiz session token.")
            else:
                raise BadRequestError(
                    "Kullanıcı kimliği veya oturum belirteci sağlanmalıdır.")

        if not address:
            raise NotFoundError("Adres bulunamadı.")

        return GeneralResponse(
            status=200,
            message="Adres başarıyla getirildi.",
            details=AddressView.from_orm(address)
        )

    @staticmethod
    async def get_address_by_id(id: UUID):
        async with get_db() as db:
            instance = await db.execute(select(Address).filter(Address.id == id))
            instance = instance.scalar()
            if not instance:
                raise NotFoundError("Adres bulunamadı.")
            return GeneralResponse(
                status=200,
                message="Adres başarıyla getirildi.",
                details=AddressView.from_orm(instance)
            )






