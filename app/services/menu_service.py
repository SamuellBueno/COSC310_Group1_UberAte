from app.repositories import menu_item_repository, restaurant_repository
from app.schemas.menu_item import MenuItem, MenuItemCreate


def add_menu_item(restaurant_id: str, payload: MenuItemCreate) -> MenuItem | None:
    """Add a dish to a restaurant's menu.
    Returns None if the restaurant does not exist (the route turns that into 404).
    Raises ValueError if the menu already has a dish with this name (the route turns that into 400).
    """
    if restaurant_repository.get_by_id(restaurant_id) is None:
        return None

    for item in menu_item_repository.list_by_restaurant(restaurant_id):
        if item.name.lower() == payload.name.lower():
            raise ValueError(f"This menu already has a dish named '{payload.name}'")

    return menu_item_repository.add(restaurant_id, payload)