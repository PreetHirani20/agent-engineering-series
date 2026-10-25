def wrap(text, width):
    """Wrap text so that no line is longer than `width`."""
    lines = []
    for i in range(0, len(text), width):
        lines.append(text[i:i + width])
    return "\n".join(lines)
