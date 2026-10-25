def _cell(value):
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\r\n", " ").replace("\n", " ")


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def to_markdown(rows, columns=None):
    """Render a list of dicts as a Markdown table."""
    if columns is None:
        columns = list(dict.fromkeys(k for r in rows for k in r))
    if not columns:
        return ""
    cells = [[_cell(r.get(c)) for c in columns] for r in rows]
    widths, numeric = [], []
    for i, c in enumerate(columns):
        widths.append(max([3, len(c)] + [len(row[i]) for row in cells]))
        values = [r.get(c) for r in rows if r.get(c) is not None]
        numeric.append(bool(values) and all(_is_number(v) for v in values))

    def line(items):
        padded = [s.rjust(w) if num else s.ljust(w) for s, w, num in zip(items, widths, numeric)]
        return "| " + " | ".join(padded) + " |"

    sep = "| " + " | ".join("-" * (w - 1) + (":" if num else "-") for w, num in zip(widths, numeric)) + " |"
    return "\n".join([line(columns), sep] + [line(row) for row in cells])
