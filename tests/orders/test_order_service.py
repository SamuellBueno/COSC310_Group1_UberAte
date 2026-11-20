import pytest
from app.core.errors import NotFoundError, PermissionDeniedError
from app.repositories.order_repository import add
from app.schemas.order import OrderCreate
from app.services.order_service import list_my_orders, get_my_order

from app.schemas.order import OrderCreate, OrderItem

ITEMS = [OrderItem(menu_item_id="M1", name="Burger", unit_price=10.0, quantity=2)]

def make_order(customer_id="U1"):
    return OrderCreate(customer_id=customer_id, restaurant_id="A1", restaurant_name="DonaldMac", items=ITEMS, total=20.0)

# normal flow
def test_get_my_order():
    order = add(make_order("U1"))
    assert get_my_order(order.id, "U1") == order

def test_list_my_orders_only_returns_their_orders():
    add(make_order("U1"))
    add(make_order("U2"))
    orders = list_my_orders("U1")
    assert len(orders) == 1
    assert orders[0].customer_id == "U1"

# error handling
def test_get_unknown_id():
    with pytest.raises(NotFoundError):
        get_my_order("O999", "U1")

def test_get_other_customers_order_is_refused():
    order = add(make_order("U1"))
    with pytest.raises(PermissionDeniedError):
        get_my_order(order.id, "U2")