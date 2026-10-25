`Inventory.apply_orders()` in `inventory.py` lets stock go negative, and when a batch fails halfway the first orders have already been applied.

Please:
- Add an exception class `InventoryError(Exception)` to `inventory.py`.
- Make `apply_orders(orders)` all-or-nothing. `orders` is a list of `(sku, qty)` pairs. If any order cannot be filled, raise `InventoryError` and leave the stock exactly as it was before the call.
- An order cannot be filled if the SKU is unknown, or if the total quantity for that SKU across the whole batch is more than the stock (two orders for the same SKU in one batch add up).
- `qty` must be a positive `int`; otherwise raise `ValueError` (and also leave the stock unchanged).
- `restock(sku, qty)` must also reject a `qty` that is not a positive `int` with `ValueError`.
