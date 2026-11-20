import pytest
from app.repositories.restaurant_repository import load_restaurants
from app.repositories import session_repository

@pytest.fixture
def owner_headers():
    session = session_repository.add("U2")
    return {"Authorization": f"Bearer {session.session_id}"}

def test_restaurant_routes_status(client):
    response = client.get("/restaurants")

    assert response.status_code == 200

def test_restaurant_routes_returns_list(client):
    response = client.get("/restaurants")
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_restaurant_route_incorrect_id(client):
    response = client.get("/restaurants/TEST1")

    assert response.status_code == 404

def test_restaurant_route_get_correct_id(client, owner_headers):
    created = client.post("/restaurants", headers=owner_headers, json={
        "name": "Test Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    })
    assert created.status_code == 201
    test = created.json()

    response = client.get(f"/restaurants/{test['id']}")

    assert response.status_code == 200
    assert response.json() == test

def test_get_restaurant_filter_cuisine(client, owner_headers):
    created = client.post("/restaurants", headers=owner_headers, json={
        "name": "Test Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    })
    assert created.status_code == 201, created.text
    test = created.json()

def test_get_restaurant_search(client, owner_headers):
    created = client.post("/restaurants", headers=owner_headers, json={
        "name": "Test Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    })
    assert created.status_code == 201, created.text
    test = created.json()

def test_get_restaurants_open(client, owner_headers):
    open_response = client.post("/restaurants", headers=owner_headers, json={
        "name": "Test Open Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    })
    assert open_response.status_code == 201, open_response.text

    closed_response = client.post("/restaurants", headers=owner_headers, json={
        "name": "Test Closed Pizza Place",
        "cuisine": "Pizza",
        "address": "321 Address",
        "is_open": False,
    })
    assert closed_response.status_code == 201, closed_response.text

    response = client.get("/restaurants", params={"open": "true"})
    assert response.status_code == 200, response.text

    restaurants = response.json()
    ids = [restaurant["id"] for restaurant in restaurants]
    assert open_response.json()["id"] in ids
    assert closed_response.json()["id"] not in ids
    assert all(restaurant["is_open"] for restaurant in restaurants)

def test_get_restaurants_all_filters(client, owner_headers):
    created = client.post("/restaurants", headers=owner_headers, json={
        "name": "Test All Pizza",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    })
    assert created.status_code == 201, created.text
    test = created.json()

    response = client.get("/restaurants", params={
        "cuisine": "pizza",
        "search": "Test all",
        "open": "true",
    })
    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [test["id"]]

    response = client.get("/restaurants", params={
        "cuisine": "sushi",
        "search": "Test All",
        "open": "true",
    })
    assert response.status_code == 200
    assert response.json() == []

def test_post_restaurant_route_returns_201(client, owner_headers):
    response = client.post("/restaurants", headers=owner_headers, json={
            "name": "DonaldMac",
            "cuisine": "burger",
            "address": "123street",
            "is_open": True,
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["owner_id"] == "U2"

def test_post_duplicate_restaurant_is_rejected(client, owner_headers):
    restaurant = {
        "name": "DonaldMac",
        "cuisine": "burger",
        "address": "123street",
        "is_open": True,
    }

    first = client.post("/restaurants", headers=owner_headers, json=restaurant)
    assert first.status_code == 201, first.text

    second = client.post("/restaurants", headers=owner_headers, json=restaurant)
    assert second.status_code == 409, second.text

def test_post_restaurant_with_id_is_rejected(client, owner_headers):
    response = client.post(
        "/restaurants",
        headers=owner_headers,
        json={
            "id": "A1",
            "name": "DonaldMac",
            "cuisine": "burger",
            "address": "123street",
            "is_open": True,
        },
    )

    assert response.status_code == 422, response.text

def test_patch_restaurant_route_returns_200(client, owner_headers):
    response = client.patch("/restaurants/A1", headers=owner_headers,json={"name": "Test Updated Name"},)

    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Test Updated Name"

def test_patch_unknown_restaurant_returns_404(client, owner_headers):
    response = client.patch("/restaurants/notrealid", headers=owner_headers, json={"name": "Test Name"},)

    assert response.status_code == 404, response.text

def test_patch_duplicate_name_is_rejected(client, owner_headers):
    restaurants = load_restaurants()
    existing_name = next(r.name for r in restaurants if r.id == "A2")

    response = client.patch("/restaurants/A1", headers=owner_headers, json={"name": existing_name},)

    assert response.status_code == 409, response.text

def test_patch_restaurant_with_id_is_rejected(client, owner_headers):
    response = client.patch("/restaurants/A1", headers=owner_headers, json={"id": "A1000"},)

    assert response.status_code == 422, response.text

def test_patch_with_nothing_to_change_returns_400(client, owner_headers):
    response = client.patch("/restaurants/A1", headers=owner_headers, json={},)

    assert response.status_code == 400, response.text

def test_owner_cannot_patch_someone_elses_restaurant(client):
    before = client.get("/restaurants/A1")
    assert before.status_code == 200, before.text

    session = session_repository.add("U3")
    headers = {"Authorization": f"Bearer {session.session_id}"}

    response = client.patch(
        "/restaurants/A1",
        headers=headers,
        json={"name": "Unauthorized Name"},
    )

    assert response.status_code == 403, response.text

    after = client.get("/restaurants/A1")
    assert after.status_code == 200, after.text
    assert after.json() == before.json()

def test_post_restaurant_without_signing_in_returns_401(client):
    response = client.post("/restaurants", json={
        "name": "Test Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    })

    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Sign in first"

def test_customer_cannot_create_restaurant(client):
    before = load_restaurants()
    session = session_repository.add("U4")
    headers = {"Authorization": f"Bearer {session.session_id}"}

    response = client.post(
        "/restaurants",
        headers=headers,
        json={
            "name": "Test Pizza Place",
            "cuisine": "Pizza",
            "address": "123 Address",
            "is_open": True,
        },
    )

    assert response.status_code == 403, response.text
    assert load_restaurants() == before