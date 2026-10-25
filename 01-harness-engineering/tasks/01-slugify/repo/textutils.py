import re


def slugify(text):
    """Turn a title into a URL slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text


def word_count(text):
    return len(text.split())
