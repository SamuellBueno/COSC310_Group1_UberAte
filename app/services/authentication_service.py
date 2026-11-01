from app.core.security import *
from app.repositories import user_repository, session_repository
from app.schemas.user import *


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

def login(payload: LoginRequest) -> LoginResponse:
    """check the email and password, then start a session"""
    user = user_repository.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise ValueError("Wrong email or password")
    if not user.is_active:
        raise ValueError("This account is deactivated")
    # everything checks out, save a session with a fresh random id
    session = session_repository.add(user.id)
    return LoginResponse(session_id=session.session_id, user=to_public(user))


def logout(session_id: str) -> None:
    """sign out: delete the session so its id stops working"""
    session_repository.delete(session_id)


def get_user_for_session(session_id: str) -> User | None:
    """which account owns this session id
    None if the id is unknown or the session has expired"""
    session = session_repository.get(session_id)
    if session is None or is_expired(session.expires_at):
        return None
    return user_repository.get_by_id(session.user_id)