from .core import calc_total as _total


def monthly_charge(plan_items, months=1):
    return round(_total(plan_items) * months, 2)


def annual_charge(plan_items):
    """Twelve months for the price of eleven."""
    return round(_total(plan_items) * 11, 2)
