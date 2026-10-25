from export import to_csv


def test_quotes_doubled():
    assert to_csv([{"q": 'say "hi"'}], ["q"], header=False) == '"say ""hi"""\r\n'


def test_newline_quoted():
    assert to_csv([{"n": "a\nb"}], ["n"], header=False) == '"a\nb"\r\n'


def test_none_and_missing():
    assert to_csv([{"a": None}], ["a", "b"], header=False) == ",\r\n"


def test_header_flag():
    assert to_csv([{"a": 1}], ["a"], header=False) == "1\r\n"
    assert to_csv([{"a": 1}], ["a"]) == "a\r\n1\r\n"


def test_empty():
    assert to_csv([], ["a"], header=False) == ""
    assert to_csv([], ["a"]) == "a\r\n"


def test_booleans():
    assert to_csv([{"ok": True, "bad": False}], ["ok", "bad"], header=False) == "true,false\r\n"


def test_other_delimiter_and_header_quoting():
    out = to_csv([{"a;b": "x;y", "c": 2.5}], ["a;b", "c"], delimiter=";")
    assert out == '"a;b";c\r\n"x;y";2.5\r\n'
