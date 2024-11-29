from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, select
from uuid import UUID, uuid4
from src.utils.single_psql_db import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="PENDING")

    # Define only the necessary attributes without direct circular dependency
    order_items = relationship("BasketItem", back_populates="order")

    @classmethod
    async def create(cls, db, user_id: UUID, total_amount: float, status: str = "PENDING"):
        new_order = cls(user_id=user_id, total_amount=total_amount, status=status)
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        return new_order

    @classmethod
    async def get(cls, db, order_id: UUID):
        return await db.scalar(select(cls).where(cls.id == order_id))

    @classmethod
    async def update(cls, db, order_id: UUID, **kwargs):
        order = await cls.get(db, order_id)
        if not order:
            return None
        for key, value in kwargs.items():
            setattr(order, key, value)
        await db.commit()
        await db.refresh(order)
        return order

    @classmethod
    async def delete(cls, db, order_id: UUID):
        order = await cls.get(db, order_id)
        if order:
            await db.delete(order)
            await db.commit()
        return order
