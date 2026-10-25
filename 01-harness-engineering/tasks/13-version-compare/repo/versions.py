def compare(a, b):
    """Return -1 if a < b, 0 if they are equal, 1 if a > b."""
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def latest(versions):
    """The newest version in the list."""
    return max(versions)
