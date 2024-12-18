from src.utils.exceptions import AuthError
from fastapi import Cookie, Request, Header
from src.settings import config
from src.users.models import User

from datetime import datetime
from jose import JWTError, jwt
from pydantic import ValidationError


async def get_current_user(
        Authorization: str = Cookie(None),
        authorization: str = Header(None, alias="Authorization")
) -> User:
    token = None

    if Authorization is not None:
        token = Authorization

    if authorization is not None:
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization

    if token is None:
        return None

    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        email: str = payload.get("sub")
        expired_at: int = payload.get("exp")

        if datetime.fromtimestamp(expired_at) < datetime.now():
            raise AuthError("Token süresi dolmuş.")

        if email is None:
            raise AuthError("Geçersiz token formatı.")

        user = await User.by_email(email)
        if user is None:
            return None

        if user.is_active is False:
            raise AuthError("Kullanıcı aktif değil.")

        return user

    except (JWTError, ValidationError):
        return None