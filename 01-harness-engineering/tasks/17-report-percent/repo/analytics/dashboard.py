from .formatting import format_pct
from .metrics import bounce_rate


def bounce_tile(stats):
    return {"title": "Bounce rate", "value": format_pct(bounce_rate(stats["bounces"], stats["visits"]))}
