from fastapi import APIRouter, Depends

from app.api.role_checks import require_customer
from app.schemas.cart import CartItemAdd, CartView
from app.schemas.user import User
from app.services import cart_service

router = APIRouter(tags=["cart"])


@router.get(
    "/cart",
    response_model=CartView,
    status_code=200,
    summary="Get or create active cart",
    description="Returns the signed-in customer's active cart, or creates a new empty cart if none exists.",
    responses={
        200: {"description": "Active cart returned"},
        401: {"description": "Not signed in"},
        403: {"description": "Not a customer or account is deactivated"},
    },
)
def get_cart(current_user: User = Depends(require_customer)):
    return cart_service.get_or_create_cart(current_user.id)


@router.post(
    "/cart/items",
    response_model=CartView,
    status_code=200,
    summary="Add a menu item to the active cart",
    description="Adds an available menu item to the signed-in customer's cart, incrementing quantity if already present.",
    responses={
        200: {"description": "Updated cart returned"},
        400: {"description": "Menu item is unavailable"},
        401: {"description": "Not signed in"},
        403: {"description": "Not a customer or account is deactivated"},
        404: {"description": "Menu item not found"},
        409: {"description": "Menu item belongs to a different restaurant"},
    },
)
def add_cart_item(
    payload: CartItemAdd,
    current_user: User = Depends(require_customer),
) -> CartView:
    return cart_service.add_item(current_user.id, payload)