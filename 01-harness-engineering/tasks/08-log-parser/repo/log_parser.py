import re
from collections import Counter

LINE = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) - (?P<user>\w+) \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/[\d.]+" (?P<status>\d{3}) (?P<size>\d+)'
)


def parse_line(line):
    """Parse one access-log line into a dict."""
    m = LINE.match(line)
    entry = m.groupdict()
    entry["status"] = int(entry["status"])
    entry["size"] = int(entry["size"])
    return entry


def status_counts(path):
    """Count responses per HTTP status code."""
    counts = Counter()
    with open(path, encoding="utf-8") as f:
        for line in f:
            counts[parse_line(line)["status"]] += 1
    return counts
