from app.repositories import restaurant_repository
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate

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

def update_restaurant(restaurant_id: str, restaurant_data: RestaurantUpdate) -> Restaurant | None:
    if restaurant_data.name is None and restaurant_data.cuisine is None and restaurant_data.address is None and restaurant_data.is_open is None:
        raise ValueError("Send at least one field to update")

    if restaurant_repository.get_by_id(restaurant_id) is None:
        return None

    if restaurant_data.name is not None:
        for r in restaurant_repository.load_restaurants():
            if r.id != restaurant_id and r.name.lower() == restaurant_data.name.lower():
                raise ValueError("A Restaurant with this name already exists")

    return restaurant_repository.update(restaurant_id, restaurant_data)

