from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.auth.current_user import get_current_user
from src.users.models import User
from src.basket.service import BasketService
from uuid import UUID

basket = APIRouter(
    prefix="/basket",
    tags=["basket"],
)


@basket.post("/add-to-basket/{product_id}")
async def add_to_basket(product_id: UUID, quantity: int, current_user: User = Depends(get_current_user)):
    resp = await BasketService.add_to_basket(current_user.id, product_id, quantity)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@basket.get("/view-basket")
async def view_basket(current_user: User = Depends(get_current_user)):
    resp = await BasketService.view_basket(current_user.id)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@basket.delete("/remove-from-basket/{product_id}")
async def remove_from_basket(product_id: UUID, quantity: int, current_user: User = Depends(get_current_user)):
    resp = await BasketService.remove_from_basket(current_user.id, product_id, quantity)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())