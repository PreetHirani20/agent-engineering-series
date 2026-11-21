"""Compare an answer with the expected value, and say what kind of mistake it was."""

from __future__ import annotations

import re

from .scenario import Task

NULLS = {"", "null", "none", "na", "n/a", "unknown", "nothing", "noneonfile"}


def norm(value) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def as_number(value):
    m = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(m.group()) if m else None


def as_minutes(value):
    s = str(value).strip().lower().replace(".", ":")
    m = re.search(r"(\d{1,2})(?::?(\d{2}))?\s*(am|pm)?", s)
    if not m:
        return None
    h, mins, ampm = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if ampm == "pm" and h < 12:
        h += 12
    if ampm == "am" and h == 12:
        h = 0
    return h * 60 + mins


def same(kind: str, answer, target) -> bool:
    if answer is None or target is None:
        return False
    if kind == "number":
        a, b = as_number(answer), as_number(target)
        return a is not None and b is not None and abs(a - b) < 0.005
    if kind == "time":
        return as_minutes(answer) is not None and as_minutes(answer) == as_minutes(target)
    if kind == "text":
        return norm(target) in norm(answer)
    if kind == "carrier":  # "Royal Mail Tracked 48" names Royal Mail; "DHL" names DHL Express
        return norm(target) in norm(answer) or norm(answer) == norm(str(target).split()[0])
    return norm(answer) == norm(target)  # postcode, email, code


def is_null(answer) -> bool:
    return answer is None or norm(answer) in NULLS


def grade(task: Task, answer) -> str:
    """ok | missing | outdated | not-forgotten | mixed-up | wrong"""
    if task.expected is None:
        if is_null(answer):
            return "ok"
        return "not-forgotten" if any(same(task.kind, answer, o) for o in task.old_values) else "wrong"
    if is_null(answer):
        return "missing"
    stale = any(same(task.kind, answer, o) for o in task.old_values)
    if same(task.kind, answer, task.expected) and not stale:
        return "ok"
    if stale:
        return "outdated"
    if any(same(task.kind, answer, c) for c in task.confusers):
        return "mixed-up"
    return "wrong"
