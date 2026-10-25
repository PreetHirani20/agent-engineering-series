from log_parser import parse_line


def test_normal_line():
    e = parse_line('203.0.113.9 - alice [10/Oct/2026:13:55:36 +0000] "GET /login HTTP/1.1" 200 5120')
    assert e["ip"] == "203.0.113.9" and e["user"] == "alice"
    assert e["status"] == 200 and e["size"] == 5120 and e["path"] == "/login"


def test_anonymous_user():
    e = parse_line('203.0.113.9 - - [10/Oct/2026:13:55:36 +0000] "GET / HTTP/1.1" 200 512')
    assert e["user"] is None
