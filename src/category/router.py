from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from src.auth.current_user import get_current_user
from src.category.schemas import CategoryCreate
from src.category.service import CategoryService
from src.users.models import User
from src.utils.schemas import PaginationGet

category = APIRouter(
    prefix="/category",
    tags=["category"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@category.post("")
async def create_category(category: CategoryCreate, current_user: User = Depends(get_current_user)):
    resp = await CategoryService.create(category=category, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@category.get("")
async def get_categories(data: PaginationGet = Depends()):
    content = await CategoryService.get(pagination_data=data)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@category.get("/{category_id}")
async def get_category(category_id: UUID):
    content = await CategoryService.get_category(category_id=category_id)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@category.put("/{category_id}")
async def update_category(category_id: UUID, data: CategoryCreate, current_user: User = Depends(get_current_user)):
    content = await CategoryService.update(category_id=category_id, data=data, actor=current_user)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@category.delete("/{category_id}")
async def delete_category(category_id: UUID, current_user: User = Depends(get_current_user)):
    content = await CategoryService.delete(category_id=category_id, actor=current_user)
    return JSONResponse(status_code=content.status, content=content.model_dump())