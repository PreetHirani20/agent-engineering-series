import re

UNITS = {"h": 3600, "m": 60, "s": 1}


def parse_duration(text):
    """Parse strings like '1h30m' into seconds."""
    total = 0
    for value, unit in re.findall(r"(\d+)([hms])", text):
        total += int(value) * UNITS[unit]
    return total
