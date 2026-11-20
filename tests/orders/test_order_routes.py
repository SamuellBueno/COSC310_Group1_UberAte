from app.repositories.order_repository import add
from app.schemas.order import OrderCreate, OrderItem
import json

ITEMS = [OrderItem(menu_item_id="M1", name="Burger", unit_price=10.0, quantity=2)]

def make_order(customer_id):
    return OrderCreate(customer_id=customer_id, restaurant_id="A1", restaurant_name="DonaldMac", items=ITEMS, total=20.0)

def sign_in(client):
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    return {"Authorization": f"Bearer {login.json()['session_id']}"}

def test_list_orders_newest_first(client):
    first = add(make_order("U4"))
    second = add(make_order("U4"))
    response = client.get("/orders", headers=sign_in(client))
    assert [o["id"] for o in response.json()] == [second.id, first.id]

def test_list_orders_hides_other_customers_orders(client):
    add(make_order("U999"))
    response = client.get("/orders", headers=sign_in(client))
    assert response.json() == []

def test_orders_signed_out_returns_401(client):
    assert client.get("/orders").status_code == 401

def test_other_customers_order_returns_403(client):
    order = add(make_order("U999"))
    assert client.get(f"/orders/{order.id}", headers=sign_in(client)).status_code == 403

def test_unknown_order_returns_404(client):
    assert client.get("/orders/O999", headers=sign_in(client)).status_code == 404

def test_saved_order_keeps_original_price(client, isolated_data):
    order = add(make_order("U4"))
    menu_path = isolated_data / "menu_items.json"
    menu = json.loads(menu_path.read_text(encoding="utf-8"))
    for item in menu:
        item["price"] = 99.0
        item["name"] = "Changed"
    menu_path.write_text(json.dumps(menu), encoding="utf-8")
    response = client.get(f"/orders/{order.id}", headers=sign_in(client))
    assert response.json()["items"][0]["name"] == "Burger"
    assert response.json()["items"][0]["unit_price"] == 10.0