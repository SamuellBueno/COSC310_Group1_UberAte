def test_restaurant_routes_status(client):
    response = client.get("/restaurants")

    assert response.status_code == 200

def test_restaurant_routes_returns_list(client):
    response = client.get("/restaurants")
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2

def test_restaurant_route_wrong_path(client):
    response = client.get("/restaurants/wrongpath")

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