import pytest
from durations import parse_duration


def test_spaces_case_order():
    assert parse_duration("1h 30m") == 5400
    assert parse_duration("1H30M") == 5400
    assert parse_duration("30m1h") == 5400
    assert parse_duration("1d2h3m4s") == 93784
    assert parse_duration("45s") == 45


@pytest.mark.parametrize("bad", ["", "   ", "5", "10x", "1h and 30m", "abc", "h"])
def test_invalid(bad):
    with pytest.raises(ValueError):
        parse_duration(bad)
