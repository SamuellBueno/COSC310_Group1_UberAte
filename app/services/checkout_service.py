from app.repositories import cart_repository, menu_item_repository, order_repository, restaurant_repository, user_repository
from app.core.errors import BusinessRuleError, ConflictError, PermissionDeniedError
from app.schemas.order import Order, OrderCreate, OrderItem
from app.services import pricing

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

    order_items = []
    line_totals = []
    for line in cart.items:
        item = menu_item_repository.get_by_id(line.menu_item_id)
        if item is None or not item.active or not item.available or item.restaurant_id != cart.restaurant_id:
            raise BusinessRuleError("An item in your cart is no longer available. Review your cart.")
        unit_price = pricing.money(item.price)
        line_totals.append(pricing.line_total(unit_price, line.quantity))
        order_items.append(OrderItem(menu_item_id=item.id, name=item.name, unit_price=float(unit_price), quantity=line.quantity))

    subtotal, delivery_fee, total = pricing.totals(line_totals)
    if total != pricing.money(expected_total):
        raise ConflictError("The total has changed since you reviewed your cart. Review your cart.")

    order = order_repository.add(OrderCreate(
        customer_id=customer_id,
        restaurant_id=restaurant.id,
        restaurant_name=restaurant.name,
        items=order_items,
        total=float(total),
    ))
    # clear the cart after the order is saved
    # if clear fails undo the order
    try:
        cart_repository.save(cart.model_copy(update={"items": [], "restaurant_id": None}))
    except Exception:
        order_repository.delete(order.id)
        raise
    return order