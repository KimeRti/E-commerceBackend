from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.utils.single_psql_db import init_psql_db
from src.utils.single_mongo_db import init_mongo_db
from src.utils.exceptions import GeneralException

from src.users.router import user
from src.product.router import product
from src.category.router import category
from src.auth.base.router import auth
from src.cart.router import cart
from src.order.router import order

app = FastAPI(
    title="E-Commerce API",
    description="Simple E-Commerce API with FastAPI and SQLAlchemy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Include routers
app.include_router(user)
app.include_router(product)
app.include_router(category)
app.include_router(auth)
app.include_router(cart)
app.include_router(order)


origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
async def startup():
    await init_psql_db()
    await init_mongo_db()


@app.exception_handler(GeneralException)
async def general_exception_handler(request: Request, exc: GeneralException):
    return JSONResponse(status_code=exc.general_response.status, content=exc.general_response.model_dump(),
                        headers=exc.headers)


@app.exception_handler(NotImplementedError)
async def not_implemented_error_handler(request: Request, exc: NotImplementedError):
    return JSONResponse(status_code=501, content={"message": str(exc)})
