from app.repositories import json_storage
from app.schemas.menu_item import MenuItem, MenuItemCreate

FILENAME = "menu_items.json"


def list_all() -> list[MenuItem]:
    """Return every menu item in the data file."""
    # Each record is a dict like {"id": "M1", "name": "Dragon Roll", ...}.
    # model_validate checks the dict against the MenuItem rules and turns it into a MenuItem object.
    return [MenuItem.model_validate(record) for record in json_storage.read_list(FILENAME)]


def add(restaurant_id: str, payload: MenuItemCreate) -> MenuItem:
    """Give the new item the next id, save it, and return it."""
    records = json_storage.read_list(FILENAME)
    new_item = MenuItem(
        id=json_storage.next_id(records, "M"),   # the server picks the id
        restaurant_id=restaurant_id,           # comes from the URL
        name=payload.name,                     
        description=payload.description,
        category=payload.category,
        price=payload.price,
        available=payload.available,
    )
    records.append(new_item.model_dump())     
    json_storage.write_list(FILENAME, records)
    return new_item

def list_by_restaurant(restaurant_id: str) -> list[MenuItem]:
    """Return only the menu items that belong to one restaurant"""
    items = []
    for item in list_all():
        if item.restaurant_id == restaurant_id:
            items.append(item)
    return items

def get_by_id(item_id: str) -> MenuItem | None:
    """Return the menu item with this id or none"""
    for item in list_all():
        if item.id == item_id:
            return item
    return None

def update(item_id: str, changes: dict) -> MenuItem | None:
    """Apply the changes to one menu item and return it"""
    records = json_storage.read_list(FILENAME)
    for index, record in enumerate(records):
        if record["id"] == item_id:
            updated_record = dict(record)
            updated_record.update(changes)
            updated_item = MenuItem.model_validate(updated_record)
            records[index] = updated_item.model_dump()
            json_storage.write_list(FILENAME, records)
            return updated_item
    return None

def delete(item_id: str) -> bool:
    """Remove the menu item with this id returns True if it was deleted and False if it didn't exist"""
    records = json_storage.read_list(FILENAME)
    for index, record in enumerate(records):
        if record["id"] == item_id:
            records.pop(index)
            json_storage.write_list(FILENAME, records)
            return True
    return False