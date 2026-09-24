import pytest
from pydantic import ValidationError

from app.schemas.restaurant import Restaurant

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