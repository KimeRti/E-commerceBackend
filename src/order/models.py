from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum

from uuid import UUID, uuid4

from src.cart.models import CartItem
from src.order.schemas import OrderStatus
from src.utils.single_psql_db import Base


class Order(Base):
    __tablename__ = "order"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    order_number: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[UUID] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)

    items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="order")

    user: Mapped["User"] = relationship("User", back_populates="orders")

