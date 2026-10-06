import json

from app.core.config import get_data_dir


def read_list(filename: str) -> list[dict]:
    """Read a JSON file from the data folder and return its records as a list of dicts.
    Example: read_list("restaurants.json") returns every restaurant.
    """
    path = get_data_dir() / filename
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_list(filename: str, records: list[dict]) -> None:
    """Save a list of records to a JSON file in the data folder, replacing what was there.
    Callers read the list, change it, then pass the full updated list back in.
    """
    path = get_data_dir() / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        f.write("\n")


def next_id(records: list[dict], prefix: str) -> str:
    """Return the next free id for a prefix, e.g. "A6" when the highest restaurant id is "A5".
    Ids only go up and are never reused, even if there are gaps (A1, A2, A7 gives A8).
    Ids with a different prefix are ignored.
    """
    numbers = [
        int(r["id"][len(prefix):])
        for r in records
        if r["id"].startswith(prefix) and r["id"][len(prefix):].isdigit()
    ]
    return f"{prefix}{max(numbers, default=0) + 1}"