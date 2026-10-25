import re
from functools import cmp_to_key

VERSION = re.compile(r"v?(\d+(?:\.\d+)*)(?:-([A-Za-z]+)(\d*))?")


def _parse(v):
    m = VERSION.fullmatch(v.strip())
    if not m:
        raise ValueError(f"invalid version: {v!r}")
    nums = [int(x) for x in m.group(1).split(".")]
    pre = (m.group(2).lower(), int(m.group(3) or 0)) if m.group(2) else None
    return nums, pre


def _cmp(x, y):
    return (x > y) - (x < y)


def compare(a, b):
    """Return -1 if a < b, 0 if they are equal, 1 if a > b."""
    (na, pa), (nb, pb) = _parse(a), _parse(b)
    width = max(len(na), len(nb))
    na, nb = na + [0] * (width - len(na)), nb + [0] * (width - len(nb))
    if na != nb:
        return _cmp(na, nb)
    if pa is None or pb is None:
        return _cmp(pa is None, pb is None)
    return _cmp(pa, pb)


def latest(versions):
    """The newest version in the list."""
    return max(versions, key=cmp_to_key(compare))
