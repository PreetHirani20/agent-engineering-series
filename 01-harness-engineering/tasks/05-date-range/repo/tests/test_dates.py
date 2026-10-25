from datetime import date

from dates import days_between, next_monday


def test_inclusive_across_month():
    days = days_between(date(2024, 1, 30), date(2024, 2, 2))
    assert days == [date(2024, 1, 30), date(2024, 1, 31), date(2024, 2, 1), date(2024, 2, 2)]


def test_next_monday():
    assert next_monday(date(2024, 3, 6)) == date(2024, 3, 11)
    assert next_monday(date(2024, 3, 11)) == date(2024, 3, 18)
