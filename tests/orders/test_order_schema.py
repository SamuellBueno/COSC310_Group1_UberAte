import pytest
from pydantic import ValidationError

from app.schemas.order import Order, OrderCreate, OrderItem

ITEMS = [{"menu_item_id": "M1", "name": "Burger", "unit_price": 10.0, "quantity": 2}]

#OrderItem
def test_valid_order_item_is_accepted():
    item = OrderItem(menu_item_id="M1", name="Burger", unit_price=10.0, quantity=2)
    assert item.quantity == 2

def test_order_item_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        OrderItem(menu_item_id="M1", name="Burger", unit_price=10.0, quantity=0)

#OrderCreate
def test_valid_order_create_is_accepted():
    order = OrderCreate(customer_id="U1", restaurant_id="A1", restaurant_name="DonaldMac", delivery_address="1 Test St, Kelowna", items=ITEMS, subtotal=20.0, delivery_fee=0.0, total=20.0)
    assert order.total == 20.0

def test_order_create_rejects_empty_items():
    with pytest.raises(ValidationError):
        OrderCreate(customer_id="U1", restaurant_id="A1", restaurant_name="DonaldMac", items=[], total=0)

def test_order_create_with_id_is_denied():
    with pytest.raises(ValidationError):
        OrderCreate(id="O1", customer_id="U1", restaurant_id="A1", restaurant_name="DonaldMac", items=ITEMS, total=20.0)

#Order
def test_order_requires_an_id():
    with pytest.raises(ValidationError):
        Order(status="placed", created_at="2026-11-18", customer_id="U1", restaurant_id="A1", restaurant_name="DonaldMac", items=ITEMS, total=20.0)