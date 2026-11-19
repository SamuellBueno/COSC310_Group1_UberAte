import json
import pytest
from app.core.errors import BusinessRuleError, ConflictError, PermissionDeniedError
from app.repositories import cart_repository, menu_item_repository, order_repository
from app.schemas.cart import Cart, CartLine
from app.services import pricing
from app.services.checkout_service import checkout

def put_item_in_cart(customer_id="U4"):
    item = next(i for i in menu_item_repository.list_all() if i.active and i.available)
    cart_repository.save(Cart(id="C-test", customer_id=customer_id, restaurant_id=item.restaurant_id,
                              items=[CartLine(menu_item_id=item.id, quantity=2)]))
    total = float(pricing.totals([pricing.line_total(item.price, 2)])[2])
    return item, total

def test_checkout_saves_order_and_clears_cart():
    item, total = put_item_in_cart()
    order = checkout("U4", total)
    assert order_repository.get_by_id(order.id) is not None
    assert order.items[0].name == item.name
    assert order.total == total
    cart = cart_repository.get_by_customer("U4")
    assert cart is not None
    assert cart.items == []

def test_empty_cart_is_rejected():
    with pytest.raises(BusinessRuleError):
        checkout("U4", 0)

def test_wrong_expected_total_is_rejected_and_nothing_saved():
    item, total = put_item_in_cart()
    with pytest.raises(ConflictError):
        checkout("U4", total + 1)
    assert order_repository.load_orders() == []
    cart = cart_repository.get_by_customer("U4")
    assert cart is not None
    assert len(cart.items) == 1

def test_unavailable_item_is_rejected(isolated_data):
    item, total = put_item_in_cart()
    path = isolated_data / "menu_items.json"
    menu = json.loads(path.read_text(encoding="utf-8"))
    for m in menu:
        if m["id"] == item.id:
            m["available"] = False
    path.write_text(json.dumps(menu), encoding="utf-8")
    with pytest.raises(BusinessRuleError):
        checkout("U4", total)

def test_price_change_after_review_is_rejected(isolated_data):
    item, total = put_item_in_cart()
    path = isolated_data / "menu_items.json"
    menu = json.loads(path.read_text(encoding="utf-8"))
    for m in menu:
        if m["id"] == item.id:
            m["price"] = 99.0
    path.write_text(json.dumps(menu), encoding="utf-8")
    with pytest.raises(ConflictError):
        checkout("U4", total)

def test_deactivated_customer_is_rejected(isolated_data):
    item, total = put_item_in_cart()
    path = isolated_data / "users.json"
    users = json.loads(path.read_text(encoding="utf-8"))
    for u in users:
        if u["id"] == "U4":
            u["is_active"] = False
    path.write_text(json.dumps(users), encoding="utf-8")
    with pytest.raises(PermissionDeniedError):
        checkout("U4", total)