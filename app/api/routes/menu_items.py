from fastapi import APIRouter, HTTPException

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
        400: {"description": "This menu already has a dish with that name"},
        404: {"description": "Restaurant not found"},
        201: {"description": "Everything went well. Item created"}
    },
)
def add_menu_item(restaurant_id: str, payload: MenuItemCreate):
    try:
        item = menu_service.add_menu_item(restaurant_id, payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    if item is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return item

@router.patch(
    "/menu-items/{item_id}",
    response_model=MenuItem,
    summary="Update a menu item",
    description="Changes only the fields that are sent the empty ones are not accounted for "
                "A dish can't be moved to another restaurant.",
    responses={
        200: {"description": "Menu item updated"},
        400: {"description": "Nothing to update or this menu already has an item with that name"},
        404: {"description": "Menu item not found"},
    },
)
def update_menu_item(item_id: str, payload: MenuItemUpdate):
    try:
        item = menu_service.update_menu_item(item_id, payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item