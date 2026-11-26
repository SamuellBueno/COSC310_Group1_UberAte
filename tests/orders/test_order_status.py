import pytest

from app.core.errors import ConflictError
from app.services.order_status import check_move


def test_normal_moves_are_allowed():
    check_move("placed", "preparing")
    check_move("preparing", "ready")
    check_move("ready", "out_for_delivery")
    check_move("out_for_delivery", "delivered")


def test_placed_and_preparing_can_be_cancelled():
    check_move("placed", "cancelled")
    check_move("preparing", "cancelled")


def test_cannot_skip_a_step():
    with pytest.raises(ConflictError):
        check_move("placed", "ready")


def test_cannot_go_backwards():
    with pytest.raises(ConflictError):
        check_move("ready", "preparing")


def test_ready_order_cannot_be_cancelled():
    with pytest.raises(ConflictError):
        check_move("ready", "cancelled")


def test_delivered_and_cancelled_are_final():
    with pytest.raises(ConflictError):
        check_move("delivered", "cancelled")
    with pytest.raises(ConflictError):
        check_move("cancelled", "preparing")