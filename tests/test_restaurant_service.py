import pytest
from app.services.restaurant_service import list_restaurants

def test_list_restaurants_returns_list():
    restaurants = list_restaurants()

    assert isinstance(restaurants, list)

def test_list_restaurants_correct_types():
    restaurants = list_restaurants()

    for r in restaurants:
        assert isinstance(r['id'], str)
        assert isinstance(r['name'], str)
        assert isinstance(r['cuisine'], str)
        assert isinstance(r['rating'], float)
        assert isinstance(r['address'], str)
        assert isinstance(r['is_open'], bool)