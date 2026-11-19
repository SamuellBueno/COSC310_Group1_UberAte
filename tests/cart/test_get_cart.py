import json

from app.repositories import cart_repository, session_repository
from app.schemas.cart import Cart, CartLine


def _auth_headers(user_id: str) -> dict[str, str]:
    session = session_repository.add(user_id)
    return {"Authorization": f"Bearer {session.session_id}"}


def test_unauthenticated_user_cannot_get_cart(client):
    response = client.get("/cart")
    assert response.status_code == 401


def test_non_customer_cannot_get_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    manager = next(u for u in users if u["role"] != "customer")

    response = client.get("/cart", headers=_auth_headers(manager["id"]))
    assert response.status_code == 403


def test_deactivated_customer_cannot_get_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    # Deactivate account in storage after signing in
    customer["is_active"] = False
    (isolated_data / "users.json").write_text(json.dumps(users), encoding="utf-8")

    response = client.get("/cart", headers=headers)
    assert response.status_code == 403


def test_customer_gets_new_empty_cart_and_refresh_returns_same_cart(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    first = client.get("/cart", headers=headers)
    assert first.status_code == 200
    body = first.json()
    assert body["customer_id"] == customer["id"]
    assert body["restaurant_id"] is None
    assert body["items"] == []
    assert body["subtotal"] == 0.0
    assert body["delivery_fee"] == 0.0
    assert body["total"] == 0.0

    # Repeatedly opening/refreshing keeps the exact same active cart
    second = client.get("/cart", headers=headers)
    assert second.status_code == 200
    assert second.json()["id"] == body["id"]
    assert len(cart_repository.list_all()) == 1


def test_customer_with_existing_cart_sees_items_and_totals(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    dish = next(m for m in menu_items if m.get("active", True))

    cart_repository.save(
        Cart(
            id="C-existing",
            customer_id=customer["id"],
            restaurant_id=dish["restaurant_id"],
            items=[CartLine(menu_item_id=dish["id"], quantity=2)],
        )
    )

    response = client.get("/cart", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "C-existing"
    assert body["restaurant_id"] == dish["restaurant_id"]
    assert len(body["items"]) == 1
    assert body["items"][0]["menu_item_id"] == dish["id"]
    assert body["items"][0]["name"] == dish["name"]
    assert body["items"][0]["quantity"] == 2
    assert body["subtotal"] == round(dish["price"] * 2, 2)
    assert body["delivery_fee"] == 3.99
    assert body["total"] == round(body["subtotal"] + 3.99, 2)