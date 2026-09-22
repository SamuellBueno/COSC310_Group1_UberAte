import os
from pathlib import Path

DATA_DIR_ENV_VAR = "COSC310_DATA_DIR"
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def get_data_dir() -> Path:
    """Return the folder that holds the JSON data files."""
    value = os.getenv(DATA_DIR_ENV_VAR)
    return Path(value) if value else DEFAULT_DATA_DIR