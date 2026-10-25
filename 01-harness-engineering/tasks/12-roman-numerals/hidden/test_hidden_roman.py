import pytest
from roman import from_roman, to_roman


@pytest.mark.parametrize("n,s", [(9, "IX"), (14, "XIV"), (40, "XL"), (90, "XC"), (400, "CD"),
                                 (900, "CM"), (1994, "MCMXCIV"), (3999, "MMMCMXCIX")])
def test_subtractive(n, s):
    assert to_roman(n) == s
    assert from_roman(s) == n


@pytest.mark.parametrize("n", [0, -1, 4000])
def test_range(n):
    with pytest.raises(ValueError):
        to_roman(n)


def test_lowercase():
    assert from_roman("xiv") == 14


@pytest.mark.parametrize("bad", ["", "IIII", "IC", "VX", "MMMM", "ABC", "XM", "IIV"])
def test_invalid(bad):
    with pytest.raises(ValueError):
        from_roman(bad)


def test_round_trip():
    for n in range(1, 4000):
        assert from_roman(to_roman(n)) == n
