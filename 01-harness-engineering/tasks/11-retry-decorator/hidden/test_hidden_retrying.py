import pytest
from retrying import retry


def test_times_validation():
    with pytest.raises(ValueError):
        retry(times=0)


def test_other_exceptions_not_retried():
    calls, waits = [], []

    @retry(times=5, exceptions=(ConnectionError,), sleep=waits.append)
    def broken():
        calls.append(1)
        raise KeyError("x")

    with pytest.raises(KeyError):
        broken()
    assert len(calls) == 1 and waits == []


def test_delays_and_no_final_sleep():
    waits = []

    @retry(times=4, exceptions=(ValueError,), delays=[0.1, 0.5], sleep=waits.append)
    def bad():
        raise ValueError("no")

    with pytest.raises(ValueError):
        bad()
    assert waits == [0.1, 0.5, 0.5]


def test_default_delay():
    waits = []

    @retry(times=3, sleep=waits.append)
    def bad():
        raise RuntimeError("no")

    with pytest.raises(RuntimeError):
        bad()
    assert waits == [1, 1]


def test_recovers():
    state = {"n": 0}

    @retry(times=3, exceptions=(TimeoutError,), sleep=lambda s: None)
    def eventually(x):
        state["n"] += 1
        if state["n"] < 3:
            raise TimeoutError()
        return x * 2

    assert eventually(21) == 42


def test_wraps():
    @retry()
    def documented():
        """Docs."""

    assert documented.__name__ == "documented" and documented.__doc__ == "Docs."
