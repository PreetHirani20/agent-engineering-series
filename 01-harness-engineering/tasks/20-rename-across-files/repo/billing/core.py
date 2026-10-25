def calc_total(items, discount=0.0):
    """Sum of price * qty over (price, qty) items, minus a fractional discount."""
    gross = sum(price * qty for price, qty in items)
    return round(gross * (1 - discount), 2)
