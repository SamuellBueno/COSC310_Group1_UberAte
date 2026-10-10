import pytest
from pydantic import ValidationError

from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate

#Must include all perameters
def test_restaurant_requires_an_id():
    with pytest.raises(ValidationError):
        Restaurant(name="DonaldMac", cuisine="burger", rating=5.0, address="123 street", is_open=True)

#rating cannot be greater than 5 or less than 0
def test_rating_bounds():
    with pytest.raises(ValidationError):
        Restaurant(id="mc", name="DonaldMac", cuisine="burger", rating=6.0, address="123street", is_open=True)

def test_valid_restaurant_is_accepted():
    restaurant = Restaurant(id="mc", name="DonaldMac", cuisine="burger", rating=5.0, address="123street", is_open=True)
    assert restaurant.id == "mc"

def test_restaurant_without_rating_is_accepted():
    restaurant = Restaurant(id="mc", name="DonaldMac", cuisine="burger", address="123street", is_open=True)
    assert restaurant.rating is None

#RestaurantCreate
def test_valid_restaurant_create_is_accepted():
    restaurant = RestaurantCreate(name="DonaldMac", cuisine="burger", address="123street", is_open=True)
    assert restaurant.is_open == True

def test_restaurant_create_with_rating_is_denied():
     with pytest.raises(ValidationError):
        restaurant = RestaurantCreate(name="DonaldMac", cuisine="burger", rating=5.0, address="123street", is_open=True)

def test_restaurant_create_with_id_is_denied():
     with pytest.raises(ValidationError):
        RestaurantCreate(id="mc", name="DonaldMac", cuisine="burger", address="123street", is_open=True)

def test_restaurant_create_rejects_empty_name():
    with pytest.raises(ValidationError):
        RestaurantCreate(name="", cuisine="burger", address="123street", is_open=True)

#RestaurantUpdate
def test_restaurant_update_is_open_only():
        restaurant = RestaurantUpdate(is_open=False)
        assert restaurant.is_open == False

def test_invalid_restaurant_update_is_denied():
     with pytest.raises(ValidationError):
         RestaurantUpdate(id="mc", name="DonaldMac", cuisine="burger", rating=5.0, address="123street", is_open=True)
