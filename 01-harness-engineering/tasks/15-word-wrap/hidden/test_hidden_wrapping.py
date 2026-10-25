import pytest
from wrapping import wrap


def test_exact_width():
    assert wrap("abc def", 7) == "abc def"
    assert wrap("abc def", 6) == "abc\ndef"


def test_long_word():
    assert wrap("abcdefghij", 4) == "abcd\nefgh\nij"


def test_whitespace_collapse():
    assert wrap("  a\t\tb   c  ", 80) == "a b c"


def test_paragraphs():
    assert wrap("one two\nthree\n\n\n  four  ", 20) == "one two three\n\nfour"
    assert wrap("a\n \t \nb", 5) == "a\n\nb"


def test_empty_and_invalid():
    assert wrap("", 10) == ""
    assert wrap("   \n\n  ", 10) == ""
    with pytest.raises(ValueError):
        wrap("abc", 0)


def test_no_line_too_long():
    text = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor"
    out = wrap(text, 12)
    assert all(len(line) <= 12 for line in out.split("\n"))
    assert out.split() == text.split()
