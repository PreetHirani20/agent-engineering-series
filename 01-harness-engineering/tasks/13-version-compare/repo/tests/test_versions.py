from versions import compare


def test_equal():
    assert compare("1.2.3", "1.2.3") == 0


def test_numeric_parts():
    assert compare("1.10.0", "1.9.0") == 1
    assert compare("1.9.0", "1.10.0") == -1
