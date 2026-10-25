from .constants import TAX_RATE


def add_tax(amount):
    return round(amount * (1 + TAX_RATE), 2)


def tax_on(amount):
    return round(amount * TAX_RATE, 2)
