from typing import Optional, Any, Dict

from src.utils.schemas import GeneralResponse


class GeneralException(Exception):
    def __init__(self, message: str, status: Optional[int] = 400, code: Optional[str] = "GeneralException",
                 details: Optional[Any] = None, headers: Optional[Dict[str, str]] = None):
        self.general_response: GeneralResponse = GeneralResponse(status=status, message=message, code=code,
                                                                 details=details)
        self.headers = headers


class AuthError(GeneralException):

    def __init__(self, message: Optional[str] = "Giriş yapınız.", status: Optional[int] = 401,
                 code: Optional[str] = "AuthException",
                 details: Optional[Any] = None, headers: Optional[Dict[str, str]] = None):
        super().__init__(message, status, code, details, headers)


class AccessError(GeneralException):

    def __init__(self, message: Optional[str] = "Erişiminiz yok. İletişime geçiniz.", status: Optional[int] = 403,
                 code: Optional[str] = "AccessException",
                 details: Optional[Any] = None, headers: Optional[Dict[str, str]] = None):
        super().__init__(message, status, code, details, headers)


class NotFoundError(GeneralException):

    def __init__(self, message: Optional[str] = "Bulunamadı.", status: Optional[int] = 404,
                 code: Optional[str] = "NotFoundException",
                 details: Optional[Any] = None, headers: Optional[Dict[str, str]] = None):
        super().__init__(message, status, code, details, headers)


class InternalError(GeneralException):

    def __init__(self, message: Optional[str] = "Sunucu Hatası. Lütfen iletişime geçiniz", status: Optional[int] = 500,
                 code: Optional[str] = "InternalException",
                 details: Optional[Any] = None, headers: Optional[Dict[str, str]] = None):
        super().__init__(message, status, code, details, headers)


class BadRequestError(GeneralException):

    def __init__(self, message: Optional[str] = "Geçersiz İstek Hatası", status: Optional[int] = 400,
                 code: Optional[str] = "BadRequestException",
                 details: Optional[Any] = None, headers: Optional[Dict[str, str]] = None):
        super().__init__(message, status, code, details, headers)
