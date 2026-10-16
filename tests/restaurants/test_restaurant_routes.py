from app.repositories.restaurant_repository import load_restaurants


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

def test_restaurant_route_get_correct_id(client):
    test = client.post("/restaurants", json={
        "name": "Test Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    }).json()

    response = client.get(f"/restaurants/{test['id']}")

    assert response.status_code == 200
    assert response.json() == test

def test_get_restaurant_filter_cuisine(client):
    test = client.post("/restaurants", json={
        "name": "Test Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    }).json()

    response = client.get("/restaurants", params={"cuisine": "pizza"})
    restaurants = response.json()

    assert response.status_code == 200
    assert test["id"] in [r["id"] for r in restaurants]
    assert all(r["cuisine"].lower() == "pizza" for r in restaurants)

def test_get_restaurant_search(client):
    test = client.post("/restaurants", json={
        "name": "Test Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    }).json()

    response = client.get("/restaurants", params={"search": "PLACE"})
    restaurants = response.json()

    assert response.status_code == 200
    assert test["id"] in [r["id"] for r in restaurants]
    assert all("place" in r["name"].lower() for r in restaurants)

def test_get_restaurants_open(client):
    open = client.post("/restaurants", json={
        "name": "Test Open Pizza Place",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    }).json()

    closed = client.post("/restaurants", json={
        "name": "Test Closed Pizza Place",
        "cuisine": "Pizza",
        "address": "321 Address",
        "is_open": False,
    }).json()

    response = client.get("/restaurants", params={"open": "true"})
    restaurants = response.json()

    assert response.status_code == 200
    assert open["id"] in [r["id"] for r in restaurants]
    assert closed["id"] not in [r["id"] for r in restaurants]
    assert all(r["is_open"] for r in restaurants)

def test_get_restaurants_all_filters(client):
    test = client.post("/restaurants", json={
        "name": "Test All Pizza",
        "cuisine": "Pizza",
        "address": "123 Address",
        "is_open": True,
    }).json()

    response = client.get("/restaurants", params={
        "cuisine": "pizza",
        "search": "Test all",
        "open_only": "true",
    })

    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [test["id"]]

    response = client.get("/restaurants", params={
        "cuisine": "sushi",
        "search": "Test All",
        "open_only": "true",
    })

    assert response.status_code == 200
    assert response.json() == []

def test_post_restaurant_route_returns_201(client):
    response = client.post("/restaurants", json={"name": "DonaldMac", "cuisine": "burger", "address": "123street", "is_open": True})

    assert response.status_code == 201

def test_post_duplicate_restaurant_is_rejected(client):
    client.post("/restaurants", json={"name": "DonaldMac", "cuisine": "burger", "address": "123street", "is_open": True})

    response = client.post("/restaurants", json={"name": "DonaldMac", "cuisine": "burger", "address": "123street", "is_open": True})

    assert response.status_code == 400

def test_post_restaurant_with_id_is_rejected(client):
    response = client.post("/restaurants", json={"id": "A1", "name": "DonaldMac", "cuisine": "burger", "address": "123street", "is_open": True})

    assert response.status_code == 422

def test_patch_restaurant_route_returns_200(client):
    restaurant = load_restaurants()[1]
    response = client.patch(f"/restaurants/{restaurant.id}", json={"name": "Test Updated Name"})

    assert response.status_code == 200

def test_patch_unknown_restaurant_returns_404(client):
    response = client.patch("/restaurants/notrealid", json={"name": "Test Name"})

    assert response.status_code == 404

def test_patch_duplicate_name_is_rejected(client):
    restaurants = load_restaurants()
    response = client.patch(f"/restaurants/{restaurants[1].id}", json={"name": restaurants[0].name})

    assert response.status_code == 400

def test_patch_restaurant_with_id_is_rejected(client):
    restaurant = load_restaurants()[1]
    response = client.patch(f"/restaurants/{restaurant.id}", json={"id": "A1000"})

    assert response.status_code == 422


