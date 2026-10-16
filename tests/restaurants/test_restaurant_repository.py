import pytest
from app.repositories.restaurant_repository import load_restaurants, get_by_id, add, update
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate

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

def test_add_is_saved_to_json():
    restaurant = add(RestaurantCreate(name="DonaldMac", cuisine="burger", address="123street", is_open=True))
    assert get_by_id(restaurant.id) is not None

def test_add_gives_no_rating():
    restaurant = add(RestaurantCreate(name="DonaldMac", cuisine="burger", address="123street", is_open=True))
    assert restaurant.rating == None

def test_update_is_saved_to_json():
    restaurants = load_restaurants()
    restaurant = restaurants[1]
    update(restaurant.id, RestaurantUpdate(address = "123 New Test Street"))
    updated = get_by_id(restaurant.id)
    assert updated is not None
    assert updated.address == "123 New Test Street"

def test_update_only_changes_fields_sent():
    restaurants = load_restaurants()
    restaurant = restaurants[1]
    updated = update(restaurant.id, RestaurantUpdate(name="Test Name"))
    assert updated is not None
    assert updated.name == "Test Name"
    assert updated.address == restaurant.address

def test_wrong_id_returns_none():
    assert update("random id", RestaurantUpdate(name="DonaldMacintosh")) is None

