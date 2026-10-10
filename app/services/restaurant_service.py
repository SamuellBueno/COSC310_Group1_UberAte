from app.repositories import restaurant_repository
from app.schemas.restaurant import Restaurant, RestaurantCreate

def list_restaurants() -> list[Restaurant]:
    # No business rules needed so just passing through
    return restaurant_repository.load_restaurants();

def create_restaurant(restaurant_data: RestaurantCreate) -> Restaurant:
    restaurants = restaurant_repository.load_restaurants()

    for r in restaurants:
        if r.name.lower() == restaurant_data.name.lower():
            raise ValueError("A Restaurant with this name already exists")
        
    return restaurant_repository.add(restaurant_data)
