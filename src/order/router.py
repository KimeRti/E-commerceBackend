from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from src.auth.current_user import get_current_user
from src.users.models import User
from src.utils.schemas import PaginationGet
from src.order.schemas import OrderCreate, OrderUpdate, OrderView
from uuid import UUID
from src.order.service import OrderService

orders = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@orders.post("/")
async def create_order(data: OrderCreate, current_user: User = Depends(get_current_user)):
    response = await OrderService.create(data, current_user)
    if response.status != 201:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.message)
    return JSONResponse(status_code=response.status, content=response.model_dump())


@orders.get("/{order_id}")
async def get_order(order_id: UUID, current_user: User = Depends(get_current_user)):
    response = await OrderService.get(order_id)
    if response.status != 200:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    return JSONResponse(status_code=response.status, content=response.model_dump())


@orders.patch("/{order_id}")
async def update_order(order_id: UUID, data: OrderUpdate, current_user: User = Depends(get_current_user)):
    response = await OrderService.update(order_id, data)
    if response.status != 200:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    return JSONResponse(status_code=response.status, content=response.model_dump())


@orders.delete("/{order_id}")
async def delete_order(order_id: UUID, current_user: User = Depends(get_current_user)):
    response = await OrderService.delete(order_id)
    if response.status != 200:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    return JSONResponse(status_code=response.status, content=response.model_dump())
