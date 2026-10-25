PARTICLES = {"van", "von", "de", "da", "del", "der", "di", "le", "la"}


def split_name(full):
    """Split a full name into (first, last).

    Middle names stay with the first name. Surname particles such as
    'van' or 'de la' stay with the last name.
    """
    parts = full.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    last_start = len(parts) - 1
    while last_start > 1 and parts[last_start - 1].lower() in PARTICLES:
        last_start -= 1
    return " ".join(parts[:last_start]), " ".join(parts[last_start:])


def initials(full):
    first, last = split_name(full)
    return "".join(w[0].upper() for w in (first + " " + last).split() if w.lower() not in PARTICLES)
