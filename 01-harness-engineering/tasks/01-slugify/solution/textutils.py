import re
import unicodedata


def slugify(text, max_length=None):
    """Turn a title into a URL slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if max_length is not None:
        text = text[:max_length].rstrip("-")
    return text


def word_count(text):
    return len(text.split())
