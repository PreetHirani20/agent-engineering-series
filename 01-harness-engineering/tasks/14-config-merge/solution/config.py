import copy
from functools import reduce


def merge(base, override):
    """Layer `override` on top of `base`."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_layers(*layers):
    """Merge config layers left to right (later layers win)."""
    return reduce(merge, layers, {})
