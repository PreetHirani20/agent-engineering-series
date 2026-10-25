from log_parser import parse_line, status_counts


def test_size_dash():
    e = parse_line('203.0.113.9 - bob [10/Oct/2026:13:55:36 +0000] "GET /x HTTP/1.1" 304 -')
    assert e["size"] == 0 and e["status"] == 304


def test_ipv6_and_usernames():
    e = parse_line('2001:db8:1f::a3 - j.doe [10/Oct/2026:13:55:36 +0000] "POST /api/orders HTTP/1.1" 201 77')
    assert e["ip"] == "2001:db8:1f::a3" and e["user"] == "j.doe"
    assert parse_line('10.0.0.2 - svc-backup [10/Oct/2026:13:55:36 +0000] "PUT /a HTTP/1.1" 200 1')["user"] == "svc-backup"


def test_bad_lines_return_none():
    for bad in ["", "\n", "-- log rotated --", '10.0.0.1 - - [10/Oct/2026:13:55:36 +0000] "GET /api/ord']:
        assert parse_line(bad) is None


def test_status_counts_on_real_log():
    counts = status_counts("data/access.log")
    assert dict(counts) == {200: 2562, 201: 160, 204: 175, 301: 181, 302: 124, 304: 151, 400: 69, 401: 77, 403: 77, 404: 263, 429: 85, 500: 77, 502: 81, 503: 78}
