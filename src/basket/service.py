from uuid import UUID

from sqlalchemy import select

from src.basket.models import Basket, BasketItem
from src.basket.schemas import BasketView, BasketItemView, BasketItemCreate
from src.product.models import Product
from src.utils.exceptions import NotFoundError
from src.utils.schemas import GeneralResponse
from src.utils.single_psql_db import get_db


class BasketService:

    @staticmethod
    async def add_to_basket(user_id: UUID, product_id: UUID, quantity: int):
        async with get_db() as db:
            product = await db.scalar(select(Product).where(Product.id == product_id))
            if not product:
                raise NotFoundError("Ürün bulunamadı.")

            basket = await db.scalar(select(Basket).where(Basket.user_id == user_id))
            if not basket:
                basket = Basket(user_id=user_id, total_amount=0.0)
                db.add(basket)
                await db.commit()
                await db.refresh(basket)

            basket_item = await db.scalar(
                select(BasketItem).where(BasketItem.basket_id == basket.id, BasketItem.product_id == product_id))
            if basket_item:
                basket_item.quantity += quantity
                basket_item.price = product.price * basket_item.quantity
            else:
                basket_item = BasketItem(basket_id=basket.id, product_id=product_id, quantity=quantity,
                                         price=product.price * quantity)
                db.add(basket_item)

            basket_items = await db.execute(select(BasketItem).where(BasketItem.basket_id == basket.id))
            items = basket_items.scalars().all()
            basket.total_amount = sum(item.price for item in items)

            await db.commit()
            await db.refresh(basket)

            return GeneralResponse(
                message="Ürün sepete eklendi",
                status=201,
                details={
                    "id": str(basket.id),
                    "total_amount": basket.total_amount
                }
            )

    @staticmethod
    async def view_basket(user_id: UUID):
        async with get_db() as db:
            basket = await db.scalar(select(Basket).where(Basket.user_id == user_id))
            if not basket:
                raise NotFoundError("Sepet bulunamadı.")

            basket_items = await db.execute(select(BasketItem).where(BasketItem.basket_id == basket.id))
            items = basket_items.scalars().all()

            return GeneralResponse(
                message="Sepet görüntülendi",
                status=200,
                details={
                    "id": str(basket.id),
                    "user_id": str(basket.user_id),
                    "basket_items": [
                        {
                            "id": str(item.id),
                            "product_id": str(item.product_id),
                            "quantity": item.quantity,
                            "price": item.price
                        }
                        for item in items
                    ],
                    "total_amount": basket.total_amount
                }
            )

    @staticmethod
    async def remove_from_basket(user_id: UUID, product_id: UUID, quantity: int = 1):
        async with get_db() as db:
            basket = await db.scalar(select(Basket).where(Basket.user_id == user_id))
            if not basket:
                raise NotFoundError("Sepet bulunamadı.")

            basket_item = await db.scalar(
                select(BasketItem).where(BasketItem.basket_id == basket.id, BasketItem.product_id == product_id))
            if not basket_item:
                raise NotFoundError("Ürün sepette bulunamadı.")

            if basket_item.quantity > quantity:
                basket_item.quantity -= quantity
                basket_item.price = (basket_item.price / (
                            basket_item.quantity + quantity)) * basket_item.quantity
            else:
                await db.delete(basket_item)

            basket_items = await db.execute(select(BasketItem).where(BasketItem.basket_id == basket.id))
            items = basket_items.scalars().all()
            total_amount = sum(item.price for item in items)

            basket.total_amount = total_amount
            await db.commit()
            await db.refresh(basket)

            return GeneralResponse(
                message="Ürün sepetten çıkarıldı",
                status=200,
                details={
                    "id": str(basket.id),
                    "total_amount": basket.total_amount
                }
            )