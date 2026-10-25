from .core import calc_total


def refund_amount(items, restocking_fee=0.0):
    return round(calc_total(items) * (1 - restocking_fee), 2)
