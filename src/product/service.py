from src.product.models import Product
from src.product.schemas import ProductCreate, ProductView, ProductUpdate

from src.utils.single_psql_db import get_db
from src.utils.pagination import get_pagination_info
from src.utils.exceptions import NotFoundError
from src.utils.schemas import GeneralResponse, PaginationGet, ListView

from sqlalchemy import select
from uuid import UUID


class ProductService:

    @staticmethod
    async def product_create(product: ProductCreate):
        await Product.create(product)
        return GeneralResponse(status=201, message="Ürün Başarıyla Oluşturuldu")

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

            products = await db.scalars(query)
            products = products.all()

            count = await Product.get_count(where_query)
            pagination_info = get_pagination_info(total_items=count, current_page=pagination_data.page,
                                                  page_size=pagination_data.pageSize)

            return GeneralResponse(
                status=200,
                message="Ürünler Listelendi.",
                details=ListView[ProductView](info=pagination_info, items=products)
            )

    @staticmethod
    async def get_product(product_id: UUID):
        async with get_db() as db:
            product = await Product.get(product_id)
            if not product:
                raise NotFoundError("Ürün Bulunamadı")
            return GeneralResponse(status=200, message="Ürün Bulundu", details=ProductView.model_validate(product))

    @staticmethod
    async def product_update(product_id: UUID, data: ProductUpdate):
        async with get_db() as db:
            product = await Product.get(product_id)
            if not product:
                raise NotFoundError("Ürün Bulunamadı")
            await Product.update(id=product_id, product=data)
            return GeneralResponse(status=200, message="Ürün Güncellendi")

    @staticmethod
    async def product_delete(product_id: UUID):
        await Product.delete(product_id)
        return GeneralResponse(status=200, message="Ürün Silindi")

