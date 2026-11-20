import json
from decimal import Decimal

from app.repositories import cart_repository, session_repository
from app.schemas.cart import Cart, CartLine


def _auth_headers(user_id: str) -> dict[str, str]:
    session = session_repository.add(user_id)
    return {"Authorization": f"Bearer {session.session_id}"}


def test_remove_item_leaves_other_items_and_recalculates_totals(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    active_dishes = [m for m in menu_items if m.get("active", True) and m.get("available", True)]
    first_dish = active_dishes[0]
    second_dish = next(
        m for m in active_dishes
        if m["restaurant_id"] == first_dish["restaurant_id"] and m["id"] != first_dish["id"]
    )

    cart_repository.save(
        Cart(
            id="C-seed",
            customer_id=customer["id"],
            restaurant_id=first_dish["restaurant_id"],
            items=[
                CartLine(menu_item_id=first_dish["id"], quantity=3),
                CartLine(menu_item_id=second_dish["id"], quantity=2),
            ],
        )
    )

    res = client.delete(f"/cart/items/{first_dish['id']}", headers=headers)
    assert res.status_code == 200
    body = res.json()

    assert len(body["items"]) == 1
    assert body["items"][0]["menu_item_id"] == second_dish["id"]
    assert body["items"][0]["quantity"] == 2

    expected_subtotal = Decimal(str(second_dish["price"])) * 2
    assert Decimal(str(body["subtotal"])) == expected_subtotal
    assert Decimal(str(body["total"])) == expected_subtotal + Decimal(str(body["delivery_fee"]))


def test_remove_last_item_returns_empty_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    dish = next(m for m in menu_items if m.get("active", True) and m.get("available", True))

    cart_repository.save(
        Cart(
            id="C-seed",
            customer_id=customer["id"],
            restaurant_id=dish["restaurant_id"],
            items=[CartLine(menu_item_id=dish["id"], quantity=2)],
        )
    )

    res = client.delete(f"/cart/items/{dish['id']}", headers=headers)
    assert res.status_code == 200
    body = res.json()

    assert body["items"] == []
    assert body["restaurant_id"] is None
    assert Decimal(str(body["subtotal"])) == Decimal("0")
    assert Decimal(str(body["delivery_fee"])) == Decimal("0")
    assert Decimal(str(body["total"])) == Decimal("0")


def test_remove_item_not_in_cart_returns_404_and_preserves_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    active_dishes = [m for m in menu_items if m.get("active", True) and m.get("available", True)]
    in_cart_dish = active_dishes[0]
    not_in_cart_dish = active_dishes[1]

    # When customer has no cart yet
    res_no_cart = client.delete(f"/cart/items/{not_in_cart_dish['id']}", headers=headers)
    assert res_no_cart.status_code == 404

    # When customer has a cart without that item
    cart_repository.save(
        Cart(
            id="C-seed",
            customer_id=customer["id"],
            restaurant_id=in_cart_dish["restaurant_id"],
            items=[CartLine(menu_item_id=in_cart_dish["id"], quantity=2)],
        )
    )

    res_missing = client.delete(f"/cart/items/{not_in_cart_dish['id']}", headers=headers)
    assert res_missing.status_code == 404

    unchanged = cart_repository.get_by_customer(customer["id"])
    assert unchanged is not None
    assert len(unchanged.items) == 1
    assert unchanged.items[0].menu_item_id == in_cart_dish["id"]
    assert unchanged.items[0].quantity == 2


def test_remove_item_requires_active_customer(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    dish = next(m for m in menu_items if m.get("active", True) and m.get("available", True))

    # Unauthenticated
    unauth = client.delete(f"/cart/items/{dish['id']}")
    assert unauth.status_code == 401

    # Non-customer role
    owner = next(u for u in users if u["role"] == "restaurant_owner" and u.get("is_active", True))
    wrong_role = client.delete(
        f"/cart/items/{dish['id']}",
        headers=_auth_headers(owner["id"]),
    )
    assert wrong_role.status_code == 403

    # Deactivated customer
    inactive_customers = [u for u in users if u["role"] == "customer" and not u.get("is_active", True)]
    if inactive_customers:
        deactivated = client.delete(
            f"/cart/items/{dish['id']}",
            headers=_auth_headers(inactive_customers[0]["id"]),
        )
        assert deactivated.status_code == 403