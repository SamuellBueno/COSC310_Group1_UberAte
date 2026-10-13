from fastapi import APIRouter, HTTPException
from app.services import restaurant_service
from app.schemas.restaurant import Restaurant, RestaurantCreate

router = APIRouter(tags=['restaurants'])
@router.get("/restaurants", response_model=list[Restaurant])
def list_restaurants():
    return restaurant_service.list_restaurants()

@router.post("/restaurants", response_model=Restaurant, status_code=201, summary="Create a Restaurant")
def create_restaurant(restaurant_data: RestaurantCreate):
    try:
        return restaurant_service.create_restaurant(restaurant_data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))