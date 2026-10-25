import pytest
from versions import compare, latest


def test_missing_parts_and_v():
    assert compare("1.2", "1.2.0") == 0
    assert compare("1", "1.0.0") == 0
    assert compare("v1.2.3", "1.2.3") == 0
    assert compare("2.0", "1.99.99") == 1


def test_prerelease():
    assert compare("1.0.0-rc1", "1.0.0") == -1
    assert compare("1.0.0", "1.0.0-rc1") == 1
    assert compare("1.0.0-alpha", "1.0.0-beta") == -1
    assert compare("1.0.0-beta2", "1.0.0-rc1") == -1
    assert compare("1.0.0-rc2", "1.0.0-rc10") == -1
    assert compare("1.0.1-alpha", "1.0.0") == 1


@pytest.mark.parametrize("bad", ["", "1..2", "1.x", "abc", "1.0-"])
def test_invalid(bad):
    with pytest.raises(ValueError):
        compare(bad, "1.0.0")


def test_latest():
    assert latest(["1.9.0", "1.10.0", "1.10.0-rc1"]) == "1.10.0"
    assert latest(["v2.0.0-beta", "1.99"]) == "v2.0.0-beta"
