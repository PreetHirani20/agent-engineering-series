from decimal import Decimal

from invoice import invoice_total, line_total


def test_returns_decimal_two_places():
    r = line_total(3, 0.1)
    assert isinstance(r, Decimal)
    assert r == Decimal("0.30") and str(r) == "0.30"


def test_input_types():
    assert line_total("2", "19.99") == Decimal("39.98")
    assert line_total(Decimal("1"), Decimal("1.005")) == Decimal("1.01")
    assert line_total(1, 1.005) == Decimal("1.01")


def test_tax_on_rounded_lines():
    # lines round to 39.98 and 5.01 -> 44.99; * 1.08 = 48.5892 -> 48.59
    total = invoice_total([(2, "19.99"), (1, "5.005")], 0.08)
    assert total == Decimal("48.59") and isinstance(total, Decimal)


def test_empty():
    t = invoice_total([], 0.2)
    assert t == Decimal("0.00") and str(t) == "0.00"
