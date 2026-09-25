from fastapi import APIRouter
from app.services import restaurant_service
from app.schemas.restaurant import Restaurant

router = APIRouter(tags=['restaurants'])
@router.get("/restaurants", response_model=list[Restaurant])
def list_restaurants():
    return restaurant_service.list_restaurants()