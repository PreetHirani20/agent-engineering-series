Invoice totals in `invoice.py` are sometimes off by a cent. `line_total(1, 2.675)` returns `2.67`; accounting expects `2.68`.

Please change both functions so that:
- They return `decimal.Decimal` values with exactly two decimal places, rounded half-up (the way invoices are done on paper): `line_total(1, 2.675) == Decimal("2.68")`.
- They accept quantities and prices as int, float, str or Decimal. Floats must be converted through `str()` first so binary float noise does not leak in.
- Each line is rounded to cents first; tax is applied to the sum of the rounded lines and the result is rounded once at the end.
- `invoice_total([], 0.2)` returns `Decimal("0.00")`.
