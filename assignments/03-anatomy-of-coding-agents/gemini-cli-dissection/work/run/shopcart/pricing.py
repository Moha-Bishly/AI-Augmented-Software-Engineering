"""Pricing rules: discounts and tax. All amounts are integer cents."""
from __future__ import annotations

TAX_RATE = 0.08
SHIPPING_FEE = 599
FREE_SHIPPING_THRESHOLD = 5000

# code -> (kind, value). "percent" values are whole percents; "fixed" values are cents.
DISCOUNT_CODES = {
    "SAVE10": ("percent", 10),
    "SAVE25": ("percent", 25),
    "TENOFF": ("fixed", 1000),
}


def validate_code(code: str) -> None:
    if code not in DISCOUNT_CODES:
        raise ValueError(f"invalid discount code: {code}")


def apply_discount(amount_cents: int, code: str | None) -> int:
    """Return the amount after applying a discount code. Never goes below zero."""
    if code is None:
        return amount_cents
    validate_code(code)
    kind, value = DISCOUNT_CODES[code]
    if kind == "percent":
        return round(amount_cents * (100 - value) / 100)
    return max(0, amount_cents - value)


def apply_tax(amount_cents: int) -> int:
    return round(amount_cents * (1 + TAX_RATE))


def calculate_shipping(subtotal_cents: int, discounted_cents: int) -> int:
    """Return shipping fee in cents. Free if subtotal after discount >= $50.00, or empty cart."""
    if subtotal_cents == 0:
        return 0
    if discounted_cents >= FREE_SHIPPING_THRESHOLD:
        return 0
    return SHIPPING_FEE


def final_total(subtotal_cents: int, code: str | None = None) -> int:
    """Total the customer pays for a given subtotal and optional discount code, including shipping."""
    # Discount is applied before tax, per store policy.
    discounted = apply_discount(subtotal_cents, code)
    taxed = apply_tax(discounted)
    shipping = calculate_shipping(subtotal_cents, discounted)
    return taxed + shipping
