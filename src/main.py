from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jose import jwt
from starlette import status

from src.settings import config
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
    version="2.0",
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


origins = ["http://localhost:3000", "http://192.168.1.102:55684/api"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def create_access_token(data: dict,
                        expires_delta: timedelta = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


@app.middleware("http")
async def add_session_token(request: Request, call_next):
    if "session_token" not in request.cookies:
        access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": "user"}, expires_delta=access_token_expires
        )

        response = await call_next(request)
        response.set_cookie(
            key="session_token", value=access_token, httponly=True, max_age=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    else:
        response = await call_next(request)

    return response


def verify_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/profile")
async def get_profile(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

    user_data = verify_token(token)
    return {"user": user_data["sub"]}

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
