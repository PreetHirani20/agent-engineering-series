`status_counts("data/access.log")` crashes with `AttributeError: 'NoneType' object has no attribute 'groupdict'`. `data/access.log` is a real (anonymised) production log; it's large, around 400 KB.

`parse_line()` in `log_parser.py` must handle what real traffic looks like:
- A user field of `-` means anonymous: return `None` for `user`.
- A size of `-` means no body: return `0` for `size`.
- IPv6 client addresses such as `2001:db8:1f::a3` must parse.
- User names can contain dots, hyphens and underscores (`j.doe`, `svc-backup`, `carol_92`).
- Lines that are not in this format (blank lines, truncated lines, junk) return `None` instead of raising.

`status_counts(path)` must skip unparseable lines and return a `dict` (a `Counter` is fine) mapping status code (int) to count.
