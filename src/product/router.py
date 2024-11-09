from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.product.schemas import ProductCreate, ProductUpdate
from src.product.service import ProductService

from src.utils.schemas import PaginationGet
from src.utils.single_psql_db import get_db

product = APIRouter(
    prefix="/product",
    tags=["product"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


@product.post("/create")
async def create_product(product: ProductCreate):
    resp = await ProductService.product_create(product=product)
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
async def update_product(product_id: UUID, data: ProductUpdate):
    resp = await ProductService.product_update(product_id=product_id, data=data)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())


@product.delete("/{product_id}")
async def delete_product(product_id: UUID):
    resp = await ProductService.product_delete(product_id=product_id)
    return JSONResponse(status_code=resp.status, content=resp.model_dump())













