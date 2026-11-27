from datetime import datetime, timezone

from pydantic import ValidationError

from app.core.errors import DataStoreError
from app.repositories import json_storage
from app.schemas.order import Order, OrderCreate

FILENAME = "orders.json"


def load_orders() -> list[Order]:
    """Return every order in the data file as a list of Order objects"""
    orders = json_storage.read_list(FILENAME)
    try:
        return [Order.model_validate(order) for order in orders]
    except ValidationError as exc:
        raise DataStoreError(f"Invalid record in {FILENAME}") from exc


def get_by_id(order_id: str) -> Order | None:
    """Return the order with this id, or None if there is none."""
    for order in load_orders():
        if order.id == order_id:
            return order
    return None


def list_by_customer(customer_id: str) -> list[Order]:
    """Return every order placed by this customer."""
    return [order for order in load_orders() if order.customer_id == customer_id]


def add(order_data: OrderCreate) -> Order:
    # Give the new order the next id, a status and a time, save it and return it.
    data_json = json_storage.read_list(FILENAME)
    order = Order(
        id=json_storage.next_id(data_json, "O"),
        status="placed",
        created_at=datetime.now(timezone.utc).isoformat(),
        customer_id=order_data.customer_id,
        restaurant_id=order_data.restaurant_id,
        restaurant_name=order_data.restaurant_name,
        delivery_address=order_data.delivery_address,
        items=order_data.items,
        subtotal=order_data.subtotal,
        delivery_fee=order_data.delivery_fee,
        total=order_data.total,
    )
    data_json.append(order.model_dump())
    json_storage.write_list(FILENAME, data_json)
    return order

def delete(order_id: str) -> bool:
    """Remove the order with this id. Return False if there is none."""
    data_json = json_storage.read_list(FILENAME)
    remaining = [order for order in data_json if order["id"] != order_id]
    if len(remaining) == len(data_json):
        return False
    json_storage.write_list(FILENAME, remaining)
    return True