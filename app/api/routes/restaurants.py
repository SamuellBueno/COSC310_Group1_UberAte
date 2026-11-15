from fastapi import APIRouter, Query, status
from app.services import restaurant_service, menu_service
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.schemas.menu_item import MenuItem

router = APIRouter(tags=['restaurants'])

@router.get("/restaurants", response_model=list[Restaurant], summary = "List restaurants")
def list_restaurants(cuisine: str | None = Query(default = None, description = "Filter by cuisine"),
                    search: str | None = Query(default = None, description = "Search restaurants by text in name"),
                    open : bool | None = Query(default = False, description = "Filter by open status")):
    return restaurant_service.list_restaurants(cuisine=cuisine, search=search, open=open)

@router.get("/restaurants/{restaurant_id}", response_model=Restaurant, summary = "Get restaurant details with given ID",
            responses = {404: {"description": "No restaurant exists with this ID."}})
def get_restaurant(restaurant_id: str):
    return restaurant_service.get_restaurant(restaurant_id)

@router.post("/restaurants", response_model=Restaurant, status_code=201, summary="Create a Restaurant",
             responses={409: {"description": "A restaurant with this name already exists"}})
def create_restaurant(restaurant_data: RestaurantCreate):
    return restaurant_service.create_restaurant(restaurant_data)

@router.patch(
    "/restaurants/{restaurant_id}",
    response_model=Restaurant,
    summary="Update a Restaurant",
    responses={
        400: {"description": "Nothing to update"},
        404: {"description": "Restaurant not found"},
        409: {"description": "A restaurant with this name already exists"},
    },
)
def update_restaurant(restaurant_id: str, restaurant_data: RestaurantUpdate):
    return restaurant_service.update_restaurant(restaurant_id, restaurant_data)

@router.get(
     "/restaurants/{restaurant_id}/menu-items",
     response_model=list[MenuItem],
     status_code=status.HTTP_200_OK,
     summary="List menu items for a restaurant",
     responses={404: {"description": "Restaurant not found"}},
)
def list_menu_items_for_restaurant(restaurant_id: str):
     return menu_service.get_menu_items_for_restaurant(restaurant_id)
