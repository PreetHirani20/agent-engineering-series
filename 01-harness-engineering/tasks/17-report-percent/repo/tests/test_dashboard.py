from analytics.dashboard import bounce_tile


def test_bounce_tile():
    assert bounce_tile({"bounces": 250, "visits": 1000}) == {"title": "Bounce rate", "value": "25.0%"}
