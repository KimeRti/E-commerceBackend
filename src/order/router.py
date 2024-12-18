from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Header, Request, Cookie
from starlette.responses import JSONResponse

from src.auth.current_user import get_current_user
from src.order.service import OrderService
from src.users.models import User
from src.utils.exceptions import BadRequestError
from src.utils.schemas import PaginationGet

order = APIRouter(
    prefix="/order",
    tags=["order"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@order.post("")
async def create_order(request: Request, current_user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    if current_user is None:
        try:
            current_user = await get_current_user(request=request)
        except Exception:
            current_user = None

    if not current_user and not session_token:
        raise BadRequestError("Kullanıcı bilgisi bulunamadı !")

    resp = await OrderService.create_order(current_user, session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@order.get("")
async def get_orders(current_user: Optional[User] = Depends(get_current_user)):
    resp = await OrderService.get_orders(current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@order.get("/anonymous")
async def get_anonymous_orders(current_user: Optional[User] = Depends(get_current_user)):
    resp = await OrderService.get_anonymous_orders(current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@order.get("/cancelled")
async def get_cancelled_orders(current_user: Optional[User] = Depends(get_current_user)):
    resp = await OrderService.get_cancelled_orders(current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@order.get("/{order_id}")
async def get_order_detail(
    order_id: UUID,
    current_user: Optional[User] = Depends(get_current_user)
):
    resp = await OrderService.get_order_detail(order_id, current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@order.delete("/{order_id}")
async def cancel_order(order_id: UUID, reason: Optional[str] = None, current_user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    resp = await OrderService.cancel_order(order_id, current_user, session_token, reason)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())



