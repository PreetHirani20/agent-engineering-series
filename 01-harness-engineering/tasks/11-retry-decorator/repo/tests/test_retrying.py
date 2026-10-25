import pytest
from retrying import retry


def test_succeeds_first_time():
    @retry(times=3, sleep=lambda s: None)
    def ok():
        return 42

    assert ok() == 42


def test_reraises_after_last_attempt():
    calls = []

    @retry(times=3, exceptions=(ConnectionError,), sleep=lambda s: None)
    def flaky():
        calls.append(1)
        raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        flaky()
    assert len(calls) == 3
