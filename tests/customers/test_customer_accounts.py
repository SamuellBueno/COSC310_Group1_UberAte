import pytest
from app.repositories import session_repository

def test_profile_view_needs_sign_in(client):
    response = client.get("/customers/me")

    assert response.status_code == 401

def test_profile_update_needs_sign_in(client):
    # Tries changing the address without signing in
    response = client.patch("/customers/me",json={"delivery_address": "50 Main Street, Kelowna"},)

    assert response.status_code == 401

def test_owner_is_not_a_customer(client):
    session = session_repository.add("U2") # U2 is the test account for a restaurant owner
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

    # Checks that only the address changed
    expected = before.json()
    expected["delivery_address"] = new_address
    assert response.json() == expected

    # Loads the profile again to check that the new address was saved
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
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    response = client.patch(
        "/customers/me", headers=headers, json={"email": "new@uberate.test"}
    )

    assert response.status_code == 422

def test_close_my_account_marks_customer_inactive(client):
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    response = client.delete("/customers/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["is_active"] is False

def test_closed_account_cannot_reuse_session(client):
    login = client.post("/auth/login",json={"email": "alex@uberate.test", "password": "Password123!"},)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    assert client.get("/customers/me", headers=headers).status_code == 200
    assert client.delete("/customers/me", headers=headers).status_code == 200

    # Reuse the same session that worked before the account was closed
    response = client.get("/customers/me", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "This account is deactivated"

def test_closed_account_cannot_sign_in_again(client):
    credentials = {"email": "alex@uberate.test","password": "Password123!",}
    login = client.post("/auth/login", json=credentials)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}

    assert client.delete("/customers/me", headers=headers).status_code == 200

    # Try signing in again with the same email and password
    response = client.post("/auth/login", json=credentials)

    assert response.status_code == 403
    assert response.json()["detail"] == "This account is deactivated"