from uuid import uuid4

from app.core.errors import DataStoreError
from app.repositories import json_storage
from app.schemas.cart import Cart

FILENAME = "carts.json"

def new_cart_id() -> str:
    return f"C-{uuid4().hex[:8]}"

def list_all() -> list[Cart]:
    raw_items = json_storage.read_list(FILENAME)
    try:
        return [Cart.model_validate(item) for item in raw_items]
    except Exception as exc:
        raise DataStoreError(f"invalid cart data in {FILENAME}")from exc

def get_by_id(cart_id: str) -> Cart | None:
    for cart in list_all():
        if cart.id == cart_id:
            return cart
    return None

def get_by_customer(customer_id: str) -> Cart | None:
    for cart in list_all():
        if cart.customer_id == customer_id:
            return cart
    return None

def save(cart: Cart) -> Cart:
    carts = list_all()
    updated = False
    for idx, existing in enumerate(carts):
        if existing.id == cart.id:
            carts[idx] = cart
            updated = True
            break
    if not updated:
        carts.append(cart)
    json_storage.write_list(FILENAME, [c.model_dump() for c in carts])
    return cart

def delete(cart_id: str) -> bool:
    carts = list_all()
    remaining = [c for c in carts if c.id != cart_id]
    if len(remaining) == len(carts):
        return False
    json_storage.write_list(FILENAME, [c.model_dump() for c in remaining])
    return True