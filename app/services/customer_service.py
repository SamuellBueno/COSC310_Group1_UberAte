from app.repositories import user_repository
from app.core.errors import PermissionDeniedError, NotFoundError, BusinessRuleError
from app.schemas.user import User, UserPublic, ProfileUpdate
from app.services.authentication_service import to_public

def require_active_customer(customer_id: str) -> User:
    """load the customer as stored right now, every cart and checkout rule starts here"""
    user = user_repository.get_by_id(customer_id)
    if user is None or user.role != "customer":
        raise NotFoundError(f"Customer '{customer_id}' not found")
    if not user.is_active:
        raise PermissionDeniedError("This account is deactivated")
    return user

def get_profile(customer_id: str) -> UserPublic:
    return to_public(require_active_customer(customer_id))

def update_profile(customer_id: str, payload: ProfileUpdate) -> UserPublic:
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise BusinessRuleError("Send at least one field to update")

    require_active_customer(customer_id)
    return to_public(user_repository.update(customer_id, changes))

def deactivate(customer_id: str) -> UserPublic:
    require_active_customer(customer_id)
    return to_public(user_repository.update(customer_id, {"is_active": False}))