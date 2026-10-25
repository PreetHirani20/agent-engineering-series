from analytics.formatting import format_count, format_duration, format_pct


def test_format_pct():
    assert format_pct(0.123) == "12.3%"
    assert format_pct(0.5, digits=0) == "50%"


def test_other_formats():
    assert format_count(1234567) == "1,234,567"
    assert format_duration(125) == "2m 05s"
