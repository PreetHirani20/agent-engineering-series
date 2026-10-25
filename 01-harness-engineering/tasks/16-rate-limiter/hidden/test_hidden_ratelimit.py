import pytest
from ratelimit import TokenBucket


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_fractional_refill():
    clock = FakeClock()
    b = TokenBucket(rate=2, capacity=2, clock=clock)
    assert b.allow(2)
    assert not b.allow()
    clock.now = 0.5
    assert b.allow()
    assert not b.allow()
    clock.now = 0.75
    assert not b.allow()
    clock.now = 1.0
    assert b.allow()


def test_capped_at_capacity():
    clock = FakeClock()
    b = TokenBucket(rate=10, capacity=3, clock=clock)
    clock.now = 100
    assert b.allow(3)
    assert not b.allow()


def test_failed_allow_takes_nothing():
    clock = FakeClock()
    b = TokenBucket(rate=1, capacity=3, clock=clock)
    assert b.allow(2)
    assert not b.allow(2)
    assert b.allow(1)


def test_cost_validation():
    b = TokenBucket(rate=1, capacity=3, clock=FakeClock())
    for bad in (0, -1, 4):
        with pytest.raises(ValueError):
            b.allow(bad)


def test_constructor_validation():
    for rate, cap in ((0, 1), (-1, 1), (1, 0), (1, -5)):
        with pytest.raises(ValueError):
            TokenBucket(rate=rate, capacity=cap, clock=FakeClock())
