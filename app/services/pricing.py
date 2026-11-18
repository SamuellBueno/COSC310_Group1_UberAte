from decimal import Decimal, ROUND_HALF_UP

DELIVERY_FEE = Decimal("3.99")
CENT = Decimal("0.01")

def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def line_total(unit_price: Decimal | int | float | str, quantity: int) -> Decimal:
    return money(Decimal(str(unit_price)) * quantity)


def totals(line_totals: list[Decimal]) -> tuple[Decimal, Decimal, Decimal]:
    if not line_totals:
        return Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
    subtotal = money(sum(line_totals, Decimal("0.00")))
    delivery_fee = DELIVERY_FEE
    total = money(subtotal + delivery_fee)
    return subtotal, delivery_fee, total