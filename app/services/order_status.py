from app.core.errors import ConflictError

ALLOWED_MOVES = {
    "placed": ["preparing", "cancelled"],
    "preparing": ["ready"],
    "ready": ["out_for_delivery"],
    "out_for_delivery": ["delivered"],
    "delivered": [],
    "cancelled": [],
}

def check_move(current: str, new: str) -> None:
    """raise a 409 if an order can't go from current to new"""
    if new not in ALLOWED_MOVES[current]:
        raise ConflictError(f"An order that is {current} cannot become {new}.")