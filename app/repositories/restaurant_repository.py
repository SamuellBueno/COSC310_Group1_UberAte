from app.repositories import json_storage
from app.schemas.restaurant import Restaurant

FILENAME = "restaurants.json"


def load_restaurants() -> list[Restaurant]:
    """Return every restaurant in the data file as a list of Restaurant objects"""
    restaurants = json_storage.read_list(FILENAME)
    return [Restaurant.model_validate(restaurant) for restaurant in restaurants]


def get_by_id(restaurant_id: str) -> Restaurant | None:
    """Return the restaurant with this id, or None if there is none."""
    for restaurant in load_restaurants():
        if restaurant.id == restaurant_id:
            return restaurant
    return None
