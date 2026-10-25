def line_total(qty, unit_price):
    return round(qty * unit_price, 2)


def invoice_total(lines, tax_rate):
    """lines is a list of (qty, unit_price) pairs; tax_rate like 0.08 for 8%."""
    subtotal = sum(line_total(q, p) for q, p in lines)
    return round(subtotal * (1 + tax_rate), 2)
