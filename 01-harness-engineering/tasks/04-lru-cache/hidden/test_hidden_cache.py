import pytest
from cache import LRUCache


def test_put_existing_refreshes():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)
    c.put("c", 3)
    assert c.get("a") == 10
    assert c.get("b") is None


def test_contains_does_not_refresh():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c and "z" not in c
    c.put("c", 3)
    assert "a" not in c and "b" in c


def test_zero_capacity():
    c = LRUCache(0)
    c.put("a", 1)
    assert len(c) == 0 and c.get("a") is None


def test_negative_capacity():
    with pytest.raises(ValueError):
        LRUCache(-1)


def test_default():
    assert LRUCache(1).get("missing", 5) == 5
