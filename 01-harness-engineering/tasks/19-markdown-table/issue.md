`to_markdown(rows, columns=None)` in `mdtable.py` crashes on rows with missing keys and produces tables that are hard to read. Please make it follow this spec exactly:

- `columns=None` means: every key that appears in any row, in first-seen order.
- A missing key or a `None` value is an empty cell.
- `|` inside a value is escaped as `\|`. A newline inside a value is replaced by a single space.
- Column width = the largest of 3, the header length, and the length of every cell (after escaping).
- A column is numeric if every non-empty value in it is an `int` or `float` (`bool` does not count as numeric). Numeric columns are right-aligned (header too); other columns are left-aligned.
- Every row, including the header and separator, is written as `"| " + " | ".join(cells) + " |"`, with each cell padded to the column width.
- Separator cells are dashes of the column width; in numeric columns the last dash is replaced by `:`.
- Rows are joined with `\n` and there is no trailing newline. No rows and no columns gives `""`. No rows but given columns gives just the header and separator.

Example:
```python
to_markdown([{"name": "Ada", "score": 9.5}, {"name": "Grace Hopper", "score": 10, "note": "a|b"}])
```
returns
```
| name         | score | note |
| ------------ | ----: | ---- |
| Ada          |   9.5 |      |
| Grace Hopper |    10 | a\|b |
```
