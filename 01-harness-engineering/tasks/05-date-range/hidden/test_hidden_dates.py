from datetime import date

import pytest
from dates import business_days, days_between


def test_single_day():
    assert days_between(date(2024, 2, 29), date(2024, 2, 29)) == [date(2024, 2, 29)]


def test_business_days_weekend_and_holidays():
    # Fri 2024-03-29 .. Tue 2024-04-02, with Monday 1 April a holiday
    got = business_days(date(2024, 3, 29), date(2024, 4, 2), holidays=[date(2024, 4, 1)])
    assert got == [date(2024, 3, 29), date(2024, 4, 2)]


def test_business_days_holidays_any_iterable():
    got = business_days(date(2024, 4, 1), date(2024, 4, 3), holidays={date(2024, 4, 2)})
    assert got == [date(2024, 4, 1), date(2024, 4, 3)]


def test_business_days_inclusive_end():
    assert business_days(date(2024, 4, 1), date(2024, 4, 1)) == [date(2024, 4, 1)]


def test_reversed_raises():
    with pytest.raises(ValueError):
        days_between(date(2024, 2, 2), date(2024, 1, 30))
    with pytest.raises(ValueError):
        business_days(date(2024, 2, 2), date(2024, 1, 30))
