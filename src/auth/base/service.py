from src.auth.base.schemas import RegisterSchema, LoginSchema, ChangePassword

from src.utils.schemas import GeneralResponse
from src.utils.exceptions import AuthError, NotFoundError
from src.utils.single_psql_db import get_db

from src.users.schemas import UserCreate, UserMeView, UserMiniView
from src.users.models import User

from src.settings import config

from datetime import datetime, timedelta
from jose import jwt

import bcrypt


# from passlib.context import CryptContext
# from passlib import pwd

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password):  # no need i did in schema field validator
#     return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password.encode('utf-8'))
    # return pwd_context.verify(plain_password, hashed_password)


class AuthService:

    @staticmethod
    async def register(register_schema: RegisterSchema):
        new_user = UserCreate(**register_schema.model_dump())
        print("k")
        user = await User.create(new_user)
        access_token = AuthService.create_access_token(
            data={"sub": user.email}, expires_delta=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return GeneralResponse(status=201, message="Registered successfully", details={
            "token": access_token,
            "token_type": "bearer",
            "user": UserMiniView.model_validate(user).model_dump()
        })

    @staticmethod
    async def authenticate(identifier: str, password: str):
        user = await User.by_email(identifier)
        if not user:
            raise NotFoundError("User not found")
        if user.is_active is False:
            raise AuthError("User is not active")
        if not verify_password(password, user.password):
            raise AuthError("Şifreniz hatalı")
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: int):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def login(login_schema: LoginSchema):
        user = await AuthService.authenticate(identifier=login_schema.identifier,
                                              password=login_schema.password.get_secret_value())
        access_token = AuthService.create_access_token(
            data={"sub": user.email}, expires_delta=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

        return GeneralResponse(status=200, message="Logged in successfully", details={
            "token": access_token,
            "token_type": "bearer",
            "user": UserMeView.model_validate(user).model_dump()
        })

    # @staticmethod
    # async def google_login(credentials: str):
    #     # @TODO Google login
    #     async with httpx.AsyncClient() as client:
    #         resp = await client.post("https://oauth2.googleapis.com/token", data={
    #             "code": credentials,
    #             "client_id": config.GOOGLE_CLIENT_ID,
    #             "client_secret": config.GOOGLE_CLIENT_SECRET,
    #             "redirect_uri": config.GOOGLE_REDIRECT_URI,
    #             "grant_type": "authorization_code",
    #         })
    #         if resp.status_code != 200:
    #             raise AuthError("Google login failed")
    #         resp_json = resp.json()
    #         resp = await client.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={
    #             "Authorization": f"Bearer {resp_json['access_token']}"
    #         })
    #         if resp.status_code != 200:
    #             raise AuthError("Google login failed")
    #         resp_json = resp.json()
    #         user = await User.by_email(User.email == resp_json["email"])
    #         print("user bu", user)
    #         if user is None:
    #             user = User.create(
    #                 UserCreate(
    #                     email=resp_json["email"],
    #                     password=pwd.genword(length=24, charset="ascii_50"),
    #                     first_name=resp_json["given_name"],
    #                     last_name=resp_json["family_name"],
    #                 )
    #             )
    #         access_token = AuthService.create_access_token(
    #             data={"sub": user.email}, expires_delta=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    #         )
    #         return GeneralResponse(status=200, message="Logged in successfully", details=access_token)

    @staticmethod
    async def change_password(change_schema: ChangePassword, actor: User):
        if not verify_password(change_schema.old_password.get_secret_value(), actor.password):
            raise AuthError("Şifreler eşleşmiyor.")
        async with get_db() as db:
            user = await db.get(User, actor.id)
            user.password = bcrypt.hashpw(change_schema.new_password.get_secret_value().encode('utf-8'),
                                          bcrypt.gensalt()).decode('utf-8')
            await db.commit()
        return GeneralResponse(status=200, message="Şifre başarıyla değiştirildi.")
