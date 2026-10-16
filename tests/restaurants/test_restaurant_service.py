import pytest
from app.repositories.restaurant_repository import load_restaurants
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate
from app.services.restaurant_service import list_restaurants, create_restaurant, get_restaurant, update_restaurant

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

def test_cuisine_filter():
    test = create_restaurant (
        RestaurantCreate(
            name = "Test Pizza Place",
            cuisine = "Pizza",
            address = "123 Address",
            is_open = True
        )
    )
    restaurants = list_restaurants(cuisine = "PIZZA")

    assert test.id in [r.id for r in restaurants]
    assert all(r.cuisine.lower() == "pizza" for r in restaurants)

def test_name_search():
    test = create_restaurant (
        RestaurantCreate(
            name = "Test Pizza Place",
            cuisine = "Pizza",
            address = "123 Address",
            is_open = True
        )
    )
    restaurants = list_restaurants(search = "PLACE")

    assert test.id in [r.id for r in restaurants]
    assert all("place" in r.name.lower() for r in restaurants)

def test_open():
    open_restaurant = create_restaurant (
            RestaurantCreate(
                name = "Test Open Pizza Place",
                cuisine = "Pizza",
                address = "123 Address",
                is_open = True
            )
        )

    closed_restaurant = create_restaurant (
                RestaurantCreate(
                    name = "Test Closed Pizza Place",
                    cuisine = "Pizza",
                    address = "321 Address",
                    is_open = False
                )
            )

    restaurants = list_restaurants(open = True)
    ids = [r.id for r in restaurants]

    assert open_restaurant.id in ids
    assert closed_restaurant.id not in ids
    assert all(r.is_open for r in restaurants)

def test_all_filters():
    test = create_restaurant (
            RestaurantCreate(
                name = "Test Pizza Place",
                cuisine = "Pizza",
                address = "123 Address",
                is_open = True
            )
        )
    restaurants = list_restaurants(cuisine = "Pizza", search = "TEST", open = True)

    assert [r.id for r in restaurants] == [test.id]

def test_get_restaurant():
    test = create_restaurant(
        RestaurantCreate(
            name = "Test Pizza Place",
            cuisine = "Pizza",
            address = "123 Address",
            is_open = True
        )
    )
    restaurant = get_restaurant(test.id)
    assert restaurant == test

def test_get_unknown_id():
    with pytest.raises(ValueError):
        get_restaurant("TEST1")

def test_update_restaurant_is_saved():
    restaurant = load_restaurants()[1]
    updated = update_restaurant(restaurant.id, RestaurantUpdate(name="Test Updated Name"))

    assert updated is not None
    assert get_restaurant(restaurant.id).name == "Test Updated Name"

def test_update_restaurant_duplicate_name_is_rejected():
    restaurants = load_restaurants()

    with pytest.raises(ValueError):
        update_restaurant(restaurants[1].id, RestaurantUpdate(name=restaurants[0].name))

def test_update_restaurant_can_keep_its_own_name():
    restaurant = load_restaurants()[1]

    assert update_restaurant(restaurant.id, RestaurantUpdate(name=restaurant.name)) is not None
