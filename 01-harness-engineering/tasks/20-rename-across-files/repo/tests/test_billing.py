import billing
from billing.core import calc_total


def test_calc_total():
    assert calc_total([(2.50, 4), (1.00, 3)]) == 13.00
    assert calc_total([(10.0, 1)], discount=0.1) == 9.00


def test_new_name():
    assert billing.calculate_total([(2.50, 4)]) == 10.00
