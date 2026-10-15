from fastapi import APIRouter, HTTPException, Query
from app.services import restaurant_service
from app.schemas.restaurant import Restaurant, RestaurantCreate

router = APIRouter(tags=['restaurants'])

@router.get("/restaurants", response_model=list[Restaurant], summary = "List restaurants")
def list_restaurants(cuisine: str | None = Query(default = None, description = "Filter by cuisine"),
                    search: str | None = Query(default = None, description = "Search restaurants by text in name"),
                    open : bool | None = Query(default = False, description = "Filter by open status")):
    return restaurant_service.list_restaurants(cuisine=cuisine, search=search, open=open)

@router.get("/restaurants/{restaurant_id}", response_model=Restaurant, summary = "Get restaurant details with given ID",
            responses = {404: {"description": "No restaurant exists with this ID."}})
def get_restaurant(restaurant_id: str):
    try:
        return restaurant_service.get_restaurant(restaurant_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.post("/restaurants", response_model=Restaurant, status_code=201, summary="Create a Restaurant")
def create_restaurant(restaurant_data: RestaurantCreate):
    try:
        return restaurant_service.create_restaurant(restaurant_data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))