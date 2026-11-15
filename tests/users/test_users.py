import json

import pytest
from pydantic import ValidationError
from app.core.security import hash_password, verify_password
from app.repositories import user_repository
from app.schemas.user import RegisterRequest, UserPublic

# a small known set of users for the repository tests, so they don't depend on data/users.json
# the hashes are fake, these tests check storage not passwords
USERS = [
    {"id": "U1", "email": "alex@test.com", "password_hash": "$2b$fake-1", "role": "customer",
     "name": "Alex", "phone": None, "delivery_address": "1 Test St", "is_active": True},
    {"id": "U2", "email": "owner@test.com", "password_hash": "$2b$fake-2", "role": "restaurant_owner",
     "name": "Owner", "phone": None, "delivery_address": None, "is_active": True},
]

NEW_CUSTOMER = RegisterRequest(email="Jo@Example.com", password="LongEnough1", name="Jo")


@pytest.fixture
def known_users(isolated_data):
    # overwrite the temporary users.json with the users above, only for the tests that ask for it
    (isolated_data / "users.json").write_text(json.dumps(USERS), encoding="utf-8")


# --- hashing ---

def test_hash_and_verify_password():
    # the hash never contains the password, the right one passes, a wrong one fails
    hashed = hash_password("Password123!")
    assert "Password123!" not in hashed
    assert verify_password("Password123!", hashed) is True
    assert verify_password("password123!", hashed) is False


def test_verify_rejects_garbage_hash():
    # failure case: a stored value that isn't a bcrypt hash gives False instead of crashing
    assert verify_password("x", "not-a-hash") is False
    

# --- sign up rules ---

def test_sign_up_cannot_choose_a_role():
    # failure case: nobody can sign themselves up as an admin
    with pytest.raises(ValidationError):
        RegisterRequest(email="jo@example.com", password="LongEnough1", name="Jo", role="admin")


def test_password_too_short_is_refused():
    # failure case: under 5 characters is refused
    with pytest.raises(ValidationError):
        RegisterRequest(email="jo@example.com", password="lil", name="Jo")


def test_password_too_long_is_refused():
    # failure case: over 20 characters is refused
    with pytest.raises(ValidationError):
        RegisterRequest(email="jo@example.com", password="xxxxxxxxxxxxxxxxxxxxxx", name="Jo")


def test_public_user_has_no_password_hash():
    # the model we use to show users their info should not have the hash
    assert "password_hash" not in UserPublic.model_fields


# --- repository, on the known users above ---

def test_get_by_email_ignores_capitals(known_users):
    # same account whatever the capitals, an unknown email gives None
    assert user_repository.get_by_email("ALEX@test.com").id == "U1"
    assert user_repository.get_by_email("ghost@test.com") is None


def test_add_customer_saves_a_new_customer(known_users):
    # next id after U2, email stored lowercase, always a customer, saved to the file
    user = user_repository.add_customer(NEW_CUSTOMER, "$2b$fake-new")
    assert user.id == "U3"
    assert user.email == "jo@example.com"
    assert user.role == "customer"
    assert user_repository.get_by_id("U3") is not None


def test_broken_record_raises_data_store_error(isolated_data):
    # failure case: a record missing its fields is caught, not a crash
    (isolated_data / "users.json").write_text('[{"id": "U1"}]', encoding="utf-8")
    with pytest.raises(ValueError):
        user_repository.list_all()
