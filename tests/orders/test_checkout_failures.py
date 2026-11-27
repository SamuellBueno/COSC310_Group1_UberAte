# what happens when saving the order fails in the middle of checkout
from app.core.errors import DataStoreError
from app.repositories import json_storage


def sign_in(client):
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    return {"Authorization": f"Bearer {login.json()['session_id']}"}


def fill_cart(client, headers):
    # Dragon Roll 14.00 x2 + 3.99 delivery = 31.99, returns the total the customer saw
    cart = client.post("/cart/items", json={"menu_item_id": "M1", "quantity": 2}, headers=headers).json()
    return cart["total"]


def make_orders_file_fail(monkeypatch):
    # a fake write_list: saving orders.json fails like a full disk would, every other file saves normally
    real_write = json_storage.write_list

    def write_that_fails(filename, records):
        if filename == "orders.json":
            raise DataStoreError("Could not save orders.json")
        real_write(filename, records)

    monkeypatch.setattr(json_storage, "write_list", write_that_fails)


def test_orders_file_fails_returns_500(client, monkeypatch):
    # the customer gets the safe error, not a stack trace
    alex = sign_in(client)
    total = fill_cart(client, alex)
    make_orders_file_fail(monkeypatch)
    response = client.post("/checkout", json={"expected_total": total}, headers=alex)
    assert response.status_code == 500
    assert response.json() == {"detail": "Data storage error"}


def test_orders_file_fails_keeps_the_cart(client, monkeypatch):
    # no order was made, so the customer must not lose their cart
    alex = sign_in(client)
    total = fill_cart(client, alex)
    make_orders_file_fail(monkeypatch)
    client.post("/checkout", json={"expected_total": total}, headers=alex)
    assert len(client.get("/cart", headers=alex).json()["items"]) == 1


def test_orders_file_fails_creates_no_order(client, monkeypatch):
    # nothing half made is counted as an order
    alex = sign_in(client)
    total = fill_cart(client, alex)
    make_orders_file_fail(monkeypatch)
    client.post("/checkout", json={"expected_total": total}, headers=alex)
    assert client.get("/orders", headers=alex).json() == []