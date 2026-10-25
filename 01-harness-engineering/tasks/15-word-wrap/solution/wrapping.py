import re


def wrap(text, width):
    """Wrap text so that no line is longer than `width`."""
    if width < 1:
        raise ValueError("width must be at least 1")
    paragraphs = []
    for para in re.split(r"\n[ \t]*\n", text):
        lines, cur = [], ""
        for word in para.split():
            while len(word) > width:
                if cur:
                    lines.append(cur)
                    cur = ""
                lines.append(word[:width])
                word = word[width:]
            if not cur:
                cur = word
            elif len(cur) + 1 + len(word) <= width:
                cur += " " + word
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        if lines:
            paragraphs.append("\n".join(lines))
    return "\n\n".join(paragraphs)
