import pytest

from app.repositories import json_storage, menu_item_repository
from app.repositories.menu_item_repository import DataStoreError
from app.schemas.menu_item import MenuItem


def test_list_all_returns_models(isolated_data):
    items = menu_item_repository.list_all()
    assert len(items) > 0
    assert all(isinstance(item, MenuItem) for item in items)


def test_list_by_restaurant_matches_and_filters(isolated_data):
    items = menu_item_repository.list_by_restaurant("A1")
    assert len(items) > 0
    assert all(item.restaurant_id == "A1" for item in items)


def test_list_restaurant_returns_empty_when_no_items(isolated_data):
    items = menu_item_repository.list_by_restaurant("A6")
    assert items == []


def test_get_by_id_found_and_not_found(isolated_data):
    item = menu_item_repository.get_by_id("M1")
    assert item is not None
    assert item.id == "M1"
    missing = menu_item_repository.get_by_id("NONEXISTENT_ID")
    assert missing is None


def test_delete_existing_and_nonexistent_item(isolated_data):
    assert menu_item_repository.delete("M1") is True
    assert menu_item_repository.get_by_id("M1") is None

    assert menu_item_repository.delete("M1") is False
    assert menu_item_repository.delete("NONEXISTENT_ID") is False


def test_corrupted_data_raises_datastore_error(isolated_data):
    json_storage.write_list("menu_items.json", [{"id": "M99", "name": "Broken"}])
    with pytest.raises(DataStoreError):
        menu_item_repository.list_all()