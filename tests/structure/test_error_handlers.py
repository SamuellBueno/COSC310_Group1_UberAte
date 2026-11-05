from app.core.errors import (
    AuthenticationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.main import STATUS_FOR_ERROR


def test_each_error_maps_to_its_status():
    # each domain error has one status code
    assert STATUS_FOR_ERROR[NotFoundError] == 404
    assert STATUS_FOR_ERROR[ConflictError] == 409
    assert STATUS_FOR_ERROR[BusinessRuleError] == 400
    assert STATUS_FOR_ERROR[AuthenticationError] == 401
    assert STATUS_FOR_ERROR[PermissionDeniedError] == 403


def test_broken_data_file_returns_500(client, isolated_data):
    # broken data files return a safe server error
    (isolated_data / "restaurants.json").write_text("not json", encoding="utf-8")
    response = client.get("/restaurants")
    assert response.status_code == 500
    assert response.json() == {"detail": "Data storage error"}
