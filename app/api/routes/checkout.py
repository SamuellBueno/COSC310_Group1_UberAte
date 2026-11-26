from fastapi import APIRouter, Depends
from app.api.role_checks import require_customer
from app.schemas.order import CheckoutRequest, Order
from app.schemas.user import User
from app.services import checkout_service

router = APIRouter(tags=["checkout"])

@router.post("/checkout", response_model=Order, status_code=201, summary="Place an order from my cart",
             description="Turns the signed-in customer's cart into an order. expected_total is the total the customer saw in the cart.",
             responses={400: {"description": "Cart is empty, an item is unavailable, or the customer has no delivery address"},
                        401: {"description": "Not signed in"},
                        403: {"description": "Not a customer or account is deactivated"},
                        409: {"description": "The total has changed since the customer reviewed the cart"}})

def place_order(request: CheckoutRequest, current_user: User = Depends(require_customer)):
    return checkout_service.checkout(current_user.id, request.expected_total)