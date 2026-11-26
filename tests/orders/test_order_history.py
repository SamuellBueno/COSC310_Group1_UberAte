

def sign_in(client, email):
    # sign in through the real endpoint and return the header to send on later requests
    login = client.post("/auth/login", json={"email": email, "password": "Password123!"})
    return {"Authorization": f"Bearer {login.json()['session_id']}"}


def place_order(client, headers, item_id="M1", quantity=2):
    # put an item in the cart and check out with the total the customer saw, returns the order
    cart = client.post("/cart/items", json={"menu_item_id": item_id, "quantity": quantity}, headers=headers).json()
    response = client.post("/checkout", json={"expected_total": cart["total"]}, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_order_saves_address_subtotal_and_fee(client):
    # alex lives at 1000 KLO Rd, Kelowna. Dragon Roll 14.00 x2 = 28.00, plus the 3.99 delivery fee = 31.99
    alex = sign_in(client, "alex@uberate.test")
    order = place_order(client, alex, "M1", 2)
    assert order["delivery_address"] == "1000 KLO Rd, Kelowna"
    assert order["subtotal"] == 28.0
    assert order["delivery_fee"] == 3.99
    assert order["total"] == 31.99


def test_address_change_keeps_old_order_and_new_order_uses_new_address(client):
    # the demo item: change the address, then compare the old and the new order
    alex = sign_in(client, "alex@uberate.test")
    old_order = place_order(client, alex)
    client.patch("/customers/me", json={"delivery_address": "999 New Street, Kelowna"}, headers=alex)
    new_order = place_order(client, alex)
    assert client.get(f"/orders/{old_order['id']}", headers=alex).json()["delivery_address"] == "1000 KLO Rd, Kelowna"
    assert client.get(f"/orders/{new_order['id']}", headers=alex).json()["delivery_address"] == "999 New Street, Kelowna"


def test_checkout_without_an_address_is_refused_and_cart_is_kept(client):
    # a new account has no address yet
    client.post("/auth/register", json={"email": "noaddress@example.com", "password": "Password123!", "name": "No Address"})
    headers = sign_in(client, "noaddress@example.com")
    cart = client.post("/cart/items", json={"menu_item_id": "M1", "quantity": 1}, headers=headers).json()
    response = client.post("/checkout", json={"expected_total": cart["total"]}, headers=headers)
    assert response.status_code == 400
    # nothing was saved and the cart still has the item
    assert client.get("/cart", headers=headers).json()["items"] != []


def test_deactivated_dish_still_shows_in_an_old_order(client):
    alex = sign_in(client, "alex@uberate.test")
    owner = sign_in(client, "owner.sushi@uberate.test")
    order = place_order(client, alex, "M1", 1)
    client.post("/menu-items/M1/deactivate", headers=owner)
    saved = client.get(f"/orders/{order['id']}", headers=alex).json()
    assert saved["items"][0]["name"] == "Dragon Roll"
    assert saved["items"][0]["unit_price"] == 14.0


def test_renamed_restaurant_does_not_change_an_old_order(client):
    alex = sign_in(client, "alex@uberate.test")
    owner = sign_in(client, "owner.sushi@uberate.test")
    order = place_order(client, alex)
    client.patch("/restaurants/A1", json={"name": "Renamed Sushi"}, headers=owner)
    saved = client.get(f"/orders/{order['id']}", headers=alex).json()
    assert saved["restaurant_name"] == "Kelowna Sushi"