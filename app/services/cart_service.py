from uuid import uuid4

from app.repositories import cart_repository, menu_item_repository
from app.schemas.cart import Cart, CartLineView, CartView
from app.services import pricing


def to_view(cart: Cart) -> CartView:
    line_views: list[CartLineView] = []
    line_totals = []

    for line in cart.items:
        item = menu_item_repository.get_by_id(line.menu_item_id)
        if item is None:
            continue
        unit_price = pricing.money(item.price)
        total = pricing.line_total(unit_price, line.quantity)
        line_totals.append(total)
        line_views.append(
            CartLineView(
                menu_item_id=item.id,
                name=item.name,
                unit_price=unit_price,
                quantity=line.quantity,
                line_total=total,
            )
        )

    subtotal, delivery_fee, total = pricing.totals(line_totals)
    return CartView(
        id=cart.id,
        customer_id=cart.customer_id,
        restaurant_id=cart.restaurant_id,
        items=line_views,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
    )


def get_or_create_cart(customer_id: str) -> CartView:
    existing = cart_repository.get_by_customer(customer_id)
    if existing is not None:
        return to_view(existing)

    new_cart = Cart(
        id=f"C-{uuid4().hex[:8]}",
        customer_id=customer_id,
        restaurant_id=None,
        items=[],
    )
    cart_repository.save(new_cart)
    return to_view(new_cart)