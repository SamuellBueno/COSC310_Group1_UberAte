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

