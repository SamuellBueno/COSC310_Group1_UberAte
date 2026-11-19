from app.core.errors import PermissionDeniedError
from app.schemas.restaurant import Restaurant
from app.schemas.user import User


def ensure_can_manage(actor: User, restaurant: Restaurant) -> None:
    # Allow admins to manage any restaurant and owners can manage their own
    if actor.role == "admin":
        return
    if actor.role == "restaurant_owner" and restaurant.owner_id == actor.id:
        return
    raise PermissionDeniedError("You can only manage your own restaurant")