from app.repositories import json_storage
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate

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

def add(restaurant_data: RestaurantCreate) -> Restaurant:
    # Give the new restaurant the next id and save it and and return it.
    data_json = json_storage.read_list(FILENAME)
    restaurant = Restaurant(
        id=json_storage.next_id(data_json, "A"),
        name=restaurant_data.name,
        cuisine=restaurant_data.cuisine,
        rating=None,
        address=restaurant_data.address,
        is_open=restaurant_data.is_open,
    )
    data_json.append(restaurant.model_dump())
    json_storage.write_list(FILENAME, data_json)
    return restaurant

def update(restaurant_id: str, restaurant_data: RestaurantUpdate) -> Restaurant | None:
    data_json = json_storage.read_list(FILENAME)
    for index, record in enumerate(data_json):
        if record["id"] == restaurant_id:
            restaurant = Restaurant.model_validate(record)
            if restaurant_data.name is not None:
                restaurant.name = restaurant_data.name
            if restaurant_data.cuisine is not None:
                restaurant.cuisine = restaurant_data.cuisine
            if restaurant_data.address is not None:
                restaurant.address = restaurant_data.address
            if restaurant_data.is_open is not None:
                restaurant.is_open = restaurant_data.is_open
            data_json[index] = restaurant.model_dump()
            json_storage.write_list(FILENAME, data_json)
            return restaurant
    return None