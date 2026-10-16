from app.repositories.restaurant_repository import load_restaurants


def test_restaurant_routes_status(client):
    response = client.get("/restaurants")

    assert response.status_code == 200

def test_restaurant_routes_returns_list(client):
    response = client.get("/restaurants")
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2

def test_restaurant_route_wrong_path(client):
    response = client.get("/wrongpath")

    assert response.status_code == 404

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


