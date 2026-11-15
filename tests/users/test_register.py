from app.core.security import verify_password
from app.repositories import user_repository

# a valid sign up used by most tests, the email isn't in the seed data
NEW_CUSTOMER = {"email": "notanemail@Example.com", "password": "Secret123", "name": "Jo", "delivery_address": "1 Main St"}


def test_register_returns_201_and_a_customer(client):
    # a new account is made, always a customer, email saved lowercase
    response = client.post("/auth/register", json=NEW_CUSTOMER)
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "customer"
    assert body["email"] == "notanemail@example.com"


def test_register_saves_a_hash_that_works(client, isolated_data):
    # the file has the hash not the password, and the hash matches the password
    client.post("/auth/register", json=NEW_CUSTOMER)
    assert "Secret123" not in (isolated_data / "users.json").read_text(encoding="utf-8")
    saved = user_repository.get_by_email("notanemail@Example.com")
    assert verify_password("Secret123", saved.password_hash)


def test_same_email_with_other_capitals_returns_409(client):
    # failure case: one account per email, capitals don't matter
    client.post("/auth/register", json=NEW_CUSTOMER)
    second = {"email": "notanEMAIL@Example.com", "password": "Other1234", "name": "Jo Two"}
    response = client.post("/auth/register", json=second)
    assert response.status_code == 409


def test_register_with_a_role_returns_422(client):
    # failure case: nobody can sign themselves up as an admin
    body = {"email": "sneaky@example.com", "password": "Secret123", "name": "Sneaky", "role": "admin"}
    response = client.post("/auth/register", json=body)
    assert response.status_code == 422


def test_register_with_short_password_returns_422(client):
    # failure case: under 5 characters is refused before our code runs
    body = {"email": "short@example.com", "password": "abc", "name": "Short"}
    response = client.post("/auth/register", json=body)
    assert response.status_code == 422