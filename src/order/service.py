from datetime import datetime
import random
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.auth.access.service import need_role
from src.cart.models import Cart, CartItem
from src.order.models import Order, OrderItem
from src.order.schemas import OrderView, OrderStatus
from src.product.models import Product
from src.users.models import User, Address
from src.users.schemas import UserRole
from src.utils.exceptions import BadRequestError
from src.utils.schemas import GeneralResponse
from src.utils.single_mongo_db import init_mongo_db
from src.order.mongo_models import MongoOrder, OrderProductDetail, OrderAddressDetail, OrderUserDetail
from src.utils.single_psql_db import get_db


class OrderService:

    @staticmethod
    async def create_order(actor: Optional[User] = None, session_token: Optional[str] = None):
        async with get_db() as session:
            async with session.begin():
                try:
                    # Sepeti bul
                    stmt = select(Cart).where(
                        Cart.user_id == actor.id if actor else Cart.session_token == session_token
                    )
                    cart = await session.scalar(stmt)
                    
                    if not cart:
                        raise BadRequestError("Sepet bulunamadı.")

                    # Sepet öğelerini bul
                    stmt = (
                        select(CartItem, Product)
                        .join(Product)
                        .where(CartItem.cart_id == cart.id)
                    )
                    result = await session.execute(stmt)
                    cart_items = result.all()

                    if not cart_items:
                        raise BadRequestError("Sepet boş.")

                    # Adresi bul
                    stmt = select(Address).where(
                        Address.user_id == actor.id if actor else Address.session_token == session_token
                    )
                    address = await session.scalar(stmt)

                    if not address:
                        raise BadRequestError("Adres bulunamadı.")

                    # Sipariş oluştur
                    order = Order(
                        user_id=actor.id if actor else None,
                        session_token=session_token if not actor else None,
                        address_id=address.id,
                        order_number=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
                        total_amount=sum(p.price * ci.quantity for ci, p in cart_items),
                        status=OrderStatus.PENDING
                    )
                    session.add(order)
                    await session.flush()

                    # Sipariş öğelerini oluştur
                    order_items = []
                    for cart_item, product in cart_items:
                        order_item = OrderItem(
                            order_id=order.id,
                            product_id=product.id,
                            quantity=cart_item.quantity,
                            price=product.price
                        )
                        session.add(order_item)
                        order_items.append((order_item, product))

                    # Response için veriyi hazırla
                    order_data = {
                        "id": str(order.id),
                        "user_id": str(order.user_id) if order.user_id else None,
                        "session_token": order.session_token,
                        "order_number": order.order_number,
                        "address": str(address.id),
                        "total_amount": float(order.total_amount),
                        "status": order.status,
                        "items": [
                            {
                                "id": str(oi.id),
                                "product_id": str(p.id),
                                "quantity": oi.quantity,
                                "price": float(oi.price),
                                "product_name": p.title
                            } for oi, p in order_items
                        ]
                    }

                    # MongoDB'ye kaydet
                    mongo_db = await init_mongo_db()
                    if mongo_db is None:
                        raise BadRequestError("MongoDB bağlantısı kurulamadı")

                    mongo_order = MongoOrder(
                        order_id=str(order.id),
                        order_number=order.order_number,
                        user=OrderUserDetail(
                            user_id=str(actor.id) if actor else None,
                            username=actor.username if actor else None,
                            email=actor.email if actor else None,
                            is_anonymous=actor is None
                        ),
                        address=OrderAddressDetail(
                            address_id=str(address.id),
                            name=address.name,
                            title=address.title,
                            country=address.country,
                            city=address.city,
                            district=address.district,
                            phone=address.phone,
                            address=address.address,
                            zip_code=address.zip_code
                        ),
                        items=[
                            OrderProductDetail(
                                product_id=str(product.id),
                                title=product.title,
                                description=product.description,
                                price=float(product.price),
                                quantity=cart_item.quantity,
                                total_price=float(product.price * cart_item.quantity)
                            ) for cart_item, product in cart_items
                        ],
                        total_amount=float(order.total_amount),
                        total_items=sum(ci.quantity for ci, _ in cart_items),
                        status=OrderStatus.PENDING.value,
                        session_token=session_token,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )

                    # MongoDB'ye kaydetmeyi dene, hata varsa fırlat
                    try:
                        await mongo_db.orders.insert_one(mongo_order.model_dump(by_alias=True))
                    except Exception as e:
                        raise BadRequestError(f"MongoDB'ye kayıt yapılamadı: {str(e)}")

                    # En son sepeti sil
                    await session.delete(cart)

                    return GeneralResponse(
                        status=201,
                        message="Sipariş başarıyla oluşturuldu.",
                        details=OrderView(**order_data)
                    )

                except Exception as e:
                    await session.rollback()
                    raise BadRequestError(f"Sipariş oluşturulurken bir hata oluştu: {str(e)}")

    @staticmethod
    async def get_orders(actor: Optional[User] = None):
        if not actor:
            raise BadRequestError("Kullanıcı girişi yapılmamış.")
        
        async with get_db() as session:
            async with session.begin():
                try:
                    if actor.role == UserRole.ADMIN:
                        query = (
                            select(Order)
                            .options(
                                selectinload(Order.items).selectinload(OrderItem.product),
                                selectinload(Order.address)
                            )
                        )
                    else:
                        query = (
                            select(Order)
                            .options(
                                selectinload(Order.items).selectinload(OrderItem.product),
                                selectinload(Order.address)
                            )
                            .where(Order.user_id == actor.id)
                        )

                    result = await session.execute(query)
                    orders = result.unique().scalars().all()

                    order_list = []
                    for order in orders:
                        order_data = {
                            "id": str(order.id),
                            "user_id": str(order.user_id) if order.user_id else None,
                            "session_token": order.session_token,
                            "order_number": order.order_number,
                            "address": str(order.address_id),
                            "total_amount": float(order.total_amount),
                            "status": order.status,
                            "items": [
                                {
                                    "id": str(item.id),
                                    "product_id": str(item.product_id),
                                    "quantity": item.quantity,
                                    "price": float(item.price),
                                    "product_name": item.product.title
                                } for item in order.items
                            ]
                        }
                        order_list.append(OrderView(**order_data))

                    return GeneralResponse(
                        status=200,
                        message="Siparişler listelendi.",
                        details=order_list
                    )

                except Exception as e:
                    raise BadRequestError(f"Siparişler listelenirken bir hata oluştu: {str(e)}")

    @staticmethod
    async def get_anonymous_orders(actor: Optional[User] = None):
        try:
            if not actor or actor.role != UserRole.ADMIN:
                raise BadRequestError("Bu işlem için admin yetkisi gerekli!")

            mongo_db = await init_mongo_db()
            if mongo_db is None:
                raise BadRequestError("MongoDB bağlantısı kurulamadı")

            # Session token'ı null olmayan tüm siparişleri getir
            cursor = mongo_db.orders.find(
                {"session_token": {"$ne": None}}
            ).sort("created_at", -1)
            
            orders = []
            async for order in cursor:
                # datetime alanlarını timestamp'e çevir
                order['created_at'] = int(order['created_at'].timestamp() * 1000)
                order['updated_at'] = int(order['updated_at'].timestamp() * 1000)
                # ObjectId'yi string'e çevir
                order['_id'] = str(order['_id'])
                orders.append(order)

            return GeneralResponse(
                status=200,
                message="Anonim siparişler listelendi.",
                details=orders
            )
        except Exception as e:
            raise BadRequestError(f"Anonim siparişler listelenirken bir hata oluştu: {str(e)}")

    @staticmethod
    async def get_order_detail(order_id: UUID, actor: Optional[User] = None):
        try:
            mongo_db = await init_mongo_db()
            order_detail = await mongo_db.orders.find_one({"order_id": str(order_id)})

            if not order_detail:
                raise BadRequestError("Sipariş bulunamadı.")

            if actor and actor.role != UserRole.ADMIN:
                if order_detail["user"]["user_id"] != str(actor.id):
                    raise BadRequestError("Bu siparişi görüntüleme yetkiniz yok.")

            # datetime ve ObjectId alanlarını dönüştür
            order_detail['created_at'] = int(order_detail['created_at'].timestamp() * 1000)
            order_detail['updated_at'] = int(order_detail['updated_at'].timestamp() * 1000)
            order_detail['_id'] = str(order_detail['_id'])

            return GeneralResponse(
                status=200,
                message="Sipariş detayları getirildi.",
                details=order_detail
            )
        except Exception as e:
            raise BadRequestError(f"Sipariş detayları getirilirken bir hata oluştu: {str(e)}")

