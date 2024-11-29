from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy import ForeignKey, Enum as SqlEnum, Column, select
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy import Enum as SQLEnum

from src.users.schemas import UserUpdate, UserCreate, UserRole
from src.utils.single_psql_db import Base, get_db
from src.utils.exceptions import BadRequestError
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(nullable=True, unique=True, index=True)
    country: Mapped[str] = mapped_column(nullable=False)
    identity_number: Mapped[str] = mapped_column(nullable=True, unique=True, index=True)
    role: Mapped[str] = mapped_column(nullable=False, default=UserRole.CUSTOMER)
    avatar: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(nullable=False, default=False)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    async def by_email(cls, email: str):
        async with get_db() as db:
            from sqlalchemy import select
            stmt = select(cls).where(cls.email == email)
            user = await db.scalar(stmt)
            return user

    @classmethod
    async def get(cls, user_id: UUID):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == user_id)
            user = await db.scalar(stmt)
            return user

    @classmethod
    async def create(cls, user: UserCreate):
        async with get_db() as db:
            existing_user = await db.execute(
                select(User).where(User.email == user.email)
            )
            existing_user = existing_user.scalars().first()

            if existing_user:
                raise BadRequestError("Bu e-posta adresi zaten kullanımda.")

            new_user = User(**user.model_dump(exclude_none=True))
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user

    @classmethod
    async def update(cls, user_id: UUID, user: UserUpdate):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == user_id)
            user_instance = await db.scalar(stmt)
            if user_instance is None:
                raise BadRequestError("Kullanıcı bulunamadı.")
            for key, value in user.dict().items():
                setattr(user_instance, key, value)
            await db.commit()
            await db.refresh(user_instance)
            return user_instance

    @classmethod
    async def delete(cls, user_id: UUID):
        async with get_db() as db:
            user_instance = await db.scalar(select(cls).where(cls.id == user_id))
            if user_instance is None:
                raise BadRequestError("Kullanıcı bulunamadı.")
            try:
                await db.delete(user_instance)
                await db.commit()
                return user_instance
            except (UniqueViolationError, IntegrityError):
                raise BadRequestError("Kullanıcı silinemedi. İletişime geçiniz.")

    @classmethod
    async def add_avatar(cls, user_id: UUID, avatar: str):
        async with get_db() as db:
            user_instance = await db.scalar(select(cls).where(cls.id == user_id))
            if user_instance is None:
                raise BadRequestError("Kullanıcı bulunamadı.")
            user_instance.avatar = avatar
            await db.commit()
            await db.refresh(user_instance)
            return user_instance




