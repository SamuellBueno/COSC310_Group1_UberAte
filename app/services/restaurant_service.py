from app.repositories import restaurant_repository
from app.core.errors import BusinessRuleError, ConflictError, NotFoundError
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.schemas.user import User
from app.services.access import ensure_can_manage

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
        raise NotFoundError(f"Restaurant '{restaurant_id}' does not exist.")
    
    return restaurant

def _ensure_name_is_free(name: str, ignore_id: str | None = None) -> None:
    # helper elimates duplicate code smell
    for other in restaurant_repository.load_restaurants():
        if other.id != ignore_id and other.name.lower() == name.lower():
            raise ConflictError("A Restaurant with this name already exists")

def create_restaurant(restaurant_data: RestaurantCreate, actor: User) -> Restaurant:
    _ensure_name_is_free(restaurant_data.name)
    return restaurant_repository.add(restaurant_data, owner_id = actor.id)

def update_restaurant(restaurant_id: str, restaurant_data: RestaurantUpdate, actor: User) -> Restaurant:
    if restaurant_data.name is None and restaurant_data.cuisine is None and restaurant_data.address is None and restaurant_data.is_open is None:
        raise BusinessRuleError("Send at least one field to update")

    restaurant = restaurant_repository.get_by_id(restaurant_id)
    if restaurant is None:
        raise NotFoundError("Restaurant not found")

    ensure_can_manage(actor, restaurant)

    if restaurant_data.name is not None:
        _ensure_name_is_free(restaurant_data.name, ignore_id=restaurant_id)

    updated = restaurant_repository.update(restaurant_id, restaurant_data)
    if updated is None:
        raise NotFoundError("Restaurant not found")
    return updated
