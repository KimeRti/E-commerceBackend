from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, select
from uuid import UUID, uuid4

from src.product.schemas import ProductCreate, ProductUpdate
from src.utils.single_psql_db import Base, get_db
from src.utils.exceptions import NotFoundError


class Product(Base):
    __tablename__ = "products"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)

    @classmethod
    async def create(cls, product: ProductCreate):
        async with get_db() as db:
            new_product = Product(**product.model_dump(exclude_none=True))
            db.add(new_product)
            await db.commit()
            await db.refresh(new_product)
            return new_product

    @classmethod
    async def get(cls, product_id: UUID):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == product_id)
            product = await db.scalar(stmt)
            return product

    @classmethod
    async def update(cls, id: UUID, data: ProductUpdate):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == id)
            instance = await db.scalar(stmt)
            if instance is None:
                raise NotFoundError("Ürün bulunamadı.")
            for key, value in data.dict().items():
                setattr(instance, key, value)
            await db.commit()
            await db.refresh(instance)
            return instance

    @classmethod
    async def delete(cls, product_id: UUID):
        async with get_db() as db:
            stmt = select(cls).where(cls.id == product_id)
            product = await db.scalar(stmt)
            await db.delete(product)
            await db.commit()
            return product

    @classmethod
    async def get_by_category(cls, category_id: UUID):
        async with get_db() as db:
            stmt = select(cls).where(cls.category_id == category_id)
            products = await db.execute(stmt)
            return products

    @classmethod
    async def get_by_title(cls, title: str):
        async with get_db() as db:
            stmt = select(cls).where(cls.title == title)
            product = await db.scalar(stmt)
            return product





