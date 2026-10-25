class Inventory:
    def __init__(self, stock=None):
        self.stock = dict(stock or {})

    def apply_orders(self, orders):
        """Apply a batch of (sku, qty) orders, reducing stock."""
        for sku, qty in orders:
            self.stock[sku] -= qty

    def restock(self, sku, qty):
        self.stock[sku] = self.stock.get(sku, 0) + qty

    def available(self, sku):
        return self.stock.get(sku, 0)
