import json
from decimal import Decimal

from app.repositories import cart_repository, session_repository
from app.schemas.cart import Cart, CartLine


def _auth_headers(user_id: str) -> dict[str, str]:
    session = session_repository.add(user_id)
    return {"Authorization": f"Bearer {session.session_id}"}


def test_update_item_quantity_recalculates_totals(client, isolated_data):
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
            items=[CartLine(menu_item_id=dish["id"], quantity=1)],
        )
    )

    res = client.patch(
        f"/cart/items/{dish['id']}",
        json={"quantity": 4},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 4

    expected_subtotal = Decimal(str(dish["price"])) * 4
    assert Decimal(str(body["subtotal"])) == expected_subtotal
    assert Decimal(str(body["total"])) == expected_subtotal + Decimal(str(body["delivery_fee"]))


def test_update_invalid_quantity_fails_and_preserves_cart(client, isolated_data):
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

    for bad_qty in (0, -3, 1.5, True, 21):
        res = client.patch(
            f"/cart/items/{dish['id']}",
            json={"quantity": bad_qty},
            headers=headers,
        )
        assert res.status_code in (400, 422)

    unchanged = cart_repository.get_by_customer(customer["id"])
    assert unchanged is not None
    assert unchanged.items[0].quantity == 2


def test_update_item_not_in_cart_returns_404_and_preserves_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    active_dishes = [m for m in menu_items if m.get("active", True) and m.get("available", True)]
    in_cart_dish = active_dishes[0]
    not_in_cart_dish = active_dishes[1]

    # Customer has no cart yet
    res_no_cart = client.patch(
        f"/cart/items/{not_in_cart_dish['id']}",
        json={"quantity": 2},
        headers=headers,
    )
    assert res_no_cart.status_code == 404

    # Customer has a cart without that item
    cart_repository.save(
        Cart(
            id="C-seed",
            customer_id=customer["id"],
            restaurant_id=in_cart_dish["restaurant_id"],
            items=[CartLine(menu_item_id=in_cart_dish["id"], quantity=2)],
        )
    )

    res_missing = client.patch(
        f"/cart/items/{not_in_cart_dish['id']}",
        json={"quantity": 3},
        headers=headers,
    )
    assert res_missing.status_code == 404

    unchanged = cart_repository.get_by_customer(customer["id"])
    assert unchanged is not None
    assert len(unchanged.items) == 1
    assert unchanged.items[0].menu_item_id == in_cart_dish["id"]
    assert unchanged.items[0].quantity == 2


def test_update_item_requires_active_customer(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    dish = next(m for m in menu_items if m.get("active", True) and m.get("available", True))

    # Unauthenticated
    unauth = client.patch(f"/cart/items/{dish['id']}", json={"quantity": 2})
    assert unauth.status_code == 401

    # Non-customer role
    owner = next(u for u in users if u["role"] == "restaurant_owner" and u.get("is_active", True))
    wrong_role = client.patch(
        f"/cart/items/{dish['id']}",
        json={"quantity": 2},
        headers=_auth_headers(owner["id"]),
    )
    assert wrong_role.status_code == 403

    # Deactivated customer
    inactive_customers = [u for u in users if u["role"] == "customer" and not u.get("is_active", True)]
    if inactive_customers:
        deactivated = client.patch(
            f"/cart/items/{dish['id']}",
            json={"quantity": 2},
            headers=_auth_headers(inactive_customers[0]["id"]),
        )
        assert deactivated.status_code == 403