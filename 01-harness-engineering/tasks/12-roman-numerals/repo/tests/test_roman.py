from roman import from_roman, to_roman


def test_additive():
    assert to_roman(2026) == "MMXXVI"
    assert from_roman("MMXXVI") == 2026


def test_four():
    assert to_roman(4) == "IV"
