from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Header
from fastapi.responses import JSONResponse

from src.auth.current_user import get_current_user
from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate, AddressCreate
from src.users.service import UserService
from src.utils.exceptions import BadRequestError
from src.utils.schemas import PaginationGet

user = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@user.post("")
async def create_user(user: UserCreate, current_user: User = Depends(get_current_user)):
    resp = await UserService.create(user=user, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@user.post("/address")
async def create_address(request: Request, address: AddressCreate, current_user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Header(None)):
    if current_user is None:
        try:
            current_user = await get_current_user(request=request)
        except Exception:
            current_user = None

    if not current_user and not session_token:
        raise BadRequestError("Kullanıcı bilgisi bulunamadı !")

    resp = await UserService.create_address(address=address, actor=current_user, session_token=session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@user.get("/addresses")
async def get_addresses(request: Request, current_user: Optional[User] = Depends(get_current_user), session_token: Optional[str] = Header(None)):
    if current_user is None:
        try:
            current_user = await get_current_user(request=request)
        except Exception:
            current_user = None

    if not current_user and not session_token:
        raise BadRequestError("Kullanıcı bilgisi bulunamadı !")

    resp = await UserService.get_address(actor=current_user, session_token=session_token)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@user.get("")
async def get_users(data: PaginationGet = Depends()):
    content = await UserService.get_users(pagination_data=data)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@user.get("/users/{user_id}")
async def get_user(user_id: UUID):
    content = await UserService.get_user(user_id=user_id)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@user.put("/{user_id}")
async def update_user(user_id: UUID, data: UserUpdate, current_user: User = Depends(get_current_user)):
    resp = await UserService.update(user_id=user_id, data=data, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@user.delete("/{user_id}")
async def delete_user(user_id: UUID, current_user: User = Depends(get_current_user)):
    resp = await UserService.delete(user_id=user_id, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())