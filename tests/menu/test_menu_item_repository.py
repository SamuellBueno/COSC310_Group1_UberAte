import pytest

from app.repositories import json_storage, menu_item_repository
from app.core.errors import DataStoreError
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


def test_update_can_deactivate_item_without_deleting(isolated_data):
    updated = menu_item_repository.update("M1", {"active": False, "available": False})
    assert updated is not None
    assert updated.active is False
    assert updated.available is False

    reloaded = menu_item_repository.get_by_id("M1")
    assert reloaded is not None
    assert reloaded.active is False
    assert reloaded.available is False

    assert menu_item_repository.update("NONEXISTENT_ID", {"active": False}) is None


def test_corrupted_data_raises_datastore_error(isolated_data):
    json_storage.write_list("menu_items.json", [{"id": "M99", "name": "Broken"}])
    with pytest.raises(DataStoreError):
        menu_item_repository.list_all()