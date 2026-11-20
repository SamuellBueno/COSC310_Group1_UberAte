import json
import pytest
from app.core.errors import NotFoundError
from app.repositories import menu_item_repository, user_repository, session_repository
from app.services import menu_service

RESTAURANTS = [
    {"id": "A1", "name": "Test Sushi", "cuisine": "Sushi", "rating": 4.0,
     "address": "1 Test St", "is_open": True, "owner_id": "U2"},
    {"id": "A2", "name": "Test Donair", "cuisine": "Donair", "rating": 4.0,
     "address": "2 Test St", "is_open": True, "owner_id": "U2"},
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

def test_update_changes_only_the_fields_sent(client, owner_headers):
    # Criterion: an owner can change one field without reentering the rest
    # and a dish marked unavailable shows as unavailable
    response = client.patch("/menu-items/M1", headers=owner_headers, json={"available": False})
    assert response.status_code == 200
    assert response.json()["available"] is False
    assert response.json()["name"] == "Dragon Roll"
    assert response.json()["price"] == 14.0


def test_update_is_saved_to_the_file(client, owner_headers):
    # Criterion: changes are saved and still there later
    response = client.patch("/menu-items/M1", headers=owner_headers, json={"price": 15.5})

    assert response.status_code == 200, response.text
    assert menu_item_repository.get_by_id("M1").price == 15.5


def test_cannot_move_dish_to_another_restaurant(client, owner_headers):
    response = client.patch("/menu-items/M1", headers=owner_headers, json={"restaurant_id": "A2"},)

    assert response.status_code == 422, response.text


def test_rename_to_name_already_on_same_menu_returns_409(client, owner_headers):
    response = client.patch("/menu-items/M2", headers=owner_headers, json={"name": "dragon roll"},)

    assert response.status_code == 409, response.text


def test_unknown_dish_returns_404(client, owner_headers):
    response = client.patch("/menu-items/M999", headers=owner_headers, json={"price": 5.0},)

    assert response.status_code == 404, response.text


def test_empty_update_returns_400(client, owner_headers):
    response = client.patch("/menu-items/M1", headers=owner_headers, json={})

    assert response.status_code == 400, response.text

def test_deactivate_returns_200_and_marks_inactive_and_unavailable(client, owner_headers):
    response = client.post("/menu-items/M1/deactivate", headers=owner_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == "M1"
    assert body["active"] is False
    assert body["available"] is False


def test_deactivated_dish_stays_in_the_file(client, owner_headers):
    response = client.post("/menu-items/M1/deactivate", headers=owner_headers)
    assert response.status_code == 200, response.text

    saved = menu_item_repository.get_by_id("M1")
    assert saved is not None
    assert saved.active is False
    assert saved.available is False

def test_deactivated_dish_is_hidden_from_restaurant_menu_but_still_readable_by_id(client, owner_headers):
    response = client.post("/menu-items/M1/deactivate", headers=owner_headers)
    assert response.status_code == 200, response.text

    menu_response = client.get("/restaurants/A1/menu-items")
    assert menu_response.status_code == 200
    assert [item["id"] for item in menu_response.json()] == ["M2"]

    single_response = client.get("/menu-items/M1")
    assert single_response.status_code == 200
    assert single_response.json()["active"] is False


def test_delete_endpoint_is_removed(client):
    response = client.delete("/menu-items/M1")
    assert response.status_code == 405


def test_deactivate_unknown_dish_returns_404(client, owner_headers):
    response = client.post("/menu-items/M999/deactivate", headers=owner_headers)

    assert response.status_code == 404, response.text

def test_deactivate_unknown_dish_raises_not_found():
    owner = user_repository.get_by_id("U2")
    assert owner is not None

    with pytest.raises(NotFoundError):
        menu_service.deactivate_menu_item("M999", actor=owner)

def test_other_owner_cannot_update_menu_item(client):
    before = menu_item_repository.get_by_id("M1")
    assert before is not None

    session = session_repository.add("U3")
    headers = {"Authorization": f"Bearer {session.session_id}"}

    response = client.patch(
        "/menu-items/M1",
        headers=headers,
        json={"price": 15.5},
    )

    assert response.status_code == 403, response.text
    assert menu_item_repository.get_by_id("M1") == before

def test_other_owner_cannot_deactivate_menu_item(client):
    before = menu_item_repository.get_by_id("M1")
    assert before is not None

    session = session_repository.add("U3")
    headers = {"Authorization": f"Bearer {session.session_id}"}

    response = client.post("/menu-items/M1/deactivate", headers=headers)

    assert response.status_code == 403, response.text
    assert menu_item_repository.get_by_id("M1") == before

def test_admin_can_update_menu_item(client):
    session = session_repository.add("U1")
    headers = {"Authorization": f"Bearer {session.session_id}"}

    response = client.patch(
        "/menu-items/M1",
        headers=headers,
        json={"price": 15.5},
    )

    assert response.status_code == 200, response.text
    saved = menu_item_repository.get_by_id("M1")
    assert saved is not None
    assert saved.price == 15.5