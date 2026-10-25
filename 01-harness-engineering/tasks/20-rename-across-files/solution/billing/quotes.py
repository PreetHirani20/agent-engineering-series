from . import core


def quote_amount(items, discount=0.0):
    return core.calculate_total(items, discount)


def compare_quotes(a, b):
    """How much more quote a costs than quote b."""
    return round(core.calculate_total(a) - core.calculate_total(b), 2)
