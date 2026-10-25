from wrapping import wrap


def test_breaks_at_spaces():
    assert wrap("the quick brown fox", 10) == "the quick\nbrown fox"
