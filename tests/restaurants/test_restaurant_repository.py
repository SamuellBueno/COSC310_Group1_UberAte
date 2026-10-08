import pytest
from app.repositories.restaurant_repository import load_restaurants, get_by_id
from app.schemas.restaurant import Restaurant

def test_restaurant_load_restaurants_list():
    restaurants = load_restaurants()

    assert isinstance (restaurants, list)

def test_restaurant_load_restaurants_pydantic_model():
    restaurants = load_restaurants()

    assert isinstance(restaurants[0], Restaurant)

def test_restaurant_load_restaurants_at_least_two_restaurants():
    restaurants = load_restaurants()

    assert len(restaurants) >= 2

def test_restaurant_load_restaurants_stable_identifiers():
    restaurants = load_restaurants()

    ids = [restaurant.id for restaurant in restaurants]
    assert len(ids) == len(set(ids))

def test_get_by_id_exists():
    restaurants = load_restaurants()
    restaurant_id = restaurants[0].id
    restaurant = get_by_id(restaurant_id)

    assert isinstance(restaurant, Restaurant)

def test_get_by_id_does_not_exist():
    restaurant = get_by_id("id does not exist")

    assert restaurant is None