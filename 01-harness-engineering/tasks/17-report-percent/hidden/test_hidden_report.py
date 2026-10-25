from analytics.dashboard import bounce_tile
from analytics.formatting import format_pct
from analytics.report import weekly_report

WEEK = {"visits": 1000, "signups": 450, "bounces": 300, "session_seconds": 125000, "sessions": 1000}
EMPTY = {"visits": 0, "signups": 0, "bounces": 0, "session_seconds": 0, "sessions": 0}


def test_full_report():
    assert weekly_report(WEEK) == "Visits: 1,000\nConversion: 45.0%\nBounce rate: 30.0%\nAvg session: 2m 05s"


def test_zero_visits():
    text = weekly_report(EMPTY)
    assert "Conversion: 0.0%" in text and "Bounce rate: 0.0%" in text


def test_shared_helpers_unchanged():
    assert format_pct(0.123) == "12.3%"
    assert bounce_tile({"bounces": 1, "visits": 8}) == {"title": "Bounce rate", "value": "12.5%"}
