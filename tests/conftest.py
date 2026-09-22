import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

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