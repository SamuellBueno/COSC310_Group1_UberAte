from fastapi import APIRouter, Depends

from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.services import menu_service
from app.api.role_checks import require_manager
from app.schemas.user import User

router = APIRouter(tags=["menu"])


@router.get(
    "/menu-items/{item_id}",
    response_model=MenuItem,
    summary="Get a menu item",
    description="Returns a single menu item by ID, even if it was deactivated.",
    responses={
        200: {"description": "Item found"},
        404: {"description": "Item not found"},
    },
)
def get_menu_item(item_id: str):
    return menu_service.get_menu_item(item_id)


@router.post(
    "/restaurants/{restaurant_id}/menu-items",
    response_model=MenuItem,
    status_code=201,
    summary="Add a menu item",
    description="Adds a menu item to a restaurant's menu and the id comes from the server",
    responses={
        404: {"description": "Restaurant not found"},
        409: {"description": "This menu already has a dish with that name"},
        201: {"description": "Everything went well. Item created"},
    },
)
def add_menu_item(restaurant_id: str, payload: MenuItemCreate, user: User = Depends(require_manager)):
    return menu_service.add_menu_item(restaurant_id, payload, actor=user)


@router.patch(
    "/menu-items/{item_id}",
    response_model=MenuItem,
    summary="Update a menu item",
    description="Changes only the fields that are sent; empty ones are not accounted for. "
                "A dish can't be moved to another restaurant.",
    responses={
        200: {"description": "Item updated"},
        400: {"description": "Nothing to update"},
        404: {"description": "Item not found"},
        409: {"description": "This menu already has an item with that name"},
    },
)
def update_menu_item(item_id: str, payload: MenuItemUpdate, user: User = Depends(require_manager)):
    return menu_service.update_menu_item(item_id, payload, actor=user)


@router.post(
    "/menu-items/{item_id}/deactivate",
    response_model=MenuItem,
    status_code=200,
    summary="Deactivate a menu item",
    description="Marks a menu item inactive and unavailable instead of deleting it from storage.",
    responses={
        200: {"description": "Item deactivated"},
        404: {"description": "Item not found"},
    },
)
def deactivate_menu_item(item_id: str, user: User = Depends(require_manager)):
    return menu_service.deactivate_menu_item(item_id, actor=user)