from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, select
from uuid import UUID, uuid4

from src.cart.models import Cart
from src.order.models import Order
from src.utils.single_psql_db import Base, get_db
from src.utils.exceptions import BadRequestError
from src.users.schemas import UserCreate, UserUpdate, AddressCreate, UserRole
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(nullable=False, default=UserRole.CUSTOMER)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    cart: Mapped[list["Cart"]] = relationship("Cart", back_populates="user")
    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="user")

    @classmethod
    async def by_email(cls, email: str):
        async with get_db() as db:
            stmt = select(cls).where(cls.email == email)
            return await db.scalar(stmt)

    @classmethod
    async def get(cls, user_id: UUID):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == user_id)
            return await db.scalar(stmt)

    @classmethod
    async def create(cls, user: UserCreate):
        async with get_db() as db:
            existing_user = await db.scalar(
                select(cls).where(cls.email == user.email)
            )
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

            update_data = user.model_dump(exclude_unset=True)
            for key, value in update_data.items():
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


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    session_token: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    district: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    identity_number: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    zip_code: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="addresses")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="address")

    @classmethod
    async def create(cls, address_data: dict):
        async with get_db() as db:
            instance = cls(**address_data)
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance