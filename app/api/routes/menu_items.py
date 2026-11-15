from fastapi import APIRouter

from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.services import menu_service

router = APIRouter(tags=["menu"])

@router.post(
    "/restaurants/{restaurant_id}/menu-items",
    response_model=MenuItem,
    status_code=201,
    summary="Add a menu item",
    description="Adds a menu it to a restaurant's menu and the id comes from the server",
    responses={
    404: {"description": "Restaurant not found"},
    409: {"description": "This menu already has a dish with that name"},
    201: {"description": "Everything went well. Item created"}
    },
)
def add_menu_item(restaurant_id: str, payload: MenuItemCreate):
    return menu_service.add_menu_item(restaurant_id, payload)

@router.patch(
    "/menu-items/{item_id}",
    response_model=MenuItem,
    summary="Update a menu item",
    description="Changes only the fields that are sent the empty ones are not accounted for "
                "A dish can't be moved to another restaurant.",
    responses={
        200: {"description": "Item updated"},
        400: {"description": "Nothing to update"},
        404: {"description": "Item not found"},
        409: {"description": "This menu already has an item with that name"},
    },
)
def update_menu_item(item_id: str, payload: MenuItemUpdate):
    return menu_service.update_menu_item(item_id, payload)

@router.delete(
    "/menu-items/{item_id}",
    status_code=204,
    summary="Delete a menu item",
    responses={404: {"description": "Item not found"}},
)
def delete_menu_item(item_id: str):
    menu_service.delete_menu_item(item_id)