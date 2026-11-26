import pytest
from app.core.errors import DataStoreError
from app.repositories.order_repository import load_orders, get_by_id, list_by_customer, add
from app.schemas.order import Order, OrderCreate

ITEMS = [{"menu_item_id": "M1", "name": "Burger", "unit_price": 10.0, "quantity": 2}]

def make_order(customer_id="U1"):
    return OrderCreate(customer_id=customer_id, restaurant_id="A1", restaurant_name="DonaldMac", delivery_address="1 Test St, Kelowna", items=ITEMS, subtotal=20.0, delivery_fee=0.0, total=20.0)

def test_load_orders_list():
    orders = load_orders()

    assert isinstance(orders, list)

def test_add_is_saved_to_json():
    order = add(make_order())

    saved = get_by_id(order.id)
    assert isinstance(saved, Order)

def test_add_gives_placed_status():
    order = add(make_order())

    assert order.status == "placed"

def test_add_keeps_item_name_and_price():
    order = add(make_order())

    saved = get_by_id(order.id)
    assert saved is not None
    assert saved.items[0].name == "Burger"
    assert saved.items[0].unit_price == 10.0

def test_add_gives_different_ids():
    first = add(make_order())
    second = add(make_order())

    assert first.id != second.id

def test_get_by_id_does_not_exist():
    assert get_by_id("id does not exist") is None

def test_list_by_customer_only_returns_their_orders():
    add(make_order("U1"))
    add(make_order("U2"))

    orders = list_by_customer("U1")
    assert len(orders) == 1
    assert orders[0].customer_id == "U1"

def test_list_by_customer_with_no_orders():
    assert list_by_customer("nobody") == []

def test_broken_record_raises_data_store_error(isolated_data):
    # broken order records raise a data store error
    (isolated_data / "orders.json").write_text('[{"id": "O1"}]', encoding="utf-8")

    with pytest.raises(DataStoreError):
        load_orders()