from .core import calculate_total


def invoice_amount(invoice):
    return calculate_total(invoice["items"], invoice.get("discount", 0.0))


def invoice_summary(invoice):
    total = calculate_total(invoice["items"], invoice.get("discount", 0.0))
    return f"Invoice {invoice['id']}: {total:.2f}"
