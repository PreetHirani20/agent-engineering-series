from collections import Counter


class InventoryError(Exception):
    """An order batch could not be filled."""


def _check_qty(qty):
    if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
        raise ValueError(f"quantity must be a positive int, got {qty!r}")


class Inventory:
    def __init__(self, stock=None):
        self.stock = dict(stock or {})

    def apply_orders(self, orders):
        """Apply a batch of (sku, qty) orders, reducing stock."""
        needed = Counter()
        for sku, qty in orders:
            _check_qty(qty)
            needed[sku] += qty
        for sku, qty in needed.items():
            if sku not in self.stock:
                raise InventoryError(f"unknown sku {sku!r}")
            if qty > self.stock[sku]:
                raise InventoryError(f"not enough {sku!r}: need {qty}, have {self.stock[sku]}")
        for sku, qty in needed.items():
            self.stock[sku] -= qty

    def restock(self, sku, qty):
        _check_qty(qty)
        self.stock[sku] = self.stock.get(sku, 0) + qty

    def available(self, sku):
        return self.stock.get(sku, 0)
