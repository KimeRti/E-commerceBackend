from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select

from src.auth.current_user import get_current_user
from src.product.models import ProductPhotos

from src.product.schemas import ProductCreate, ProductUpdate, PhotoResponse
from src.product.service import ProductService
from src.settings import config
from src.users.models import User

from src.utils.schemas import PaginationGet
from src.utils.single_psql_db import get_db

product = APIRouter(
    prefix="/product",
    tags=["product"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@product.post("/create")
async def create_product(product: ProductCreate, current_user: User = Depends(get_current_user)):
    resp = await ProductService.product_create(product=product, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@product.get("")
async def get_products(data: PaginationGet = Depends()):
    content = await ProductService.get_products(pagination_data=data)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@product.get("/{product_id}")
async def get_product(product_id: UUID):
    content = await ProductService.get_product(product_id=product_id)
    return JSONResponse(status_code=content.status, content=content.model_dump())


@product.put("/{product_id}")
async def update_product(product_id: UUID, data: ProductUpdate, current_user: User = Depends(get_current_user)):
    resp = await ProductService.product_update(product_id=product_id, data=data, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@product.delete("/{product_id}")
async def delete_product(product_id: UUID, current_user: User = Depends(get_current_user)):
    resp = await ProductService.product_delete(product_id=product_id, actor=current_user)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@product.get("{product_id}/photos", response_model=list[PhotoResponse])
async def get_room_photos(product_id: UUID):
    async with get_db() as db:
        result = await db.execute(select(ProductPhotos).where(ProductPhotos.product_id == product_id))
        photos = result.scalars().all()

    return [
        PhotoResponse(id=photo.id, url=f"{config.BASE_URL}/uploads/products/{Path(photo.url).name}")
        for photo in photos
    ]


@product.post("/{product_id}/upload-photo")
async def upload_photo(product_id: UUID, file: UploadFile):
    resp = await ProductService.upload_photo(product_id=product_id, file=file)
    return JSONResponse(status_code=200, content=resp.model_dump())
