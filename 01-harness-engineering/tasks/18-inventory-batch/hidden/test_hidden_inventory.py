import pytest
from inventory import Inventory, InventoryError


def test_error_is_exception_subclass():
    assert issubclass(InventoryError, Exception)


def test_all_or_nothing():
    inv = Inventory({"apple": 5, "pear": 1})
    with pytest.raises(InventoryError):
        inv.apply_orders([("apple", 2), ("pear", 3)])
    assert inv.stock == {"apple": 5, "pear": 1}


def test_same_sku_adds_up():
    inv = Inventory({"apple": 3})
    with pytest.raises(InventoryError):
        inv.apply_orders([("apple", 2), ("apple", 2)])
    assert inv.stock == {"apple": 3}
    inv.apply_orders([("apple", 1), ("apple", 2)])
    assert inv.stock == {"apple": 0}


def test_unknown_sku():
    inv = Inventory({"apple": 3})
    with pytest.raises(InventoryError):
        inv.apply_orders([("apple", 1), ("kiwi", 1)])
    assert inv.stock == {"apple": 3}


@pytest.mark.parametrize("bad", [0, -1, 1.5, "2"])
def test_bad_qty(bad):
    inv = Inventory({"apple": 3})
    with pytest.raises(ValueError):
        inv.apply_orders([("apple", 1), ("apple", bad)])
    assert inv.stock == {"apple": 3}
    with pytest.raises(ValueError):
        inv.restock("apple", bad)
    assert inv.stock == {"apple": 3}


def test_restock_ok():
    inv = Inventory()
    inv.restock("fig", 4)
    assert inv.available("fig") == 4
