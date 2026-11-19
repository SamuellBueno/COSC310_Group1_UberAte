import pytest
from app.repositories import session_repository

def test_profile_view_needs_sign_in(client):
    response = client.get("/customers/me")

    assert response.status_code == 401

def test_profile_update_needs_sign_in(client):
    response = client.patch("/customers/me",json={"delivery_address": "50 Main Street, Kelowna"},)

    assert response.status_code == 401

def test_owner_is_not_a_customer(client):
    session = session_repository.add("U2")
    headers = {"Authorization": f"Bearer {session.session_id}"}

    response = client.get("/customers/me", headers=headers)

    assert response.status_code == 403

def test_get_my_profile(client):
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},)
    assert login.status_code == 200
    session_id = login.json()["session_id"]

    response = client.get("/customers/me",headers={"Authorization": f"Bearer {session_id}"},)

    assert response.status_code == 200
    profile = response.json()
    assert profile["id"] == "U4"
    assert profile["name"] == "Alex Customer"
    assert "password_hash" not in profile

def test_update_address_changes_only_that_field(client):
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    before = client.get("/customers/me", headers=headers)
    assert before.status_code == 200

    new_address = "50 Main Street, Kelowna"
    response = client.patch("/customers/me",headers=headers,json={"delivery_address": new_address},)

    assert response.status_code == 200
    expected = before.json()
    expected["delivery_address"] = new_address
    assert response.json() == expected

    saved_profile = client.get("/customers/me", headers=headers)
    assert saved_profile.status_code == 200
    assert saved_profile.json() == expected

def test_update_nothing_returns_400(client):
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    response = client.patch("/customers/me", headers=headers, json={})

    assert response.status_code == 400
    assert response.json()["detail"] == "Send at least one field to update"

def test_cannot_update_role_through_profile(client):
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    response = client.patch(
        "/customers/me", headers=headers, json={"role": "admin"}
    )

    assert response.status_code == 422


def test_cannot_update_email_through_profile(client):
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    response = client.patch(
        "/customers/me", headers=headers, json={"email": "new@uberate.test"}
    )

    assert response.status_code == 422