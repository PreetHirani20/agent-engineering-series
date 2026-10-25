def _field(value, delimiter):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    if any(ch in text for ch in (delimiter, '"', "\n", "\r")):
        return '"' + text.replace('"', '""') + '"'
    return text


def to_csv(rows, columns, header=True, delimiter=","):
    """Render a list of dicts as CSV text."""
    lines = []
    if header:
        lines.append(delimiter.join(_field(c, delimiter) for c in columns))
    for row in rows:
        lines.append(delimiter.join(_field(row.get(c), delimiter) for c in columns))
    return "".join(line + "\r\n" for line in lines)
