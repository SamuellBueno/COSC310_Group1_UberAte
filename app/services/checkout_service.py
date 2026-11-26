from app.repositories import cart_repository, menu_item_repository, order_repository, restaurant_repository, user_repository
from app.core.errors import BusinessRuleError, ConflictError, PermissionDeniedError
from app.schemas.cart import Cart
from app.schemas.order import Order, OrderCreate, OrderItem
from app.services import pricing


def _price_cart_items(cart: Cart):
    """Check every item against the current menu and return the order items and line totals."""
    order_items = []
    line_totals = []
    for line in cart.items:
        item = menu_item_repository.get_by_id(line.menu_item_id)
        if item is None or not item.active or not item.available or item.restaurant_id != cart.restaurant_id:
            raise BusinessRuleError("An item in your cart is no longer available. Review your cart.")
        unit_price = pricing.money(item.price)
        line_totals.append(pricing.line_total(unit_price, line.quantity))
        order_items.append(OrderItem(menu_item_id=item.id, name=item.name, unit_price=float(unit_price), quantity=line.quantity))
    return order_items, line_totals


def _clear_cart_or_undo_order(cart: Cart, order: Order) -> None:
    """Clear the cart. If that fails, delete the order so a retry can't create a duplicate."""
    try:
        cart_repository.save(cart.model_copy(update={"items": [], "restaurant_id": None}))
    except Exception:
        order_repository.delete(order.id)
        raise


def checkout(customer_id: str, expected_total: float) -> Order:
    user = user_repository.get_by_id(customer_id)
    if user is None or not user.is_active:
        raise PermissionDeniedError("Your account is not active.")

    cart = cart_repository.get_by_customer(customer_id)
    if cart is None or not cart.items:
        raise BusinessRuleError("Your cart is empty.")

    if cart.restaurant_id is None:
        raise BusinessRuleError("Your cart is invalid. Please clear it and add your items again.")

    restaurant = restaurant_repository.get_by_id(cart.restaurant_id)
    if restaurant is None:
        raise BusinessRuleError("The restaurant for this cart no longer exists.")

    if not restaurant.is_open:
        raise BusinessRuleError("This restaurant is currently closed. Please choose another restaurant.")
    
    # the order keeps the address the customer has right now, a later profile change must not rewrite it
    if not user.delivery_address:
        raise BusinessRuleError("Add a delivery address to your profile before checking out.")

    order_items, line_totals = _price_cart_items(cart)

    subtotal, delivery_fee, total = pricing.totals(line_totals)
    if total != pricing.money(expected_total):
        raise ConflictError("The total has changed since you reviewed your cart. Review your cart.")

    order = order_repository.add(OrderCreate(
        customer_id=customer_id,
        restaurant_id=restaurant.id,
        restaurant_name=restaurant.name,
        delivery_address=user.delivery_address,
        items=order_items,
        subtotal=float(subtotal),
        delivery_fee=float(delivery_fee),
        total=float(total),
    ))
    _clear_cart_or_undo_order(cart, order)
    return order