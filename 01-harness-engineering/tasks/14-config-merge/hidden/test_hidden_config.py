from config import load_layers, merge


def test_lists_replaced():
    assert merge({"hosts": ["a", "b"]}, {"hosts": ["c"]}) == {"hosts": ["c"]}


def test_none_deletes():
    assert merge({"a": 1, "b": {"c": 1, "d": 2}}, {"a": None, "b": {"d": None}}) == {"b": {"c": 1}}
    assert merge({"a": 1}, {"zzz": None}) == {"a": 1}


def test_type_mismatch():
    assert merge({"a": {"x": 1}}, {"a": 5}) == {"a": 5}
    assert merge({"a": 5}, {"a": {"x": 1}}) == {"a": {"x": 1}}


def test_inputs_untouched_and_independent():
    base = {"db": {"host": "a", "opts": [1]}, "keep": {"k": 1}}
    over = {"db": {"port": 2}, "new": {"n": [1]}}
    result = merge(base, over)
    assert base == {"db": {"host": "a", "opts": [1]}, "keep": {"k": 1}}
    assert over == {"db": {"port": 2}, "new": {"n": [1]}}
    result["db"]["opts"].append(2)
    result["keep"]["k"] = 99
    result["new"]["n"].append(2)
    assert base["db"]["opts"] == [1] and base["keep"]["k"] == 1 and over["new"]["n"] == [1]


def test_layers_do_not_leak():
    defaults = {"log": {"level": "info"}}
    load_layers(defaults, {"log": {"level": "debug"}})
    assert defaults == {"log": {"level": "info"}}
