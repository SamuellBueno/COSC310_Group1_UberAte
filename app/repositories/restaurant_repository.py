from app.repositories import json_storage

FILENAME = "restaurants.json"


def load_restaurants() -> list[dict]:
    """Return every restaurant in the data file as a list of dictionaries."""
    # Reads through json_storage, which looks up the data folder on every call.
    # The old version fixed the path once at import, so tests read the real data.
    return json_storage.read_list(FILENAME)


def get_by_id(restaurant_id: str) -> dict | None:
    """Return the restaurant with this id, or None if there is none."""
    for restaurant in load_restaurants():
        if restaurant["id"] == restaurant_id:
            return restaurant
    return None