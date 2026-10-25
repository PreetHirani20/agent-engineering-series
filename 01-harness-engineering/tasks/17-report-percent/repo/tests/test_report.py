from analytics.report import weekly_report

WEEK = {"visits": 1000, "signups": 450, "bounces": 300, "session_seconds": 125000, "sessions": 1000}


def test_conversion_line():
    assert "Conversion: 45.0%" in weekly_report(WEEK)
