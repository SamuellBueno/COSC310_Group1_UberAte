from app.repositories import order_repository
from app.core.errors import NotFoundError, PermissionDeniedError
from app.schemas.order import Order

def list_my_orders(customer_id: str) -> list[Order]:
    return order_repository.list_by_customer(customer_id)

def get_my_order(order_id: str, customer_id: str) -> Order:
    order = order_repository.get_by_id(order_id)

    if order is None:
        raise NotFoundError(f"Order '{order_id}' does not exist.")
    if order.customer_id != customer_id:
        raise PermissionDeniedError("You can only view your own orders.")

    return order