from .core import calc_total
from .invoices import invoice_amount


def revenue(invoices):
    return round(sum(invoice_amount(i) for i in invoices), 2)


def average_order(orders):
    if not orders:
        return 0.0
    return round(sum(calc_total(o) for o in orders) / len(orders), 2)
