from sqlalchemy.orm import selectinload
from starlette import status

from src.cart.models import CartItem, Cart
from src.cart.schemas import CartItemCreate, CartView, CartItemView

from sqlalchemy.future import select
from uuid import UUID

from src.users.models import User
from src.utils.exceptions import BadRequestError
from src.utils.schemas import GeneralResponse
from src.utils.single_psql_db import get_db


class CartService:

    @staticmethod
    async def cart_add_item(item: CartItemCreate, actor: User = None, session_token: str = None):
        async with get_db() as db:
            user_id = actor.id if actor else None
            query = select(Cart).filter(Cart.user_id == user_id) if user_id else select(Cart).filter(
                Cart.session_token == session_token)
            result = await db.execute(query)
            cart = result.scalars().first()

            if not cart:
                cart = Cart(user_id=user_id, session_token=session_token)
                db.add(cart)
                await db.commit()
                await db.refresh(cart)

            cart_item = CartItem(**item.dict(), cart_id=cart.id)
            db.add(cart_item)
            await db.commit()

            return GeneralResponse(status_code=status.HTTP_201_CREATED, message="Ürün sepete eklendi.")

    @staticmethod
    async def cart_remove_item(item_id: UUID, actor: User = None, session_token: str = None):
        async with get_db() as db:
            user_id = actor.id if actor else None
            query = select(Cart).filter(Cart.user_id == user_id) if user_id else select(Cart).filter(
                Cart.session_token == session_token)
            result = await db.execute(query)
            cart = result.scalars().first()

            if not cart:
                raise BadRequestError("Sepet bulunamadı.")

            query = select(CartItem).filter(CartItem.id == item_id)
            result = await db.execute(query)
            cart_item = result.scalars().first()

            if not cart_item:
                raise BadRequestError("Ürün bulunamadı.")

            await db.delete(cart_item)
            await db.commit()

            return GeneralResponse(status_code=status.HTTP_200_OK, message="Ürün sepetten silindi.")

    @staticmethod
    async def cart_get(actor: User = None, session_token: str = None):
        async with get_db() as db:
            user_id = actor.id if actor else None
            query = select(Cart).filter(Cart.user_id == user_id) if user_id else select(Cart).filter(
                Cart.session_token == session_token)
            result = await db.execute(query)
            cart = result.scalars().first()

            if not cart:
                raise BadRequestError("Sepet bulunamadı.")

            stmt = select(CartItem).filter(CartItem.cart_id == cart.id)
            cart_items = await db.scalars(stmt)
            cart_items = cart_items.all()

            items_view = [
                CartItemView(
                    id=str(item.id),
                    product_id=str(item.product_id),
                    quantity=item.quantity
                ) for item in cart_items
            ]

            return GeneralResponse(status_code=status.HTTP_200_OK, message="Sepet öğeleri getirildi.", details=items_view)