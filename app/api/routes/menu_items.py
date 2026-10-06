from fastapi import APIRouter, HTTPException

from app.schemas.menu_item import MenuItem, MenuItemCreate
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