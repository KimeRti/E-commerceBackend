import shutil
from pathlib import Path

from fastapi import UploadFile

from src.auth.access.service import need_role
from src.product.models import Product, ProductPhotos
from src.product.schemas import ProductCreate, ProductView, ProductUpdate
from src.users.models import User
from src.users.schemas import UserRole

from src.utils.single_psql_db import get_db
from src.utils.pagination import get_pagination_info
from src.utils.exceptions import NotFoundError
from src.utils.schemas import GeneralResponse, PaginationGet, ListView

from sqlalchemy import select
from uuid import UUID


UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ProductService:

    @staticmethod
    async def get_products(pagination_data: PaginationGet):
        async with get_db() as db:
            where_query = None
            if pagination_data.search:
                where_query = (
                        (Product.title.like(f"%{pagination_data.search}%"))
                )
            if where_query is not None:
                query = select(Product).where(where_query)
            else:
                query = select(Product)
            if pagination_data.paginate:
                query = query.limit(pagination_data.pageSize).offset(
                    (pagination_data.page - 1) * pagination_data.pageSize
                )
            if pagination_data.order:
                query = query.order_by(Product.updated_at.desc())

            products = await db.execute(query)
            products = products.scalars().all()

            product_views = []
            for product in products:
                product_dict = {
                    "id": str(product.id),
                    "title": product.title,
                    "description": product.description,
                    "category_id": str(product.category_id),
                    "price": product.price,
                    "stock": product.stock,
                    "is_active": product.is_active,
                    "created_at": int(product.created_at.timestamp() * 1000),
                    "updated_at": int(product.updated_at.timestamp() * 1000)
                }
                product_views.append(product_dict)

            count = await Product.get_count(where_query)
            pagination_info = get_pagination_info(
                total_items=count,
                current_page=pagination_data.page,
                page_size=pagination_data.pageSize
            )

            return GeneralResponse(status=200,message="Ürünler Listelendi",details=ListView[ProductView](items=product_views, info=pagination_info))

    @staticmethod
    async def get_product(product_id: UUID):
        product = await Product.get(product_id)
        if not product:
            raise NotFoundError("Ürün Bulunamadı")
        return GeneralResponse(status=200, message="Ürün Bulundu", details=ProductView.model_validate(product))

    @staticmethod
    async def product_create(product: ProductCreate, actor: User):
        need_role(actor, [UserRole.ADMIN])
        await Product.create(product)
        return GeneralResponse(status=201, message="Ürün Başarıyla Oluşturuldu")

    @staticmethod
    async def product_update(product_id: UUID, data: ProductUpdate, actor: User):
        need_role(actor, [UserRole.ADMIN])
        product = await Product.get(product_id)
        if not product:
            raise NotFoundError("Ürün Bulunamadı")
        await Product.update(id=product_id, data=data)
        return GeneralResponse(status=200, message="Ürün Güncellendi")

    @staticmethod
    async def product_delete(product_id: UUID, actor: User):
        need_role(actor, [UserRole.ADMIN])
        await Product.delete(product_id)
        return GeneralResponse(status=200, message="Ürün Silindi")

    @staticmethod
    async def upload_photo(product_id: UUID, file: UploadFile, actor: User):
        need_role(actor, [UserRole.ADMIN])
        file_path = UPLOAD_DIR / f"{product_id}_{file.filename}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        await ProductPhotos.create(product_id=product_id, url=str(file_path))
        return GeneralResponse(message="Fotoğraf Yüklendi", status=200, details=str({"file_path": str(file_path)}))


