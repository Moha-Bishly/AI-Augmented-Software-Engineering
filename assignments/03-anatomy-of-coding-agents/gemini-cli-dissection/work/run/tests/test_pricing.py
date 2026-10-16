import pytest

from shopcart.pricing import apply_discount, apply_tax, calculate_shipping


def test_apply_tax():
    assert apply_tax(1000) == 1080


def test_no_code_means_no_discount():
    assert apply_discount(1000, None) == 1000


def test_percent_discount():
    assert apply_discount(2000, "SAVE25") == 1500


def test_fixed_discount_never_negative():
    assert apply_discount(500, "TENOFF") == 0


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        apply_discount(1000, "BOGUS")


def test_calculate_shipping_empty_cart():
    assert calculate_shipping(0, 0) == 0


def test_calculate_shipping_below_threshold():
    assert calculate_shipping(4000, 4000) == 599


def test_calculate_shipping_at_threshold():
    assert calculate_shipping(5000, 5000) == 0


def test_calculate_shipping_above_threshold():
    assert calculate_shipping(6000, 6000) == 0


def test_calculate_shipping_free_after_discount():
    assert calculate_shipping(6000, 5400) == 0


def test_calculate_shipping_not_free_after_discount():
    assert calculate_shipping(5200, 4680) == 599
