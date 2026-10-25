The `retry` decorator in `retrying.py` hides failures: when every attempt fails it returns `None` instead of raising. Please fix it so that:

1. `times` is the total number of attempts (`times=3` means at most 3 calls). `times < 1` raises `ValueError` when the decorator is created.
2. Only exceptions listed in `exceptions` trigger a retry. Any other exception propagates immediately, without sleeping.
3. When all attempts fail, the last exception is re-raised.
4. `delays` is an optional list of seconds to wait before each retry: with `delays=[0.1, 0.5]` it waits 0.1 before the 2nd attempt and 0.5 before the 3rd. If the list is shorter than needed, keep using its last value. With `delays=None`, wait 1 second before each retry.
5. Never sleep after the final failed attempt (right now it sleeps after every failure).
6. The wrapped function keeps its `__name__` and `__doc__`.

`sleep` is injectable (it defaults to `time.sleep`) so tests can record the waits.
