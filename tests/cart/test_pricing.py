from decimal import Decimal

from app.services import pricing


def test_money_rounds_half_up():
    assert pricing.money("10.005") == Decimal("10.01")
    assert pricing.money("10.004") == Decimal("10.00")


def test_line_total_multiplies_exact_decimals():
    assert pricing.line_total(0.1, 3) == Decimal("0.30")
    assert pricing.line_total(14.5, 2) == Decimal("29.00")


def test_totals_empty_cart_has_zero_delivery_fee():
    subtotal, delivery_fee, total = pricing.totals([])
    assert subtotal == Decimal("0.00")
    assert delivery_fee == Decimal("0.00")
    assert total == Decimal("0.00")


def test_totals_non_empty_cart_adds_delivery_fee():
    subtotal, delivery_fee, total = pricing.totals([Decimal("14.00"), Decimal("9.50")])
    assert subtotal == Decimal("23.50")
    assert delivery_fee == Decimal("3.99")
    assert total == Decimal("27.49")