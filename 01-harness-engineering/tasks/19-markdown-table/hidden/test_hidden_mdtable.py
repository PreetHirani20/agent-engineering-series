from mdtable import to_markdown


def test_none_and_bool_and_newline():
    rows = [{"ok": True, "n": None, "t": "x\ny"}, {"ok": False, "n": 7, "t": "z"}]
    assert to_markdown(rows) == (
        "| ok    |   n | t   |\n"
        "| ----- | --: | --- |\n"
        "| True  |     | x y |\n"
        "| False |   7 | z   |"
    )


def test_explicit_columns_order_and_missing():
    rows = [{"b": "x", "a": 1}]
    assert to_markdown(rows, columns=["a", "c", "b"]) == (
        "|   a | c   | b   |\n"
        "| --: | --- | --- |\n"
        "|   1 |     | x   |"
    )


def test_empty():
    assert to_markdown([]) == ""
    assert to_markdown([], columns=["id", "title"]) == "| id  | title |\n| --- | ----- |"


def test_union_first_seen_order():
    rows = [{"z": "1"}, {"a": "2", "z": "3"}]
    assert to_markdown(rows).splitlines()[0] == "| z   | a   |"
