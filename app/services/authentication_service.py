from app.core.security import hash_password, is_expired, verify_password
from app.core.errors import AuthenticationError, ConflictError, PermissionDeniedError
from app.repositories import session_repository, user_repository
from app.schemas.user import LoginRequest, LoginResponse, RegisterRequest, User, UserPublic


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
        raise ConflictError("An account with this email already exists")
    # hash password here, the repository only stores what it's given
    password_hash = hash_password(payload.password)
    user = user_repository.add_customer(payload, password_hash)
    return to_public(user)

def login(payload: LoginRequest) -> LoginResponse:
    """check the email and password, then start a session"""
    user = user_repository.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AuthenticationError("Wrong email or password")
    if not user.is_active:
        raise PermissionDeniedError("This account is deactivated")
    # everything checks out, save a session with a fresh random id
    session = session_repository.add(user.id)
    return LoginResponse(session_id=session.session_id, user=to_public(user))


def logout(session_id: str) -> None:
    """sign out: delete the session so its id stops working"""
    session_repository.delete(session_id)


def get_user_for_session(session_id: str) -> User:
    """which account owns this session id
    raises AuthenticationError if the id is unknown, the session has expired,
    or the account no longer exists
    raises PermissionDeniedError if the account has been deactivated"""
    session = session_repository.get(session_id)
    if session is None or is_expired(session.expires_at):
        raise AuthenticationError("Your session is missing or expired, sign in again")
    user = user_repository.get_by_id(session.user_id)
    if user is None:
        raise AuthenticationError("Your session is missing or expired, sign in again")
    if not user.is_active:
        raise PermissionDeniedError("This account is deactivated")
    return user