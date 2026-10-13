import pytest
from app.repositories.restaurant_repository import load_restaurants
from app.schemas.restaurant import RestaurantCreate
from app.services.restaurant_service import list_restaurants, create_restaurant

def test_list_restaurants_returns_list():
    restaurants = list_restaurants()

    assert isinstance(restaurants, list)

def test_list_restaurants_correct_types():
    restaurants = list_restaurants()

    for r in restaurants:
        assert isinstance(r.id, str)
        assert isinstance(r.name, str)
        assert isinstance(r.cuisine, str)
        assert r.rating is None or isinstance(r.rating, float)
        assert isinstance(r.address, str)
        assert isinstance(r.is_open, bool)

def test_create_restaurant_is_saved():
    restaurant = create_restaurant(RestaurantCreate(name="DonaldMac", cuisine="burger", address="123street", is_open=True))

    ids = []
    for r in load_restaurants():
        ids.append(r.id)

    assert restaurant.id in ids

def test_duplicate_create_restaurant_is_rejected():
    create_restaurant(RestaurantCreate(name="DonaldMac", cuisine="burger", address="123street", is_open=True))

    with pytest.raises(ValueError):
        create_restaurant(RestaurantCreate(name="DonaldMac", cuisine="burger", address="123street", is_open=True))
