from . import core


def quote_amount(items, discount=0.0):
    return core.calc_total(items, discount)


def compare_quotes(a, b):
    """How much more quote a costs than quote b."""
    return round(core.calc_total(a) - core.calc_total(b), 2)
