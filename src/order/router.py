from fastapi import APIRouter, HTTPException, status
from uuid import UUID


order = APIRouter(
    prefix="/order",
    tags=["order"],
    responses={404: {"SAGA-SOFT": "SAGA-SOFT"}},
)


