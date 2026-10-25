from .catalog import get_price
from .rules import bulk_discount
from .tax import add_tax


class Cart:
    def __init__(self, items=None):
        self.items = list(items or [])  # (sku, qty) pairs

    def add(self, sku, qty=1):
        self.items.append((sku, qty))

    def subtotal(self):
        return round(sum(get_price(sku) * qty for sku, qty in self.items), 2)

    def discount(self):
        return bulk_discount(self.subtotal())

    def total(self):
        taxed = add_tax(self.subtotal())
        return round(taxed - self.discount(), 2)
