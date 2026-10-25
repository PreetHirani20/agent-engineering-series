"""Pricing rules applied at checkout."""
from .constants import BULK_RATE, BULK_THRESHOLD


def bulk_discount(subtotal):
    """10% off orders at or above the bulk threshold."""
    if subtotal > BULK_THRESHOLD:
        return round(subtotal * BULK_RATE, 2)
    return 0.0
