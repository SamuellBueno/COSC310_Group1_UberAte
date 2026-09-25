import json
from pathlib import Path

RESTAURANT_PATH = Path("data/restaurants.json")


def load_restaurants() -> list[dict]:
        """Read the restaurants file and return it as a list of dictionaries."""
        with RESTAURANT_PATH.open() as f:
            return json.load(f)