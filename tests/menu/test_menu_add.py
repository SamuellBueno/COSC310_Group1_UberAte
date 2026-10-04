from app.repositories import menu_item_repository

# A valid dish used by several tests it is not in the data base as of 2026-10-03
NEW_DISH = {"name": "Salmon Nigiri", "category": "Nigiri", "price": 6.5}


def test_add_menu_item_returns_201_with_new_id(client):
    # Criterion: an owner can add a dish, and the server picks its id
    ids_before = [item.id for item in menu_item_repository.list_all()]
    response = client.post("/restaurants/A1/menu-items", json=NEW_DISH)
    assert response.status_code == 201
    assert response.json()["id"] not in ids_before
    assert response.json()["restaurant_id"] == "A1"


def test_added_item_is_saved_to_the_file(client):
    # Criterion: a new dish is still there later 
    client.post("/restaurants/A1/menu-items", json=NEW_DISH)
    assert menu_item_repository.list_all()[-1].name == "Salmon Nigiri"


def test_unknown_restaurant_returns_404(client):
    # Criterion: a dish can't be added to a restaurant that doesn't exist
    response = client.post("/restaurants/A999/menu-items", json=NEW_DISH)
    assert response.status_code == 404


def test_duplicate_name_on_same_menu_returns_400(client):
    # Criterion: one menu can't have two dishes with the same name
    dish = {"name": "dragon roll", "category": "Rolls", "price": 14.0}
    response = client.post("/restaurants/A1/menu-items", json=dish)
    assert response.status_code == 400


def test_same_name_on_another_restaurant_is_allowed(client):
    # Criterion: different restaurants should be able to use the same dish name
    dish = {"name": "Dragon Roll", "category": "Rolls", "price": 14.0}
    response = client.post("/restaurants/A2/menu-items", json=dish)
    assert response.status_code == 201


def test_negative_price_returns_422(client):
    # Criterion: a negative price is refused.
    dish = {"name": "Salmon Nigiri", "category": "Nigiri", "price": -1}
    response = client.post("/restaurants/A1/menu-items", json=dish)
    assert response.status_code == 422


def test_missing_name_returns_422(client):
    # Criterion: a dish with no name is refused
    dish = {"category": "Rolls", "price": 5.0}
    response = client.post("/restaurants/A1/menu-items", json=dish)
    assert response.status_code == 422


def test_restaurant_id_in_body_returns_422(client):
    # Design check: the restaurant may only come from the URL
    dish = {"name": "Salmon Nigiri", "category": "Nigiri", "price": 6.5, "restaurant_id": "A2"}
    response = client.post("/restaurants/A1/menu-items", json=dish)
    assert response.status_code == 422