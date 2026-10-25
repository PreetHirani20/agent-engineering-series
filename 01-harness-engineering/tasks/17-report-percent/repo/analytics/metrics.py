def conversion_rate(signups, visits):
    """Share of visits that signed up."""
    return signups / visits * 100


def bounce_rate(bounces, visits):
    """Share of visits that left after one page, as a fraction."""
    return bounces / visits


def avg_session(total_seconds, sessions):
    return total_seconds / sessions if sessions else 0.0
