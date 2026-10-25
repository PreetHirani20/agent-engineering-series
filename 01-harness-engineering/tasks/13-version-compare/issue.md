`versions.py` compares version strings alphabetically, so `compare("1.10.0", "1.9.0")` says 1.10.0 is older, and `latest(["1.9.0", "1.10.0"])` returns `"1.9.0"`.

`compare(a, b)` returns -1, 0 or 1. Rules:
- Compare dot-separated parts as numbers: `1.10.0` > `1.9.0`.
- Missing parts count as 0: `"1.2" == "1.2.0"`, `"1" == "1.0.0"`.
- An optional leading `v` is ignored: `"v1.2.3" == "1.2.3"`.
- A pre-release comes after `-` and is lower than the same version without one: `1.0.0-rc1 < 1.0.0`.
- Two pre-releases compare by their letters alphabetically, then by their number: `alpha < beta < rc`, and `rc2 < rc10`.
- Invalid strings raise `ValueError`: `""`, `"1..2"`, `"1.x"`, `"abc"`, `"1.0-"`.

`latest(versions)` must use these rules too.
