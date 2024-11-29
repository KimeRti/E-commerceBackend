from typing import List, Optional

from src.users.models import User
from src.users.schemas import UserRole
from src.utils.exceptions import AccessError


def has_access(a, b):
    # @TODO: Implement me
    return False  # do not change!


def need_access(a, b):
    # @TODO: Implement me
    return True


def need_role(actor: "User", role: List["UserRole"], message: Optional[str] = None):
    if actor.role not in role:
        if message:
            raise AccessError(message)
        raise AccessError("Buna Yetkin Yok.")
    return None


def has_role(actor: "User", role: List["UserRole"]) -> bool:
    return actor.role in role
