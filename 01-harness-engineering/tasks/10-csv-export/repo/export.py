def to_csv(rows, columns, header=True, delimiter=","):
    """Render a list of dicts as CSV text."""
    lines = [delimiter.join(columns)]
    for row in rows:
        lines.append(delimiter.join(str(row.get(c)) for c in columns))
    return "\n".join(lines)
