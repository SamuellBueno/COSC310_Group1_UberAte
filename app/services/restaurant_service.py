from app.repositories import restaurant_repository
from app.schemas.restaurant import Restaurant

def list_restaurants() -> list[dict]:
    # No business rules needed so just passing through
    return restaurant_repository.load_restaurants();
