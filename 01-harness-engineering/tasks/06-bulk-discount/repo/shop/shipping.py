from .catalog import get_weight
from .constants import FLAT_SHIPPING, FREE_SHIPPING_OVER


def shipping_cost(items, subtotal):
    if subtotal >= FREE_SHIPPING_OVER:
        return 0.0
    weight = sum(get_weight(sku) * qty for sku, qty in items)
    return FLAT_SHIPPING if weight < 5 else FLAT_SHIPPING * 2
