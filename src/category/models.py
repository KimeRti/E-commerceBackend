from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import select
from uuid import UUID, uuid4

from src.category.schemas import CategoryCreate, CategoryUpdate

from src.product.models import Product

from src.utils.single_psql_db import Base, get_db
from src.utils.exceptions import BadRequestError


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    products: Mapped[Product] = relationship("Product", backref="category", lazy="joined")

    @classmethod
    async def create(cls, category: CategoryCreate):
        async with get_db() as db:
            instance = Category(**category.model_dump(exclude_none=True))
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance

    @classmethod
    async def update(cls, id: UUID, data: CategoryUpdate):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == id)
            instance = await db.scalar(stmt)
            if instance is None:
                raise BadRequestError("Kategori bulunamadı.")
            for key, value in data.dict().items():
                setattr(instance, key, value)
            await db.commit()
            await db.refresh(instance)
            return instance

    @classmethod
    async def delete(cls, id: UUID):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == id)
            instance = await db.scalar(stmt)
            if instance is None:
                raise BadRequestError("Kategori bulunamadı.")
            await db.delete(instance)
            await db.commit()


