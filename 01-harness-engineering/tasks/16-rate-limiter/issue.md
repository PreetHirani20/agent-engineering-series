`TokenBucket` in `ratelimit.py` lets through far fewer requests than configured. Fix it so that:

- A new bucket starts full (`capacity` tokens).
- Tokens refill continuously at `rate` tokens per second, including fractions of a second: after 0.5 s at `rate=2`, one more token is available.
- The bucket never holds more than `capacity` tokens, however long it sits idle.
- `allow(cost=1)` takes `cost` tokens and returns `True` if enough are available, otherwise returns `False` and takes nothing.
- `allow()` with `cost <= 0` or `cost > capacity` raises `ValueError`.
- The constructor raises `ValueError` if `rate <= 0` or `capacity <= 0`.

The clock is injectable for tests (`clock=time.monotonic` by default).
