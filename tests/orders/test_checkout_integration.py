import json
from app.repositories import menu_item_repository

def sign_in(client):
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    return {"Authorization": f"Bearer {login.json()['session_id']}"}

def change_price(isolated_data, item_id, price):
    path = isolated_data / "menu_items.json"
    menu = json.loads(path.read_text(encoding="utf-8"))
    for m in menu:
        if m["id"] == item_id:
            m["price"] = price
    path.write_text(json.dumps(menu), encoding="utf-8")

def test_customer_to_order_workflow(client):
    headers = sign_in(client)
    item = next(i for i in menu_item_repository.list_all() if i.active and i.available)

    client.post("/cart/items", json={"menu_item_id": item.id, "quantity": 2}, headers=headers)
    cart = client.get("/cart", headers=headers).json()

    checkout = client.post("/checkout", json={"expected_total": cart["total"]}, headers=headers)
    assert checkout.status_code == 201

    order = client.get(f"/orders/{checkout.json()['id']}", headers=headers).json()
    assert order["total"] == cart["total"]
    assert order["items"][0]["quantity"] == 2
    assert client.get("/cart", headers=headers).json()["items"] == []

def test_menu_price_change_does_not_change_placed_order(client, isolated_data):
    headers = sign_in(client)
    item = next(i for i in menu_item_repository.list_all() if i.active and i.available)

    client.post("/cart/items", json={"menu_item_id": item.id, "quantity": 1}, headers=headers)
    total = client.get("/cart", headers=headers).json()["total"]
    order_id = client.post("/checkout", json={"expected_total": total}, headers=headers).json()["id"]

    change_price(isolated_data, item.id, 99.0)

    order = client.get(f"/orders/{order_id}", headers=headers).json()
    assert order["items"][0]["unit_price"] == item.price
    assert order["total"] == total