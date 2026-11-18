import json
import pytest
from app.core.errors import NotFoundError
from app.repositories import menu_item_repository
from app.services import menu_service

RESTAURANTS = [
    {"id": "A1", "name": "Test Sushi", "cuisine": "Sushi", "rating": 4.0,
     "address": "1 Test St", "is_open": True},
    {"id": "A2", "name": "Test Donair", "cuisine": "Donair", "rating": 4.0,
     "address": "2 Test St", "is_open": True},
]
MENU_ITEMS = [
    {"id": "M1", "restaurant_id": "A1", "name": "Dragon Roll", "description": "",
     "category": "Rolls", "price": 14.0, "available": True, "active": True},
    {"id": "M2", "restaurant_id": "A1", "name": "California Roll", "description": "",
     "category": "Rolls", "price": 9.5, "available": True, "active": True},
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


def test_rename_to_name_already_on_same_menu_returns_409(client):
    # Criterion: renaming a dish to a name already on the same menu is refused
    # M1 (Dragon Roll) and M2 are both on A1
    response = client.patch("/menu-items/M2", json={"name": "dragon roll"})
    assert response.status_code == 409


def test_unknown_dish_returns_404(client):
    # Criterion: updating a dish that doesn't exist should not work
    response = client.patch("/menu-items/M999", json={"price": 5.0})
    assert response.status_code == 404


def test_empty_update_returns_400(client):
    # Criterion: sending no changes gives should also not work
    response = client.patch("/menu-items/M1", json={})
    assert response.status_code == 400

def test_deactivate_returns_200_and_marks_inactive_and_unavailable(client):
    response = client.post("/menu-items/M1/deactivate")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "M1"
    assert body["active"] is False
    assert body["available"] is False


def test_deactivated_dish_stays_in_the_file(client):
    # Regression test: deactivating keeps the record in storage for historical orders
    client.post("/menu-items/M1/deactivate")
    saved = menu_item_repository.get_by_id("M1")
    assert saved is not None
    assert saved.active is False
    assert saved.available is False


def test_deactivated_dish_is_hidden_from_restaurant_menu_but_still_readable_by_id(client):
    client.post("/menu-items/M1/deactivate")

    menu_response = client.get("/restaurants/A1/menu-items")
    assert menu_response.status_code == 200
    ids = [item["id"] for item in menu_response.json()]
    assert ids == ["M2"]

    single_response = client.get("/menu-items/M1")
    assert single_response.status_code == 200
    assert single_response.json()["active"] is False


def test_delete_endpoint_is_removed(client):
    response = client.delete("/menu-items/M1")
    assert response.status_code == 405


def test_deactivate_unknown_dish_returns_404(client):
    response = client.post("/menu-items/M999/deactivate")
    assert response.status_code == 404


def test_deactivate_unknown_dish_raises_not_found():
    with pytest.raises(NotFoundError):
        menu_service.deactivate_menu_item("M999")