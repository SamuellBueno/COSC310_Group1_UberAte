import shutil
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import session_repository

REAL_DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    """Give every test its own temporary copy of the data files."""
    for file in REAL_DATA.glob("*.json"):
        shutil.copy(file, tmp_path / file.name)
    monkeypatch.setenv("COSC310_DATA_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def owner_headers():
    session = session_repository.add("U2")
    return {"Authorization": f"Bearer {session.session_id}"}