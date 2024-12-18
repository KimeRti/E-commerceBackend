from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Cookie

from starlette.responses import JSONResponse

from src.auth.current_user import get_current_user
from src.cart.schemas import CartItemCreate
from src.cart.service import CartService
from src.users.models import User

cart = APIRouter(
    prefix="/cart",
    tags=["cart"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@cart.get("")
async def cart_view(user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    resp = await CartService.cart_get(user, session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@cart.post("")
async def cart_add_item(item: CartItemCreate, user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    resp = await CartService.cart_add_item(item, user, session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@cart.put("/{item_id}")
async def cart_update_item(item_id: UUID, quantity: int, user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    resp = await CartService.cart_update_item_quantity(item_id, quantity, user, session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@cart.delete("/{item_id}")
async def cart_remove_item(item_id: UUID, user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    resp = await CartService.cart_remove_item(item_id, user, session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@cart.delete("")
async def cart_clear(user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    resp = await CartService.cart_clear(user, session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())