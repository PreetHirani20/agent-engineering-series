Our hand-written CSV export in `export.py` breaks when customers open files in Excel. Please make `to_csv(rows, columns, header=True, delimiter=",")` follow RFC 4180:

1. A field that contains the delimiter, a double quote, `\n` or `\r` must be wrapped in double quotes.
2. Double quotes inside a field are doubled: the value `say "hi"` is written as `"say ""hi"""`.
3. `None` or a missing key is written as an empty field (right now it writes `None`).
4. `header=False` must leave out the header row (right now the flag is ignored).
5. Every line ends with `\r\n`, including the last one. With no rows and `header=False` the result is `""`.
6. Booleans are written as `true` / `false`.

Header names follow the same quoting rules as values. Keep the function signature.
