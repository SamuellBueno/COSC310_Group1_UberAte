import json

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.role_checks import require_customer, require_manager
from app.main import app
from app.repositories import user_repository


def test_login_returns_a_session_and_the_user(client):
    # right email and password: a session id comes back, plus who signed in
    response = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["session_id"]) >= 40
    assert body["user"]["id"] == "U4"


def test_wrong_password_and_unknown_email_look_the_same(client):
    # failure case: both 401 with the same message, so nobody can find out which emails have accounts
    wrong = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "nope12"})
    unknown = client.post("/auth/login", json={"email": "ghost@uberate.test", "password": "nope12"})
    assert wrong.status_code == 401
    assert unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_deactivated_account_cannot_sign_in(client):
    # failure case: Former Customer (U6) is deactivated in the seed data
    response = client.post("/auth/login", json={"email": "former@uberate.test", "password": "Password123!"})
    assert response.status_code == 401


def test_me_returns_who_is_signed_in(client):
    # sign in as Alex, then /auth/me says who you are, without the hash
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == "U4"
    assert "password_hash" not in response.json()


def test_me_without_signing_in_returns_401(client):
    # failure case: no session id sent, or a made up one
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer made-up"}).status_code == 401


def test_expired_session_returns_401(client, isolated_data):
    # failure case: push the session's expiry into the past, it must stop working
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}
    path = isolated_data / "sessions.json"
    sessions = json.loads(path.read_text(encoding="utf-8"))
    sessions[0]["expires_at"] = "2000-01-01T00:00:00+00:00"
    path.write_text(json.dumps(sessions), encoding="utf-8")
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_logout_ends_the_session(client):
    # after signing out, the same session id is refused
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}
    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_session_survives_a_restart(client):
    # a brand new client (like restarting the app) still accepts the session, it lives in sessions.json
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}
    fresh_client = TestClient(app)
    assert fresh_client.get("/auth/me", headers=headers).status_code == 200


def test_deactivated_after_signing_in_returns_403(client):
    # signed in, then the account gets deactivated: the very next request is refused
    login = client.post("/auth/login", json={"email": "alex@uberate.test", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login.json()['session_id']}"}
    user_repository.update("U4", {"is_active": False})
    assert client.get("/auth/me", headers=headers).status_code == 403


def test_role_checks():
    # the role checks only let the right kind of account through
    customer = user_repository.get_by_id("U4")
    owner = user_repository.get_by_id("U2")
    assert require_customer(customer) == customer
    assert require_manager(owner) == owner
    # failure cases: an owner isn't a customer, a customer isn't a manager
    with pytest.raises(HTTPException):
        require_customer(owner)
    with pytest.raises(HTTPException):
        require_manager(customer)