import pytest
from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.repositories.restaurant_repository import load_restaurants
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate
from app.services.restaurant_service import list_restaurants, create_restaurant, get_restaurant, update_restaurant
from app.repositories import user_repository

def owner():
    user = user_repository.get_by_id("U2")
    assert user is not None
    return user

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
    restaurant = create_restaurant(
        RestaurantCreate(
            name="DonaldMac",
            cuisine="burger",
            address="123street",
            is_open=True,
        ),
        actor=owner(),
    )

    ids = []
    for r in load_restaurants():
        ids.append(r.id)

    assert restaurant.id in ids

def test_duplicate_create_restaurant_is_rejected():
    restaurant_data = RestaurantCreate(
        name="DonaldMac",
        cuisine="burger",
        address="123street",
        is_open=True,
    )
    actor = owner()

    create_restaurant(restaurant_data, actor=actor)

    with pytest.raises(ConflictError):
        create_restaurant(restaurant_data, actor=actor)

def test_cuisine_filter():
    test = create_restaurant(
        RestaurantCreate(
            name="Test Pizza Place",
            cuisine="Pizza",
            address="123 Address",
            is_open=True,
        ),
        actor=owner(),
    )
    restaurants = list_restaurants(cuisine="PIZZA")

    assert test.id in [r.id for r in restaurants]
    assert all(r.cuisine.lower() == "pizza" for r in restaurants)

def test_name_search():
    test = create_restaurant(
        RestaurantCreate(
            name="Test Pizza Place",
            cuisine="Pizza",
            address="123 Address",
            is_open=True,
        ),
        actor=owner(),
    )

    restaurants = list_restaurants(search="PLACE")

    assert test.id in [r.id for r in restaurants]
    assert all("place" in r.name.lower() for r in restaurants)

def test_open():
    open_restaurant = create_restaurant(
        RestaurantCreate(
            name="Test Open Pizza Place",
            cuisine="Pizza",
            address="123 Address",
            is_open=True,
        ),
        actor=owner(),
    )

    closed_restaurant = create_restaurant(
        RestaurantCreate(
            name="Test Closed Pizza Place",
            cuisine="Pizza",
            address="321 Address",
            is_open=False,
        ),
        actor=owner(),
    )

    restaurants = list_restaurants(open=True)
    ids = [r.id for r in restaurants]

    assert open_restaurant.id in ids
    assert closed_restaurant.id not in ids
    assert all(r.is_open for r in restaurants)

def test_all_filters():
    test = create_restaurant(
        RestaurantCreate(
            name="Test Pizza Place",
            cuisine="Pizza",
            address="123 Address",
            is_open=True,
        ),
        actor=owner(),
    )

    restaurants = list_restaurants(cuisine="Pizza", search="TEST", open=True)

    assert [r.id for r in restaurants] == [test.id]

def test_get_restaurant():
    test = create_restaurant(
        RestaurantCreate(
            name="Test Pizza Place",
            cuisine="Pizza",
            address="123 Address",
            is_open=True,
        ),
        actor=owner(),
    )

    restaurant = get_restaurant(test.id)

    assert restaurant == test

def test_get_unknown_id():
    with pytest.raises(NotFoundError):
        get_restaurant("TEST1")

def test_update_restaurant_is_saved():
    updated = update_restaurant(
        "A1",
        RestaurantUpdate(name="Test Updated Name"),
        actor=owner(),
    )

    assert updated is not None
    assert get_restaurant("A1").name == "Test Updated Name"

def test_update_restaurant_duplicate_name_is_rejected():
    existing_name = get_restaurant("A2").name

    with pytest.raises(ConflictError):
        update_restaurant(
            "A1",
            RestaurantUpdate(name=existing_name),
            actor=owner(),
        )

def test_update_restaurant_can_keep_its_own_name():
    restaurant = get_restaurant("A1")

    updated = update_restaurant(
        restaurant.id,
        RestaurantUpdate(name=restaurant.name),
        actor=owner(),
    )

    assert updated.name == restaurant.name

def test_owner_cannot_update_another_owners_restaurant():
    other_owner = user_repository.get_by_id("U3")
    assert other_owner is not None
    before = get_restaurant("A1")

    with pytest.raises(PermissionDeniedError):
        update_restaurant(
            "A1",
            RestaurantUpdate(name="Unauthorized Name"),
            actor=other_owner,
        )

    assert get_restaurant("A1") == before

def test_admin_can_update_any_restaurant():
    admin = user_repository.get_by_id("U1")
    assert admin is not None

    updated = update_restaurant(
        "A1",
        RestaurantUpdate(name="Admin Updated Name"),
        actor=admin,
    )

    assert updated.name == "Admin Updated Name"
    assert updated.owner_id == "U2"
    assert get_restaurant("A1").name == "Admin Updated Name"