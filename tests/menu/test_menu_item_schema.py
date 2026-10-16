import pytest
from pydantic import ValidationError

from app.schemas.menu_item import MenuItem


def test_valid_menu_item_creation():
    data = {
        "id": "M1",
        "restaurant_id": "A1",
        "name": "Dragon Roll",
        "description": "Classic sushi roll with avocado and eel",
        "category": "Sushi",
        "price": 14.50,
        "available": True,
    }
    item = MenuItem(**data)
    assert item.id == "M1"
    assert item.restaurant_id == "A1"
    assert item.name == "Dragon Roll"
    assert item.price == 14.50
    assert item.available is True


def test_default_values():
    item = MenuItem(
        id="M2",
        restaurant_id="A1",
        name="Salmon Nigiri",
        category="Sushi",
        price=6.50,
    )
    assert item.description == ""
    assert item.available is True


@pytest.mark.parametrize("invalid_price", [0, -1.0, -15.50, 1000.0])
def test_price_boundaries_rejected(invalid_price):
    with pytest.raises(ValidationError):
        MenuItem(
            id="M3",
            restaurant_id="A1",
            name="Spicy Tuna Roll",
            category="Sushi",
            price=invalid_price,
        )


def test_empty_strings_rejected_for_ids():
    with pytest.raises(ValidationError):
        MenuItem(
            id="",
            restaurant_id="A1",
            name="Roll",
            category="Sushi",
            price=5.0,
        )

    with pytest.raises(ValidationError):
        MenuItem(
            id="M1",
            restaurant_id="",
            name="Roll",
            category="Sushi",
            price=5.0,
        )


def test_missing_required_fields_raise_validation_error():
    with pytest.raises(ValidationError):
        MenuItem(
            id="M1",
            name="Veggie Roll",
            category="Sushi",
            price=5.0,
        )

    with pytest.raises(ValidationError):
        MenuItem(
            id="M1",
            restaurant_id="A1",
            name="Veggie Roll",
            price=5.0,
        )