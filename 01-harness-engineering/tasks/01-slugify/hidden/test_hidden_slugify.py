from textutils import slugify


def test_accents():
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_strip_dashes():
    assert slugify("  --Hello--  ") == "hello"


def test_runs_collapse():
    assert slugify("a  &&  b") == "a-b"


def test_empty_and_symbols():
    assert slugify("") == ""
    assert slugify("!!!") == ""


def test_max_length():
    assert slugify("hello world again", max_length=11) == "hello-world"
    assert slugify("hello world", max_length=6) == "hello"
    assert slugify("hello world", max_length=None) == "hello-world"


def test_digits_kept():
    assert slugify("Top 10 Tips") == "top-10-tips"
