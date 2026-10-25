from decimal import Decimal

from invoice import invoice_total, line_total


def test_half_up():
    assert line_total(1, 2.675) == Decimal("2.68")


def test_simple_invoice():
    assert invoice_total([(2, 5), (1, 10)], 0) == Decimal("20.00")
