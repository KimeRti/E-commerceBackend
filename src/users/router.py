from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from src.users.schemas import UserCreate
from src.users.service import UserService
from src.utils.schemas import PaginationGet

user = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@user.post("/user/create")
async def create_user(user: UserCreate):
    resp = await UserService.create(user=user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@user.get("")
async def get_users(data: PaginationGet = Depends()):
    content = await UserService.get_users(pagination_data=data)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@user.get("/users/{user_id}")
async def get_user(user_id: UUID):
    content = await UserService.get_user(user_id=user_id)
    return JSONResponse(status_code=content.status, content=content.model_dump())




