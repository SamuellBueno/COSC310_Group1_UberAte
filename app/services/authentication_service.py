from app.core.security import *
from app.repositories import user_repository
from app.schemas.user import RegisterRequest, User, UserPublic


def to_public(user: User) -> UserPublic:
    """copy only the safe fields of an account, password hash never goes to front"""
    return UserPublic(
        id=user.id,
        email=user.email,
        role=user.role,
        name=user.name,
        phone=user.phone,
        delivery_address=user.delivery_address,
        is_active=user.is_active,
    )


def register(payload: RegisterRequest) -> UserPublic:
    """create a customer account, the email can't already be in use"""
    if user_repository.get_by_email(payload.email) is not None:
        raise ValueError("An account with this email already exists")
    # hash password here, the repository only stores what it's given
    password_hash = hash_password(payload.password)
    user = user_repository.add_customer(payload, password_hash)
    return to_public(user)