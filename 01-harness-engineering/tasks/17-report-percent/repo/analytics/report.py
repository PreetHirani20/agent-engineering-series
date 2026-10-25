from .formatting import format_count, format_duration, format_pct
from .metrics import avg_session, bounce_rate, conversion_rate


def weekly_report(stats):
    """stats: dict with visits, signups, bounces, session_seconds, sessions."""
    lines = [
        f"Visits: {format_count(stats['visits'])}",
        f"Conversion: {format_pct(conversion_rate(stats['signups'], stats['visits']))}",
        f"Bounce rate: {format_pct(bounce_rate(stats['bounces'], stats['visits']))}",
        f"Avg session: {format_duration(avg_session(stats['session_seconds'], stats['sessions']))}",
    ]
    return "\n".join(lines)
