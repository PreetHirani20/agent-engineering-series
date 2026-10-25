from datetime import date, timedelta


def days_between(start, end):
    """Every date from start to end, inclusive."""
    out = []
    d = start
    while d < end:
        out.append(d)
        d += timedelta(days=1)
    return out


def business_days(start, end, holidays=()):
    """Weekdays from start to end, inclusive, skipping holidays."""
    return [d for d in days_between(start, end) if d.weekday() < 5]


def next_monday(d):
    return d + timedelta(days=(7 - d.weekday()) % 7 or 7)
