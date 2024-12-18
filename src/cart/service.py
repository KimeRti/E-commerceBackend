from starlette import status

from src.cart.models import CartItem, Cart
from src.cart.schemas import CartItemCreate, CartView, CartItemView
from src.product.models import Product

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
            try:
                user_id = actor.id if actor else None

                product = await db.scalar(select(Product).where(Product.id == item.product_id))
                if not product:
                    raise BadRequestError("Ürün bulunamadı.")

                if user_id:
                    cart = await db.scalar(select(Cart).where(Cart.user_id == user_id))
                else:
                    cart = await db.scalar(select(Cart).where(Cart.session_token == session_token))

                if not cart:
                    cart = Cart(user_id=user_id, session_token=session_token)
                    db.add(cart)
                    await db.flush()

                existing_cart_item = await db.scalar(
                    select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id)
                )
                if existing_cart_item:
                    existing_cart_item.quantity += item.quantity
                    existing_cart_item.price = float(product.price) * existing_cart_item.quantity
                else:
                    db.add(
                        CartItem(
                            cart_id=cart.id,
                            product_id=product.id,
                            quantity=item.quantity,
                            price=float(product.price) * item.quantity,
                            title=product.title,
                        )
                    )

                cart_items = await db.scalars(select(CartItem).where(CartItem.cart_id == cart.id))
                cart.total_price = sum(item.price for item in cart_items)
                await db.commit()

                return GeneralResponse(
                    status_code=status.HTTP_201_CREATED, message="Ürün sepete eklendi."
                )
            except Exception as e:
                await db.rollback()
                raise BadRequestError(f"Ürün sepete eklenirken bir hata oluştu: {str(e)}")

    @staticmethod
    async def cart_remove_item(item_id: UUID, actor: User = None, session_token: str = None):
        async with get_db() as db:
            async with db.begin():
                try:
                    user_id = actor.id if actor else None

                    cart = await db.scalar(
                        select(Cart).where(
                            Cart.user_id == user_id if user_id else Cart.session_token == session_token
                        )
                    )

                    if not cart:
                        raise BadRequestError("Sepet bulunamadı.")

                    cart_item = await db.scalar(
                        select(CartItem).where(
                            CartItem.id == item_id,
                            CartItem.cart_id == cart.id
                        )
                    )

                    if not cart_item:
                        raise BadRequestError("Ürün bulunamadı.")

                    await db.delete(cart_item)
                    await db.flush()

                    cart.total_price = sum(
                        item.price for item in cart.items
                    )

                    await db.flush()

                    return GeneralResponse(
                        status_code=status.HTTP_200_OK,
                        message="Ürün sepetten silindi."
                    )

                except Exception as e:
                    await db.rollback()
                    raise BadRequestError(f"Sepetten ürün çıkarılırken bir hata oluştu: {str(e)}")

    @staticmethod
    async def cart_get(actor: User = None, session_token: str = None):
        async with get_db() as db:
            async with db.begin():
                try:
                    user_id = actor.id if actor else None

                    cart = await db.scalar(
                        select(Cart).where(
                            Cart.user_id == user_id if user_id else Cart.session_token == session_token
                        )
                    )

                    if not cart:
                        raise BadRequestError("Sepet bulunamadı.")

                    cart_items = await db.scalars(
                        select(CartItem).where(CartItem.cart_id == cart.id)
                    )

                    items_view = [
                        CartItemView(
                            id=str(item.id),
                            product_id=str(item.product_id),
                            quantity=item.quantity,
                            price=item.price,
                            title=item.title
                        ) for item in cart_items
                    ]

                    return GeneralResponse(status_code=status.HTTP_200_OK, message="Sepet Listelendi.", details=CartView(
                        id=str(cart.id),
                        user_id=str(cart.user_id) if cart.user_id else None,
                        session_token=cart.session_token,
                        items=items_view,
                        total_price=cart.total_price
                    ))

                except Exception as e:
                    raise BadRequestError(f"Sepet bilgisi getirilirken bir hata oluştu: {str(e)}")

    @staticmethod
    async def cart_clear(actor: User = None, session_token: str = None):
        async with get_db() as db:
            async with db.begin():
                try:
                    user_id = actor.id if actor else None

                    cart = await db.scalar(
                        select(Cart).where(
                            Cart.user_id == user_id if user_id else Cart.session_token == session_token
                        )
                    )

                    if not cart:
                        raise BadRequestError("Sepet bulunamadı.")

                    await db.delete(cart)
                    await db.flush()

                    return GeneralResponse(
                        status_code=status.HTTP_200_OK,
                        message="Sepet temizlendi."
                    )

                except Exception as e:
                    await db.rollback()
                    raise BadRequestError(f"Sepet temizlenirken bir hata oluştu: {str(e)}")

    @staticmethod
    async def cart_update_item_quantity(item_id: UUID, quantity: int, actor: User = None, session_token: str = None):
        async with get_db() as db:
            async with db.begin():
                try:
                    if quantity <= 0:
                        raise BadRequestError("Miktar sıfırdan büyük olmalıdır.")

                    user_id = actor.id if actor else None
                    filter_condition = (
                        (Cart.user_id == user_id) if user_id else (Cart.session_token == session_token)
                    )

                    cart = await db.scalar(select(Cart).where(filter_condition))
                    if not cart:
                        raise BadRequestError("Sepet bulunamadı.")

                    cart_item = await db.scalar(
                        select(CartItem).where(
                            CartItem.id == item_id,
                            CartItem.cart_id == cart.id
                        )
                    )
                    if not cart_item:
                        raise BadRequestError("Sepette bu ürüne ait öğe bulunamadı.")

                    product = await db.scalar(select(Product).where(Product.id == cart_item.product_id))
                    if not product:
                        raise BadRequestError("Ürün bilgisi alınamadı.")

                    cart_item.quantity = quantity
                    cart_item.price = float(product.price) * quantity

                    cart_items = await db.scalars(select(CartItem).where(CartItem.cart_id == cart.id))
                    cart.total_price = sum(item.price for item in cart_items)

                    await db.flush()

                    return GeneralResponse(
                        status_code=status.HTTP_200_OK,
                        message="Ürün miktarı güncellendi."
                    )

                except Exception as e:
                    await db.rollback()
                    raise BadRequestError(f"Ürün miktarı güncellenirken bir hata oluştu: {str(e)}")


