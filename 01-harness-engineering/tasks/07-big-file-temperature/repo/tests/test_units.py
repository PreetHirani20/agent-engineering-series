import pytest
import units


def test_celsius_to_fahrenheit():
    assert units.celsius_to_fahrenheit(100) == pytest.approx(212.0)
    assert units.celsius_to_fahrenheit(0) == pytest.approx(32.0)


def test_some_other_conversions():
    assert units.meters_to_feet(1) == pytest.approx(3.28083989501)
    assert units.gigabytes_to_megabytes(2) == pytest.approx(2000)
    assert units.convert(1, "hours", "minutes") == pytest.approx(60)
