from textutils import slugify, word_count


def test_basic_slug():
    assert slugify("Hello, World!") == "hello-world"


def test_word_count():
    assert word_count("a b  c") == 3
