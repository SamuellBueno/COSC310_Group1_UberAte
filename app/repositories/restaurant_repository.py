import json
from app.core.config import get_data_dir

RESTAURANT_PATH = get_data_dir() / "restaurants.json"


def load_restaurants() -> list[dict]:
        """Read the restaurants file and return it as a list of dictionaries."""
        with RESTAURANT_PATH.open() as f:
            return json.load(f)