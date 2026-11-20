import json

from app.repositories import cart_repository, session_repository
from app.schemas.cart import Cart, CartLine


def _auth_headers(user_id: str) -> dict[str, str]:
    session = session_repository.add(user_id)
    return {"Authorization": f"Bearer {session.session_id}"}

def test_add_available_item_and_increment_existing_quantity(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    dish = next(m for m in menu_items if m.get("active", True) and m.get("available", True))

    # Add new item with positive integer quantity
    res1 = client.post(
        "/cart/items",
        json={"menu_item_id": dish["id"], "quantity": 2},
        headers=headers,
    )
    assert res1.status_code == 200
    body1 = res1.json()
    assert body1["restaurant_id"] == dish["restaurant_id"]
    assert len(body1["items"]) == 1
    assert body1["items"][0]["menu_item_id"] == dish["id"]
    assert body1["items"][0]["quantity"] == 2

    # Adding the same item again increments its quantity
    res2 = client.post(
        "/cart/items",
        json={"menu_item_id": dish["id"], "quantity": 3},
        headers=headers,
    )
    assert res2.status_code == 200
    body2 = res2.json()
    assert len(body2["items"]) == 1
    assert body2["items"][0]["quantity"] == 5


def test_add_unavailable_item_fails_and_preserves_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items_path = isolated_data / "menu_items.json"
    menu_items = json.loads(menu_items_path.read_text(encoding="utf-8"))
    active_dish = next(m for m in menu_items if m.get("active", True) and m.get("available", True))

    inactive_dish = next((m for m in menu_items if not m.get("active", True)), None)
    if inactive_dish is None:
        inactive_dish = next(m for m in menu_items if m["id"] != active_dish["id"])
        inactive_dish["active"] = False
        menu_items_path.write_text(json.dumps(menu_items), encoding="utf-8")

    cart_repository.save(
        Cart(
            id="C-seed",
            customer_id=customer["id"],
            restaurant_id=active_dish["restaurant_id"],
            items=[CartLine(menu_item_id=active_dish["id"], quantity=1)],
        )
    )

    res = client.post(
        "/cart/items",
        json={"menu_item_id": inactive_dish["id"], "quantity": 1},
        headers=headers,
    )
    assert res.status_code in (400, 422)

    unchanged = cart_repository.get_by_customer(customer["id"])
    assert unchanged is not None
    assert len(unchanged.items) == 1
    assert unchanged.items[0].menu_item_id == active_dish["id"]
    assert unchanged.items[0].quantity == 1


def test_add_invalid_quantity_fails_and_preserves_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    dish = next(m for m in menu_items if m.get("active", True) and m.get("available", True))

    for bad_qty in (0, -2, 1.5, True, 21):
        res = client.post(
            "/cart/items",
            json={"menu_item_id": dish["id"], "quantity": bad_qty},
            headers=headers,
        )
        assert res.status_code in (400,422)

    assert cart_repository.get_by_customer(customer["id"]) is None


def test_add_item_exceeding_max_quantity_fails_and_preserves_cart(client, isolated_data):
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
            items=[CartLine(menu_item_id=dish["id"], quantity=15)],
        )
    )

    res = client.post(
        "/cart/items",
        json={"menu_item_id": dish["id"], "quantity": 6},
        headers=headers,
    )
    assert res.status_code in (400, 422)

    unchanged = cart_repository.get_by_customer(customer["id"])
    assert unchanged is not None
    assert unchanged.items[0].quantity == 15


def test_add_item_from_different_restaurant_fails_and_preserves_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    active_dishes = [m for m in menu_items if m.get("active", True) and m.get("available", True)]
    first_dish = active_dishes[0]
    other_dish = next(m for m in active_dishes if m["restaurant_id"] != first_dish["restaurant_id"])

    client.post(
        "/cart/items",
        json={"menu_item_id": first_dish["id"], "quantity": 2},
        headers=headers,
    )

    res = client.post(
        "/cart/items",
        json={"menu_item_id": other_dish["id"], "quantity": 1},
        headers=headers,
    )
    assert res.status_code == 409

    unchanged = cart_repository.get_by_customer(customer["id"])
    assert unchanged is not None
    assert unchanged.restaurant_id == first_dish["restaurant_id"]
    assert len(unchanged.items) == 1
    assert unchanged.items[0].menu_item_id == first_dish["id"]
    assert unchanged.items[0].quantity == 2


def test_add_item_requires_active_customer(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    dish = next(m for m in menu_items if m.get("active", True) and m.get("available", True))

    # Unauthenticated
    unauth = client.post("/cart/items", json={"menu_item_id": dish["id"], "quantity": 1})
    assert unauth.status_code == 401

    # Non-customer role
    owner = next(u for u in users if u["role"] == "restaurant_owner" and u.get("is_active", True))
    wrong_role = client.post(
        "/cart/items",
        json={"menu_item_id": dish["id"], "quantity": 1},
        headers=_auth_headers(owner["id"]),
    )
    assert wrong_role.status_code == 403

    # Deactivated customer (if seeded in users.json)
    inactive_customers = [u for u in users if u["role"] == "customer" and not u.get("is_active", True)]
    if inactive_customers:
        deactivated = client.post(
            "/cart/items",
            json={"menu_item_id": dish["id"], "quantity": 1},
            headers=_auth_headers(inactive_customers[0]["id"]),
        )
        assert deactivated.status_code == 403