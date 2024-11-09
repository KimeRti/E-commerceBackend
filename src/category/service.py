from src.category.models import Category
from src.category.schemas import CategoryCreate, CategoryView
from src.product.models import Product

from src.utils.single_psql_db import get_db
from src.utils.pagination import get_pagination_info
from src.utils.exceptions import NotFoundError, BadRequestError
from src.utils.schemas import GeneralResponse, PaginationGet, ListView


from sqlalchemy import select, func
from uuid import UUID


class CategoryService:
    @staticmethod
    async def create(category: CategoryCreate):
        await Category.create(category)
        return GeneralResponse(status=201, message="Kategori Başarıyla Oluşturuldu")

    @staticmethod
    async def get(pagination_data: PaginationGet):
        async with get_db() as db:
            where_query = None
            if pagination_data.search:
                where_query = (
                    (Category.name.like(f"%{pagination_data.search}%"))
                )
            if where_query is not None:
                query = select(Category).where(where_query)
            else:
                query = select(Category)
            if pagination_data.paginate:
                query = query.limit(pagination_data.pageSize).offset(
                    (pagination_data.page - 1) * pagination_data.pageSize
                )
            if pagination_data.order:
                query = query.order_by(Category.updated_at.desc())

            category = await db.scalars(query)
            category = category.all()

            count = await Category.get_count(where_query)
            pagination_info = get_pagination_info(total_items=count, current_page=pagination_data.page,
                                                  page_size=pagination_data.pageSize)

            return GeneralResponse(
                status=200,
                message="Ürünler Listelendi.",
                details=ListView[CategoryView](info=pagination_info, items=category)
            )

    @staticmethod
    async def get_category(category_id: UUID):
        async with get_db() as db:
            category = await Category.get(category_id)
            if not category:
                raise NotFoundError("Kategori Bulunamadı")
            return GeneralResponse(status=200, message="Kategori Bulundu", details=CategoryView.model_validate(category))

    @staticmethod
    async def update(category_id: UUID, data: CategoryCreate):
        async with get_db() as db:
            category = await Category.get(category_id)
            if not category:
                raise NotFoundError("Kategori Bulunamadı")
            await category.update(id=category_id, data=data)
            return GeneralResponse(status=200, message="Kategori Güncellendi")

    @staticmethod
    async def delete(category_id: UUID):
        async with get_db() as db:
            stmt = select(Category).where(Category.id == category_id)
            category = await db.scalar(stmt)

            if category is None:
                raise BadRequestError("Kategori bulunamadı.")

            product_count_stmt = select(func.count()).select_from(Product).where(Product.category_id == category_id)
            product_count = await db.scalar(product_count_stmt)

            if product_count > 0:
                raise BadRequestError(f"Bu kategori silinemez çünkü {product_count} ürün ile ilişkilidir.")

            await db.delete(category)
            await db.commit()

            return GeneralResponse(
                status=200,
                message="Kategori başarıyla silindi.",
                details=CategoryView.model_validate(category)
            )
