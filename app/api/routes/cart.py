from fastapi import APIRouter, Depends

from app.api.role_checks import require_customer
from app.schemas.cart import CartView
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