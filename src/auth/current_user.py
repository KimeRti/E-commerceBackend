from src.utils.exceptions import AuthError
from fastapi import Cookie, Request, Header
from src.settings import config
from src.users.models import User

from datetime import datetime

from jose import JWTError, jwt
from pydantic import ValidationError


async def get_current_user(Authorization: str = Cookie(None), auth_header: str = Header(None)) -> User:
    if Authorization is None and auth_header is None:
        raise AuthError("Token yok.")
    # @TODO -> gzip zamanı buraya ekleme yaparsın
    if Authorization is not None:
        token = Authorization
    if auth_header is not None:
        token = auth_header
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        email: str = payload.get("sub")
        expired_at: int = payload.get("exp")
        if datetime.fromtimestamp(expired_at) < datetime.now():
            raise AuthError("token.not.valid")
        if email is None:
            raise AuthError("token.not.valid")
    except (JWTError, ValidationError):
        raise AuthError("token.not.valid")
    user = await User.by_email(email)
    if user is None:
        raise AuthError("token.not.valid")
    if user.is_active is False:
        raise AuthError("token.not.valid")
    return user
