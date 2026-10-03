from app.repositories import json_store
from app.schemas.menu_item import MenuItem, MenuItemCreate

FILENAME = "menu_items.json"


def list_all() -> list[MenuItem]:
    """Return every menu item in the data file."""
    # Each record is a dict like {"id": "M1", "name": "Dragon Roll", ...}.
    # model_validate checks the dict against the MenuItem rules and turns it into a MenuItem object.
    return [MenuItem.model_validate(record) for record in json_store.read_list(FILENAME)]


def add(restaurant_id: str, payload: MenuItemCreate) -> MenuItem:
    """Give the new item the next id, save it, and return it."""
    records = json_store.read_list(FILENAME)
    new_item = MenuItem(
        id=json_store.next_id(records, "M"),   # the server picks the id
        restaurant_id=restaurant_id,           # comes from the URL
        name=payload.name,                     
        description=payload.description,
        category=payload.category,
        price=payload.price,
        available=payload.available,
    )
    records.append(new_item.model_dump())     
    json_store.write_list(FILENAME, records)
    return new_item

def list_by_restaurant(restaurant_id: str) -> list[MenuItem]:
    """Return only the menu items that belong to one restaurant."""
    items = []
    for item in list_all():
        if item.restaurant_id == restaurant_id:
            items.append(item)
    return items