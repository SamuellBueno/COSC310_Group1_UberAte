from app.core.errors import BusinessRuleError, ConflictError, NotFoundError
from app.repositories import cart_repository, menu_item_repository
from app.schemas.cart import Cart, CartItemAdd, CartLine, CartLineView, CartView
from app.services import pricing


MAX_ITEM_QUANTITY = 20


def add_item(customer_id: str, payload: CartItemAdd) -> CartView:
    item = menu_item_repository.get_by_id(payload.menu_item_id)
    if item is None:
        raise NotFoundError(f"Menu item '{payload.menu_item_id}' not found")
    if not item.active or not getattr(item, "available", True):
        raise BusinessRuleError(f"Menu item '{payload.menu_item_id}' is unavailable")

    cart = cart_repository.get_by_customer(customer_id)
    if cart is None:
        cart = Cart(
            id=cart_repository.new_cart_id(),
            customer_id=customer_id,
            restaurant_id=item.restaurant_id,
            items=[],
        )
    elif cart.items and cart.restaurant_id != item.restaurant_id:
        raise ConflictError("Cannot add items from a different restaurant to the active cart")
    else:
        cart.restaurant_id = item.restaurant_id

    for line in cart.items:
        if line.menu_item_id == item.id:
            new_quantity = line.quantity + payload.quantity
            if new_quantity > MAX_ITEM_QUANTITY:
                raise BusinessRuleError(
                    f"Item quantity cannot exceed {MAX_ITEM_QUANTITY}"
                )
            line.quantity = new_quantity
            break
    else:
        if payload.quantity > MAX_ITEM_QUANTITY:
            raise BusinessRuleError(
                f"Item quantity cannot exceed {MAX_ITEM_QUANTITY}"
            )
        cart.items.append(CartLine(menu_item_id=item.id, quantity=payload.quantity))

    cart_repository.save(cart)
    return to_view(cart)


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
        id=cart_repository.new_cart_id(),
        customer_id=customer_id,
        restaurant_id=None,
        items=[],
    )
    cart_repository.save(new_cart)
    return to_view(new_cart)