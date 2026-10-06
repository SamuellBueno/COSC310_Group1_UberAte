import json
import pytest
from app.repositories import menu_item_repository

RESTAURANTS = [
    {"id": "A1", "name": "Test Sushi", "cuisine": "Sushi", "rating": 4.0,
     "address": "1 Test St", "is_open": True},
    {"id": "A2", "name": "Test Donair", "cuisine": "Donair", "rating": 4.0,
     "address": "2 Test St", "is_open": True},
]
MENU_ITEMS = [
    {"id": "M1", "restaurant_id": "A1", "name": "Dragon Roll", "description": "",
     "category": "Rolls", "price": 14.0, "available": True},
    {"id": "M2", "restaurant_id": "A1", "name": "California Roll", "description": "",
     "category": "Rolls", "price": 9.5, "available": True},
]

@pytest.fixture(autouse=True)
def known_menu_data(isolated_data):
    #Overwrite the temporary data files with the data above for this file only
    (isolated_data / "restaurants.json").write_text(json.dumps(RESTAURANTS), encoding="utf-8")
    (isolated_data / "menu_items.json").write_text(json.dumps(MENU_ITEMS), encoding="utf-8")

def test_update_changes_only_the_fields_sent(client):
    # Criterion: an owner can change one field without reentering the rest
    # and a dish marked unavailable shows as unavailable
    response = client.patch("/menu-items/M1", json={"available": False})
    assert response.status_code == 200
    assert response.json()["available"] is False
    assert response.json()["name"] == "Dragon Roll"
    assert response.json()["price"] == 14.0


def test_update_is_saved_to_the_file(client):
    # Criterion: changes are saved and still there later
    client.patch("/menu-items/M1", json={"price": 15.5})
    assert menu_item_repository.get_by_id("M1").price == 15.5


def test_cannot_move_dish_to_another_restaurant(client):
    # Criterion: a dish can't be moved to another restaurant
    response = client.patch("/menu-items/M1", json={"restaurant_id": "A2"})
    assert response.status_code == 422


def test_rename_to_name_already_on_same_menu_returns_400(client):
    # Criterion: renaming a dish to a name already on the same menu is refused
    # M1 (Dragon Roll) and M2 are both on A1
    response = client.patch("/menu-items/M2", json={"name": "dragon roll"})
    assert response.status_code == 400


def test_unknown_dish_returns_404(client):
    # Criterion: updating a dish that doesn't exist should not work
    response = client.patch("/menu-items/M999", json={"price": 5.0})
    assert response.status_code == 404


def test_empty_update_returns_400(client):
    # Criterion: sending no changes gives should also not work
    response = client.patch("/menu-items/M1", json={})
    assert response.status_code == 400