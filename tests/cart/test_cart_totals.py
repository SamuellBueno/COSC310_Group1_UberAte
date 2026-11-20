import json
from decimal import Decimal

from app.repositories import session_repository
from app.schemas.menu_item import MenuItemUpdate
from app.services import menu_service
from app.services.pricing import DELIVERY_FEE, line_total, money


def _auth_headers(user_id: str) -> dict[str, str]:
    session = session_repository.add(user_id)
    return {"Authorization": f"Bearer {session.session_id}"}


def test_cart_totals_lifecycle_and_live_menu_prices(client, isolated_data):
    users = json.loads((isolated_data / "users.json").read_text(encoding="utf-8"))
    customer = next(u for u in users if u["role"] == "customer" and u.get("is_active", True))
    headers = _auth_headers(customer["id"])

    menu_items = json.loads((isolated_data / "menu_items.json").read_text(encoding="utf-8"))
    active_dishes = [m for m in menu_items if m.get("active", True) and m.get("available", True)]
    dish_a = active_dishes[0]
    dish_b = next(
        m for m in active_dishes
        if m["restaurant_id"] == dish_a["restaurant_id"] and m["id"] != dish_a["id"]
    )

    # 1. Empty cart shows $0.00 subtotal and total
    empty_res = client.get("/cart", headers=headers)
    assert empty_res.status_code == 200
    empty_body = empty_res.json()
    assert money(empty_body["subtotal"]) == Decimal("0.00")
    assert money(empty_body["delivery_fee"]) == Decimal("0.00")
    assert money(empty_body["total"]) == Decimal("0.00")

    # 2. Adding items calculates subtotal and total (subtotal + $3.99 delivery fee)
    add_a = client.post(
        "/cart/items",
        json={"menu_item_id": dish_a["id"], "quantity": 2},
        headers=headers,
    )
    assert add_a.status_code == 200
    body_a = add_a.json()
    expected_sub_a = line_total(dish_a["price"], 2)
    assert money(body_a["subtotal"]) == expected_sub_a
    assert money(body_a["delivery_fee"]) == DELIVERY_FEE
    assert money(body_a["total"]) == money(expected_sub_a + DELIVERY_FEE)

    add_b = client.post(
        "/cart/items",
        json={"menu_item_id": dish_b["id"], "quantity": 1},
        headers=headers,
    )
    assert add_b.status_code == 200
    body_ab = add_b.json()
    expected_sub_ab = money(expected_sub_a + line_total(dish_b["price"], 1))
    assert money(body_ab["subtotal"]) == expected_sub_ab
    assert money(body_ab["total"]) == money(expected_sub_ab + DELIVERY_FEE)

    # 3. Updating quantity recalculates subtotal and total
    patch_res = client.patch(
        f"/cart/items/{dish_a['id']}",
        json={"quantity": 3},
        headers=headers,
    )
    assert patch_res.status_code == 200
    body_patched = patch_res.json()
    expected_sub_patched = money(line_total(dish_a["price"], 3) + line_total(dish_b["price"], 1))
    assert money(body_patched["subtotal"]) == expected_sub_patched
    assert money(body_patched["total"]) == money(expected_sub_patched + DELIVERY_FEE)

    # 4. Backend uses current menu prices when a dish price updates
    updated_price = Decimal("19.50")
    menu_service.update_menu_item(dish_a["id"], MenuItemUpdate(price=updated_price))

    refreshed = client.get("/cart", headers=headers)
    assert refreshed.status_code == 200
    body_refreshed = refreshed.json()
    expected_sub_new_price = money(line_total(updated_price, 3) + line_total(dish_b["price"], 1))
    assert money(body_refreshed["subtotal"]) == expected_sub_new_price
    assert money(body_refreshed["total"]) == money(expected_sub_new_price + DELIVERY_FEE)

    # 5. Removing items recalculates totals and returns $0.00 once empty
    del_a = client.delete(f"/cart/items/{dish_a['id']}", headers=headers)
    assert del_a.status_code == 200
    body_only_b = del_a.json()
    expected_sub_b = line_total(dish_b["price"], 1)
    assert money(body_only_b["subtotal"]) == expected_sub_b
    assert money(body_only_b["total"]) == money(expected_sub_b + DELIVERY_FEE)

    del_b = client.delete(f"/cart/items/{dish_b['id']}", headers=headers)
    assert del_b.status_code == 200
    body_empty_again = del_b.json()
    assert money(body_empty_again["subtotal"]) == Decimal("0.00")
    assert money(body_empty_again["delivery_fee"]) == Decimal("0.00")
    assert money(body_empty_again["total"]) == Decimal("0.00")