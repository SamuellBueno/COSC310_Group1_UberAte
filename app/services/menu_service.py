from app.repositories import menu_item_repository, restaurant_repository
from app.core.errors import BusinessRuleError, ConflictError, NotFoundError
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.schemas.user import User
from app.services.access import ensure_can_manage


def get_menu_items_for_restaurant(restaurant_id: str) -> list[MenuItem]:
    # Check if the restaurant exists first
    restaurant = restaurant_repository.get_by_id(restaurant_id)
    if restaurant is None:
        raise NotFoundError("Restaurant not found")
    
    # Returns the list of active items (or an empty list if the restaurant has none)
    items = menu_item_repository.list_by_restaurant(restaurant_id)
    active_items = [item for item in items if item.active]
    return sorted(active_items, key=lambda item: (item.category.lower(), item.name.lower()))

def get_menu_item(item_id: str) -> MenuItem:
    item = menu_item_repository.get_by_id(item_id)
    if item is None:
        raise NotFoundError(f"Menu item not found")
    return item

def add_menu_item(restaurant_id: str, payload: MenuItemCreate, actor: User) -> MenuItem:
    #Add a dish to a restaurant's menu
    restaurant = restaurant_repository.get_by_id(restaurant_id)
    if restaurant is None:
        raise NotFoundError("Restaurant not found")

    ensure_can_manage(actor, restaurant)

    for item in menu_item_repository.list_by_restaurant(restaurant_id):
        if item.name.lower() == payload.name.lower():
            raise ConflictError(f"This menu already has a dish named '{payload.name}'")

    return menu_item_repository.add(restaurant_id, payload)

def update_menu_item(item_id: str, payload: MenuItemUpdate, actor: User) -> MenuItem:
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)

    if not changes:
        raise BusinessRuleError("Send at least one field to update")

    item = menu_item_repository.get_by_id(item_id)
    if item is None:
        raise NotFoundError("Menu item not found")

    restaurant = restaurant_repository.get_by_id(item.restaurant_id)
    if restaurant is None:
        raise NotFoundError("Restaurant not found")

    ensure_can_manage(actor, restaurant)

    if "name" in changes:
        for other in menu_item_repository.list_by_restaurant(item.restaurant_id):
            if other.id != item_id and other.name.lower() == changes["name"].lower():
                raise ConflictError(f"This menu already has a dish named '{changes['name']}'")

    return menu_item_repository.update(item_id, changes)

""""
def delete_menu_item(item_id: str) -> None:
    if not menu_item_repository.delete(item_id):
        raise NotFoundError("Menu item not found")
"""

def deactivate_menu_item(item_id: str, actor: User) -> MenuItem:
    item = menu_item_repository.get_by_id(item_id)
    if item is None:
        raise NotFoundError(f"Menu item {item_id} not found")

    restaurant = restaurant_repository.get_by_id(item.restaurant_id)
    if restaurant is None:
        raise NotFoundError("Restaurant not found")

    ensure_can_manage(actor, restaurant)
    
    updated = menu_item_repository.update(item_id, {"active": False, "available": False})
    if updated is None:
        raise NotFoundError(f"Menu item {item_id} not found")
    return updated

