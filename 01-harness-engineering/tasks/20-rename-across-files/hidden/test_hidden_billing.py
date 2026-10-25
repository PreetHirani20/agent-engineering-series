import warnings
from pathlib import Path

import pytest

import billing
from billing import invoices, quotes, refunds, reports, subscriptions

ITEMS = [(2.50, 4), (1.00, 3)]
PKG = Path(billing.__file__).parent


def test_alias_warns_and_matches():
    with pytest.warns(DeprecationWarning):
        assert billing.calc_total(ITEMS, 0.1) == billing.calculate_total(ITEMS, 0.1) == 11.7


def test_package_functions_do_not_warn():
    inv = {"id": 7, "items": ITEMS, "discount": 0.0}
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        assert invoices.invoice_amount(inv) == 13.0
        assert invoices.invoice_summary(inv) == "Invoice 7: 13.00"
        assert quotes.quote_amount(ITEMS) == 13.0
        assert quotes.compare_quotes(ITEMS, [(1.0, 1)]) == 12.0
        assert subscriptions.monthly_charge(ITEMS, 2) == 26.0
        assert subscriptions.annual_charge(ITEMS) == 143.0
        assert refunds.refund_amount(ITEMS, 0.5) == 6.5
        assert reports.revenue([inv, inv]) == 26.0
        assert reports.average_order([ITEMS, [(1.0, 1)]]) == 7.0


def test_old_name_gone_from_other_modules():
    for path in PKG.glob("*.py"):
        if path.name not in ("core.py", "__init__.py"):
            assert "calc_total" not in path.read_text(encoding="utf-8"), path.name
