import json
from decimal import Decimal

from app.repositories import cart_repository, session_repository
from app.schemas.cart import Cart, CartLine


def _auth_headers(user_id: str) -> dict[str, str]:
    session = session_repository.add(user_id)
    return {"Authorization": f"Bearer {session.session_id}"}


def test_clear_cart_empties_items_and_persists_across_refresh(client, isolated_data):
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
                CartLine(menu_item_id=first_dish["id"], quantity=2),
                CartLine(menu_item_id=second_dish["id"], quantity=1),
            ],
        )
    )

    res = client.delete("/cart", headers=headers)
    assert res.status_code == 200
    body = res.json()

    assert body["items"] == []
    assert body["restaurant_id"] is None
    assert Decimal(str(body["subtotal"])) == Decimal("0")
    assert Decimal(str(body["delivery_fee"])) == Decimal("0")
    assert Decimal(str(body["total"])) == Decimal("0")

    # Simulates page refresh via GET /cart
    get_res = client.get("/cart", headers=headers)
    assert get_res.status_code == 200
    refreshed = get_res.json()
    assert refreshed["items"] == []
    assert refreshed["restaurant_id"] is None
    assert Decimal(str(refreshed["subtotal"])) == Decimal("0")
    assert Decimal(str(refreshed["total"])) == Decimal("0")


def test_clear_cart_allows_adding_from_different_restaurant(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    active_dishes = [m for m in menu_items if m.get("active", True) and m.get("available", True)]
    first_dish = active_dishes[0]
    other_restaurant_dish = next(
        m for m in active_dishes if m["restaurant_id"] != first_dish["restaurant_id"]
    )

    cart_repository.save(
        Cart(
            id="C-seed",
            customer_id=customer["id"],
            restaurant_id=first_dish["restaurant_id"],
            items=[CartLine(menu_item_id=first_dish["id"], quantity=2)],
        )
    )

    clear_res = client.delete("/cart", headers=headers)
    assert clear_res.status_code == 200

    add_res = client.post(
        "/cart/items",
        json={"menu_item_id": other_restaurant_dish["id"], "quantity": 1},
        headers=headers,
    )
    assert add_res.status_code == 200
    body = add_res.json()
    assert body["restaurant_id"] == other_restaurant_dish["restaurant_id"]
    assert len(body["items"]) == 1
    assert body["items"][0]["menu_item_id"] == other_restaurant_dish["id"]


def test_clear_cart_requires_active_customer(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))

    # Unauthenticated
    unauth = client.delete("/cart")
    assert unauth.status_code == 401

    # Non-customer role
    owner = next(u for u in users if u["role"] == "restaurant_owner" and u.get("is_active", True))
    wrong_role = client.delete("/cart", headers=_auth_headers(owner["id"]))
    assert wrong_role.status_code == 403

    # Deactivated customer
    inactive_customers = [u for u in users if u["role"] == "customer" and not u.get("is_active", True)]
    if inactive_customers:
        deactivated = client.delete("/cart", headers=_auth_headers(inactive_customers[0]["id"]))
        assert deactivated.status_code == 403