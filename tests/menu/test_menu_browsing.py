from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_menu_for_valid_restaurant(isolated_data):
    response = client.get("/restaurants/A1/menu-items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(item["restaurant_id"] == "A1" for item in data)


def test_get_menu_for_empty_restaurant(isolated_data):
    response = client.get("/restaurants/A6/menu-items")
    assert response.status_code == 200
    assert response.json() == []


def test_get_menu_for_nonexistent_restaurant(isolated_data):
    response = client.get("/restaurants/NONEXISTENT_ID/menu-items")
    assert response.status_code == 404