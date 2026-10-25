Rename `calc_total` to `calculate_total` throughout the `billing` package.

- `billing/core.py` defines `calculate_total` with the same behaviour.
- Keep `calc_total` in `billing/core.py` as a deprecated alias: it emits a `DeprecationWarning` and returns the same result as `calculate_total`.
- `billing/__init__.py` exports both names.
- No other code in the package may use `calc_total` any more (including imports and aliased imports), so calling any function in the package never triggers the deprecation warning.
