"""Old pricing rules from the 2021 storefront. Not used by the cart any more; kept for the reporting job."""


def bulk_discount_v1(subtotal, threshold=100, rate=0.05):
    if subtotal >= threshold:
        return round(subtotal * rate, 2)
    return 0.0


def loyalty_discount(years):
    return min(years, 5) * 0.01
