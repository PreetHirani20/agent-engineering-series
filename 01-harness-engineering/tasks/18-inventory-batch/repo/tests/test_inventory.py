import pytest
from inventory import Inventory, InventoryError


def test_simple_batch():
    inv = Inventory({"apple": 5, "pear": 2})
    inv.apply_orders([("apple", 2), ("pear", 1)])
    assert inv.stock == {"apple": 3, "pear": 1}


def test_cannot_go_negative():
    inv = Inventory({"apple": 1})
    with pytest.raises(InventoryError):
        inv.apply_orders([("apple", 2)])
