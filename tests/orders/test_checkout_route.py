from app.repositories import cart_repository, menu_item_repository
from app.schemas.cart import Cart, CartLine
from app.services import pricing

def sign_in(client):
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    return {"Authorization": f"Bearer {login.json()['session_id']}"}

def put_item_in_cart(): #helper for tests
    item = next(i for i in menu_item_repository.list_all() if i.active and i.available)
    cart_repository.save(Cart(id="C-test", customer_id="U4", restaurant_id=item.restaurant_id,
                              items=[CartLine(menu_item_id=item.id, quantity=2)]))
    return float(pricing.totals([pricing.line_total(item.price, 2)])[2])

def test_checkout_creates_order(client):
    total = put_item_in_cart()
    response = client.post("/checkout", json={"expected_total": total}, headers=sign_in(client))
    assert response.status_code == 201
    assert response.json()["total"] == total

def test_checkout_signed_out_returns_401(client):
    assert client.post("/checkout", json={"expected_total": 10}).status_code == 401

def test_checkout_empty_cart_returns_400(client):
    response = client.post("/checkout", json={"expected_total": 0}, headers=sign_in(client))
    assert response.status_code == 400

def test_checkout_wrong_total_returns_409(client):
    total = put_item_in_cart()
    response = client.post("/checkout", json={"expected_total": total + 1}, headers=sign_in(client))
    assert response.status_code == 409