`LRUCache` in `cache.py` is supposed to evict the least recently *used* key, but it evicts the oldest *inserted* key.

Expected behaviour:
- `get(key)` counts as a use and makes the key most recent.
- `put(key, value)` on an existing key updates the value and makes it most recent.
- `key in cache` must work, and must NOT count as a use.
- `capacity=0` is allowed; the cache then stores nothing.
- A negative capacity raises `ValueError`.
