import re
from collections import Counter

LINE = re.compile(
    r'(?P<ip>[0-9a-fA-F:.]+) - (?P<user>[\w.\-]+) \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/[\d.]+" (?P<status>\d{3}) (?P<size>\d+|-)'
)


def parse_line(line):
    """Parse one access-log line into a dict."""
    m = LINE.fullmatch(line.rstrip("\r\n"))
    if not m:
        return None
    entry = m.groupdict()
    entry["user"] = None if entry["user"] == "-" else entry["user"]
    entry["status"] = int(entry["status"])
    entry["size"] = 0 if entry["size"] == "-" else int(entry["size"])
    return entry


def status_counts(path):
    """Count responses per HTTP status code."""
    counts = Counter()
    with open(path, encoding="utf-8") as f:
        for line in f:
            entry = parse_line(line)
            if entry:
                counts[entry["status"]] += 1
    return counts
