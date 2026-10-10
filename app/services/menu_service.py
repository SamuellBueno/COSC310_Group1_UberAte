from app.repositories import menu_item_repository, restaurant_repository
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate


def add_menu_item(restaurant_id: str, payload: MenuItemCreate) -> MenuItem | None:
    #Add a dish to a restaurant's menu
    if restaurant_repository.get_by_id(restaurant_id) is None:
        return None

    for item in menu_item_repository.list_by_restaurant(restaurant_id):
        if item.name.lower() == payload.name.lower():
            raise ValueError(f"This menu already has a dish named '{payload.name}'")

    return menu_item_repository.add(restaurant_id, payload)

def update_menu_item(item_id: str, payload: MenuItemUpdate) -> MenuItem | None:
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)

    if not changes:
        raise ValueError("Send at least one field to update")

    item = menu_item_repository.get_by_id(item_id)
    if item is None:
        return None

    if "name" in changes:
        for other in menu_item_repository.list_by_restaurant(item.restaurant_id):
            if other.id != item_id and other.name.lower() == changes["name"].lower():
                raise ValueError(f"This menu already has a dish named '{changes['name']}'")

    return menu_item_repository.update(item_id, changes)

def delete_menu_item(item_id: str) -> bool:
    return menu_item_repository.delete(item_id)