from fastapi import APIRouter, Depends
from app.api.role_checks import require_customer
from app.schemas.order import Order
from app.schemas.user import User
from app.services import order_service

router = APIRouter(tags=["orders"])

@router.get("/orders", response_model=list[Order], summary="List my orders",
            description="Returns the signed-in customer's orders, newest first.",
            responses={401: {"description": "Not signed in"},
                       403: {"description": "Not a customer or account is deactivated"}})
def list_my_orders(current_user: User = Depends(require_customer)):
    return order_service.list_my_orders(current_user.id)

@router.get("/orders/{order_id}", response_model=Order, summary="Get one of my orders",
            responses={401: {"description": "Not signed in"},
                       403: {"description": "Not a customer, account is deactivated, or the order belongs to another customer"},
                       404: {"description": "No order exists with this ID"}})
def get_my_order(order_id: str, current_user: User = Depends(require_customer)):
    return order_service.get_my_order(order_id, current_user.id)