from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Column
from uuid import UUID, uuid4
from src.utils.single_psql_db import Base

class Basket(Base):
    __tablename__ = "baskets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(nullable=False)

    basket_items: Mapped[list["BasketItem"]] = relationship("BasketItem", back_populates="basket")

class BasketItem(Base):
    __tablename__ = "basket_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    basket_id: Mapped[UUID] = mapped_column(ForeignKey("baskets.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)

    # Lazy import of Order to avoid circular reference
    basket: Mapped["Basket"] = relationship("Basket", back_populates="basket_items")

    order_id = Column(ForeignKey("orders.id"), nullable=True)
    order = relationship("Order", back_populates="order_items")
