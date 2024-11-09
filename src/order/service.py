from uuid import UUID
from sqlalchemy import select
from src.utils.exceptions import NotFoundError
from src.utils.schemas import GeneralResponse
from src.users.models import User
from src.order.models import Order
from src.utils.single_psql_db import get_db


class OrderService:
    @staticmethod
    async def create(data, user: User):
        async with get_db() as db:
            new_order = await Order.create(db, user_id=user.id, total_amount=data.total_amount, status=data.status)
            return GeneralResponse(
                message="Sipariş başarıyla oluşturuldu",
                status=201,
                details={"id": str(new_order.id), "total_amount": new_order.total_amount, "status": new_order.status}
            )

    @staticmethod
    async def update(order_id: UUID, data):
        async with get_db() as db:
            order = await Order.update(db, order_id, total_amount=data.total_amount, status=data.status)
            if not order:
                raise NotFoundError("Sipariş bulunamadı.")
            return GeneralResponse(
                message="Sipariş başarıyla güncellendi",
                status=200,
                details={"id": str(order.id), "total_amount": order.total_amount, "status": order.status}
            )

    @staticmethod
    async def get(order_id: UUID):
        async with get_db() as db:
            order = await Order.get(db, order_id)
            if not order:
                raise NotFoundError("Sipariş bulunamadı.")
            return GeneralResponse(
                message="Sipariş bulundu",
                status=200,
                details={"id": str(order.id), "total_amount": order.total_amount, "status": order.status}
            )

    @staticmethod
    async def delete(order_id: UUID):
        async with get_db() as db:
            order = await Order.delete(db, order_id)
            if not order:
                raise NotFoundError("Sipariş bulunamadı.")
            return GeneralResponse(
                message="Sipariş başarıyla silindi",
                status=200
            )
