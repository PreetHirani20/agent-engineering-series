from datetime import date, timedelta


def week_bounds(day: date):
    start = day - timedelta(days=day.weekday())
    return start, start + timedelta(days=6)


def label(day: date):
    start, end = week_bounds(day)
    return f"{start:%d %b} - {end:%d %b %Y}"
