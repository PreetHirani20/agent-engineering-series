from .core import calc_total


def invoice_amount(invoice):
    return calc_total(invoice["items"], invoice.get("discount", 0.0))


def invoice_summary(invoice):
    total = calc_total(invoice["items"], invoice.get("discount", 0.0))
    return f"Invoice {invoice['id']}: {total:.2f}"
