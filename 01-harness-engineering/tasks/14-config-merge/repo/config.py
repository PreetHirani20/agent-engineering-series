from functools import reduce


def merge(base, override):
    """Layer `override` on top of `base`."""
    result = base
    result.update(override)
    return result


def load_layers(*layers):
    """Merge config layers left to right (later layers win)."""
    return reduce(merge, layers, {})
