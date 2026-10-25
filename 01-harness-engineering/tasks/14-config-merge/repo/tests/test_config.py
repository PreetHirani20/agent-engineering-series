from config import load_layers, merge


def test_nested_merge():
    base = {"db": {"host": "a", "port": 1}, "debug": False}
    assert merge(base, {"db": {"port": 2}}) == {"db": {"host": "a", "port": 2}, "debug": False}


def test_layers():
    assert load_layers({"a": 1}, {"b": 2}, {"a": 3}) == {"a": 3, "b": 2}
