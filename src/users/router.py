from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from src.auth.current_user import get_current_user
from src.users.models import User
from src.users.schemas import UserCreate, PhotoResponse
from src.users.service import UserService
from src.utils.schemas import PaginationGet
from src.utils.single_psql_db import get_db
from src.settings import config

user = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@user.post("")
async def create_user(user: UserCreate, current_user: User = Depends(get_current_user)):
    resp = await UserService.create(user=user, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@user.get("")
async def get_users(data: PaginationGet = Depends()):
    content = await UserService.get_users(pagination_data=data)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@user.get("/users/{user_id}")
async def get_user(user_id: UUID):
    content = await UserService.get_user(user_id=user_id)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@user.post("/upload")
async def upload_avatar(user_id: UUID, file: UploadFile):
    resp = await UserService.upload_avatar(user_id=user_id, file=file)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@user.get("/{user_id}/avatar", response_model=PhotoResponse)
async def get_avatar(user_id: UUID):
    user = await User.get(user_id)
    return PhotoResponse(
        url=f"{config.BASE_URL}/uploads/avatars/{Path(user.avatar).name}"
    )