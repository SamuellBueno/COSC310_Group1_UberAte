import json
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

def test_menu_is_sorted_by_category_then_name(isolated_data):
    items = [
        {"id": "M1", "restaurant_id": "A1", "name": "Zebra Roll", "description": "",
         "category": "Rolls", "price": 12.0, "available": True, "active": True},
        {"id": "M2", "restaurant_id": "A1", "name": "Miso Soup", "description": "",
         "category": "Appetizers", "price": 4.0, "available": True, "active": True},
        {"id": "M3", "restaurant_id": "A1", "name": "Alpha Roll", "description": "",
         "category": "Rolls", "price": 10.0, "available": True, "active": True},
    ]
    (isolated_data / "menu_items.json").write_text(json.dumps(items), encoding="utf-8")

    response = client.get("/restaurants/A1/menu-items")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["M2", "M3", "M1"]


def test_deactivated_items_are_excluded_from_restaurant_menu(isolated_data):
    items = [
        {"id": "M1", "restaurant_id": "A1", "name": "Active Dish", "description": "",
         "category": "Mains", "price": 12.0, "available": True, "active": True},
        {"id": "M2", "restaurant_id": "A1", "name": "Retired Dish", "description": "",
         "category": "Mains", "price": 10.0, "available": False, "active": False},
    ]
    (isolated_data / "menu_items.json").write_text(json.dumps(items), encoding="utf-8")

    response = client.get("/restaurants/A1/menu-items")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["M1"]


def test_get_single_menu_item_returns_200_and_404(isolated_data):
    ok_response = client.get("/menu-items/M1")
    assert ok_response.status_code == 200
    assert ok_response.json()["id"] == "M1"

    missing_response = client.get("/menu-items/M999")
    assert missing_response.status_code == 404