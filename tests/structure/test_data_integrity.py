import json


def _load_json(folder, filename):
    return json.loads((folder / filename).read_text(encoding="utf-8"))


def test_every_menu_item_points_to_an_existing_restaurant(isolated_data):
    # Every record in menu_items.json must reference a valid restaurant id.
    restaurants = _load_json(isolated_data, "restaurants.json")
    menu_items = _load_json(isolated_data, "menu_items.json")

    valid_restaurant_ids = {r["id"] for r in restaurants}
    assert len(valid_restaurant_ids) > 0

    for item in menu_items:
        assert item["restaurant_id"] in valid_restaurant_ids, (
            f"Menu item {item['id']} references nonexistent restaurant '{item['restaurant_id']}'"
        )


def test_menu_item_ids_are_unique(isolated_data):
    # IDs in menu_items.json must all be distinct.
    items = _load_json(isolated_data, "menu_items.json")
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids)), "Duplicate menu item IDs detected in seed data"


def test_at_least_one_restaurant_has_empty_menu(isolated_data):
    # Verify at least one restaurant has 0 menu items to allow testing empty states.
    restaurants = _load_json(isolated_data, "restaurants.json")
    menu_items = _load_json(isolated_data, "menu_items.json")

    restaurant_ids = {r["id"] for r in restaurants}
    populated_restaurant_ids = {item["restaurant_id"] for item in menu_items}

    empty_restaurants = restaurant_ids - populated_restaurant_ids
    assert len(empty_restaurants) >= 1, "Expected at least one restaurant with no menu items"