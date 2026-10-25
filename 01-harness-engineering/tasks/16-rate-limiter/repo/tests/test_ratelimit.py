from ratelimit import TokenBucket


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_starts_full():
    clock = FakeClock()
    b = TokenBucket(rate=1, capacity=2, clock=clock)
    assert b.allow() and b.allow()
    assert not b.allow()
