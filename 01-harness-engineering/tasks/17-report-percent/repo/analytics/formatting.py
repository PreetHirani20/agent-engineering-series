def format_pct(fraction, digits=1):
    """Format a fraction (0.123) as a percentage string ('12.3%')."""
    return f"{fraction * 100:.{digits}f}%"


def format_count(n):
    return f"{n:,}"


def format_duration(seconds):
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m {secs:02d}s"
