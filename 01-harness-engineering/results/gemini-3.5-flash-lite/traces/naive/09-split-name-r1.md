# 09-split-name / naive / run 1
solved=True end=finished steps=9 tokens=12042+725

## SYSTEM
```
You are a helpful coding assistant with tools for working with a code repository. Solve the user's issue.
```
## USER
```
`split_name()` in `people.py` raises `ValueError` for one-word names like `"Cher"` or `"Madonna"`. These are real customers. A one-word name should return the name as the first name and an empty last name: `split_name("Cher") == ("Cher", "")`.

While you're there:
- Extra spaces anywhere should not matter: `split_name("  Ada   Lovelace ") == ("Ada", "Lovelace")`.
- An empty or blank string returns `("", "")`.
```
## ASSISTANT -> list_files
```json
{}
```
## TOOL
```
people.py
tests/test_people.py
```
## ASSISTANT -> read_file
```json
{"path":"people.py"}
```
## TOOL
```
PARTICLES = {"van", "von", "de", "da", "del", "der", "di", "le", "la"}


def split_name(full):
    """Split a full name into (first, last).

    Middle names stay with the first name. Surname particles such as
    'van' or 'de la' stay with the last name.
    """
    parts = full.split(" ")
    last_start = len(parts) - 1
    while last_start > 1 and parts[last_start - 1].lower() in PARTICLES:
        last_start -= 1
    first = " ".join(parts[:last_start])
    last = " ".join(parts[last_start:])
    if not first:
        raise ValueError("need a first and last name")
    return first, last


def initials(full):
    first, last = split_name(full)
    return "".join(w[0].upper() for w in (first + " " + last).split() if w.lower() not in PARTICLES)

```
## ASSISTANT -> read_file
```json
{"path":"tests/test_people.py"}
```
## TOOL
```
from people import initials, split_name


def test_simple():
    assert split_name("Ada Lovelace") == ("Ada", "Lovelace")


def test_middle_names_stay_with_first():
    assert split_name("Mary Ann Smith") == ("Mary Ann", "Smith")


def test_particles_stay_with_last():
    assert split_name("Ludwig van Beethoven") == ("Ludwig", "van Beethoven")
    assert split_name("Charles de la Vallee") == ("Charles", "de la Vallee")


def test_initials():
    assert initials("Ludwig van Beethoven") == "LB"


def test_one_word_name():
    assert split_name("Cher") == ("Cher", "")

```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\01-harness-engineering\.work\naive\09-split-name-r1
plugins: anyio-4.15.1
collecting ... collected 5 items

tests/test_people.py::test_simple PASSED                                 [ 20%]
tests/test_people.py::test_middle_names_stay_with_first PASSED           [ 40%]
tests/test_people.py::test_particles_stay_with_last PASSED               [ 60%]
tests/test_people.py::test_initials PASSED                               [ 80%]
tests/test_people.py::test_one_word_name FAILED                          [100%]

================================== FAILURES ===================================
_____________________________ test_one_word_name ______________________________

    def test_one_word_name():
>       assert split_name("Cher") == ("Cher", "")
               ^^^^^^^^^^^^^^^^^^

tests\test_people.py:22: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

full = 'Cher'

    def split_name(full):
        """Split a full name into (first, last).
    
        Middle names stay with the first name. Surname particles such as
        'van' or 'de la' stay with the last name.
        """
        parts = full.split(" ")
        last_start = len(parts) - 1
        while last_start > 1 and parts[last_start - 1].lower() in PARTICLES:
            last_start -= 1
        first = " ".join(parts[:last_start])
        last = " ".join(parts[last_start:])
        if not first:
>           raise ValueError("need a first and last name")
E           ValueError: need a first and last name

people.py:17: ValueError
========================= 1 failed, 4 passed in 0.33s =========================
```
## ASSISTANT -> write_file
```json
{"content":"PARTICLES = {\"van\", \"von\", \"de\", \"da\", \"del\", \"der\", \"di\", \"le\", \"la\"}\n\n\ndef split_name(full):\n    \"\"\"Split a full name into (first, last).\n\n    Middle names stay with the first name. Surname particles such as\n    'van' or 'de la' stay with the last name.\n    \"\"\"\n    parts = [p for p in full.strip().split(\" \") if p]\n    if not parts:\n        return \"\", \"\"\n    if len(parts) == 1:\n        return parts[0], \"\"\n    last_start = len(parts) - 1\n    while last_start \u003e 1 and parts[last_start - 1].lower() in PARTICLES:\n        last_start -= 1\n    first = \" \".join(parts[:last_start])\n    last = \" \".join(parts[last_start:])\n    return first, last\n\n\ndef initials(full):\n    first, last = split_name(full)\n    return \"\".join(w[0].upper() for w in (first + \" \" + last).split() if w.lower() not in PARTICLES)\n","path":"people.py"}
```
## TOOL
```
OK
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\01-harness-engineering\.work\naive\09-split-name-r1
plugins: anyio-4.15.1
collecting ... collected 5 items

tests/test_people.py::test_simple PASSED                                 [ 20%]
tests/test_people.py::test_middle_names_stay_with_first PASSED           [ 40%]
tests/test_people.py::test_particles_stay_with_last PASSED               [ 60%]
tests/test_people.py::test_initials PASSED                               [ 80%]
tests/test_people.py::test_one_word_name PASSED                          [100%]

============================== 5 passed in 0.20s ==============================
```
## ASSISTANT -> write_file
```json
{"content":"from people import initials, split_name\n\n\ndef test_simple():\n    assert split_name(\"Ada Lovelace\") == (\"Ada\", \"Lovelace\")\n\n\ndef test_middle_names_stay_with_first():\n    assert split_name(\"Mary Ann Smith\") == (\"Mary Ann\", \"Smith\")\n\n\ndef test_particles_stay_with_last():\n    assert split_name(\"Ludwig van Beethoven\") == (\"Ludwig\", \"van Beethoven\")\n    assert split_name(\"Charles de la Vallee\") == (\"Charles\", \"de la Vallee\")\n\n\ndef test_initials():\n    assert initials(\"Ludwig van Beethoven\") == \"LB\"\n\n\ndef test_one_word_name():\n    assert split_name(\"Cher\") == (\"Cher\", \"\")\n    assert split_name(\"Madonna\") == (\"Madonna\", \"\")\n\n\ndef test_extra_spaces():\n    assert split_name(\"  Ada   Lovelace \") == (\"Ada\", \"Lovelace\")\n\n\ndef test_empty_or_blank():\n    assert split_name(\"\") == (\"\", \"\")\n    assert split_name(\"   \") == (\"\", \"\")\n","path":"tests/test_people.py"}
```
## TOOL
```
OK
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\01-harness-engineering\.work\naive\09-split-name-r1
plugins: anyio-4.15.1
collecting ... collected 7 items

tests/test_people.py::test_simple PASSED                                 [ 14%]
tests/test_people.py::test_middle_names_stay_with_first PASSED           [ 28%]
tests/test_people.py::test_particles_stay_with_last PASSED               [ 42%]
tests/test_people.py::test_initials PASSED                               [ 57%]
tests/test_people.py::test_one_word_name PASSED                          [ 71%]
tests/test_people.py::test_extra_spaces PASSED                           [ 85%]
tests/test_people.py::test_empty_or_blank PASSED                         [100%]

============================== 7 passed in 0.22s ==============================
```
## ASSISTANT
```
I have updated `split_name()` in `people.py` and added comprehensive tests to cover:
- One-word names returning `(name, "")` (e.g. `"Cher"`, `"Madonna"`).
- Extra spaces anywhere not affecting the split result (e.g. `"  Ada   Lovelace "`).
- Empty or blank strings returning `("", "")`.
```
## GRADING
```
.........                                                                [100%]
9 passed in 0.08s
```