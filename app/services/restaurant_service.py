from app.repositories import restaurant_repository
from app.schemas.restaurant import Restaurant, RestaurantCreate

def list_restaurants(cuisine: str | None = None, search: str | None = None, open: bool = False) -> list[Restaurant]:
    restaurants = restaurant_repository.load_restaurants();

    if cuisine:
        restaurants = [r for r in restaurants if r.cuisine.lower() == cuisine.lower().strip()]
    if search:
        search_text = search.lower().strip()
        restaurants = [r for r in restaurants if search_text in r.name.lower()]
    if open:
        restaurants = [r for r in restaurants if r.is_open]
    return restaurants

def get_restaurant(restaurant_id: str) -> Restaurant:
    restaurant = restaurant_repository.get_by_id(restaurant_id)

    if restaurant is None:
        raise ValueError(f"Restaurant '{restaurant_id}' does not exist.")

    return restaurant

def create_restaurant(restaurant_data: RestaurantCreate) -> Restaurant:
    restaurants = restaurant_repository.load_restaurants()

    for r in restaurants:
        if r.name.lower() == restaurant_data.name.lower():
            raise ValueError("A Restaurant with this name already exists")
        
    return restaurant_repository.add(restaurant_data)
