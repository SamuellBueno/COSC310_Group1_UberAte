import pytest
from app.repositories.restaurant_repository import load_restaurants

def test_restaurant_load_restaurants_list():
    restaurants = load_restaurants()

    assert isinstance (restaurants, list)

def test_restaurant_load_restaurants_dictionary():
    restaurants = load_restaurants()

    assert isinstance(restaurants[0], dict)

def test_restaurant_load_restaurants_at_least_two_restaurants():
    restaurants = load_restaurants()

    assert len(restaurants) >= 2

def test_restaurant_load_restaurants_stable_identifiers():
    restaurants = load_restaurants()

    ids = [restaurant["id"] for restaurant in restaurants]
    assert len(ids) == len(set(ids))