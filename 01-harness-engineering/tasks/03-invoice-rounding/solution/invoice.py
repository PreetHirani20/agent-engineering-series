from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _d(x):
    return Decimal(str(x)) if isinstance(x, float) else Decimal(x)


def line_total(qty, unit_price):
    return (_d(qty) * _d(unit_price)).quantize(CENT, rounding=ROUND_HALF_UP)


def invoice_total(lines, tax_rate):
    """lines is a list of (qty, unit_price) pairs; tax_rate like 0.08 for 8%."""
    subtotal = sum((line_total(q, p) for q, p in lines), Decimal("0"))
    return (subtotal * (1 + _d(tax_rate))).quantize(CENT, rounding=ROUND_HALF_UP)
