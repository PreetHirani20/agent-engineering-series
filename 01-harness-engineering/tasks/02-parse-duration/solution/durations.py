import re

UNITS = {"d": 86400, "h": 3600, "m": 60, "s": 1}
PART = re.compile(r"\s*(\d+)\s*([dhms])\s*", re.IGNORECASE)


def parse_duration(text):
    """Parse strings like '1h30m' into seconds."""
    if not re.fullmatch(r"(?:\s*\d+\s*[dhms]\s*)+", text, re.IGNORECASE):
        raise ValueError(f"invalid duration: {text!r}")
    return sum(int(v) * UNITS[u.lower()] for v, u in PART.findall(text))
