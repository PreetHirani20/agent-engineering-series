# 09-split-name / engineered / run 1
solved=True end=finished steps=12 tokens=26629+872

## SYSTEM
```
You are a careful software engineer working in a small Python repository. Resolve the issue by changing the code.

How to work:
1. Orient: look at the repository tree, then use `search` to find the code the issue is about. The root cause may be in a different file from the one the issue mentions.
2. Reproduce: run the tests and read what fails.
3. Make a checklist of every requirement in the issue, including each edge case and example it mentions. Write that checklist into your notes with `update_notes` and tick items off as you go.
4. Fix the root cause with small, targeted changes. Keep everything that already works working.
5. Verify: run the tests again. The existing tests do not cover every requirement, so for anything they miss, add a small test file of your own at the repository root (for example `test_issue_checks.py`) and run it.
6. When every checklist item is handled and all tests pass, call `finish` with a one-line summary.

Rules:
- Never edit the existing files in tests/. They define correct behaviour; change the code under test instead.
- Keep public function names and signatures unless the issue says otherwise.
- Standard library only.
- Act through tool calls. Do not describe a change you intend to make; make it.
```
## USER
```
<issue>
`split_name()` in `people.py` raises `ValueError` for one-word names like `"Cher"` or `"Madonna"`. These are real customers. A one-word name should return the name as the first name and an empty last name: `split_name("Cher") == ("Cher", "")`.

While you're there:
- Extra spaces anywhere should not matter: `split_name("  Ada   Lovelace ") == ("Ada", "Lovelace")`.
- An empty or blank string returns `("", "")`.
</issue>

Repository (path, size):
people.py  (23 lines, 779 bytes)
tests/test_people.py  (22 lines, 594 bytes)  [read-only]
Files marked [read-only] cannot be changed.
```
## ASSISTANT -> list_files
```json
{}
```
## TOOL
```
people.py  (23 lines, 779 bytes)
tests/test_people.py  (22 lines, 594 bytes)  [read-only]
```
## ASSISTANT -> update_notes
```json
{"notes":"- [ ] One-word names like \"Cher\" or \"Madonna\" return (\"Cher\", \"\") instead of raising ValueError.\n- [ ] Extra spaces anywhere should not matter: split_name(\"  Ada   Lovelace \") == (\"Ada\", \"Lovelace\").\n- [ ] An empty or blank string returns (\"\", \"\")."}
```
## TOOL
```
Notes saved.
```
## ASSISTANT -> read_file
```json
{"path":"people.py"}
```
## TOOL
```
    1  PARTICLES = {"van", "von", "de", "da", "del", "der", "di", "le", "la"}
    2  
    3  
    4  def split_name(full):
    5      """Split a full name into (first, last).
    6  
    7      Middle names stay with the first name. Surname particles such as
    8      'van' or 'de la' stay with the last name.
    9      """
   10      parts = full.split(" ")
   11      last_start = len(parts) - 1
   12      while last_start > 1 and parts[last_start - 1].lower() in PARTICLES:
   13          last_start -= 1
   14      first = " ".join(parts[:last_start])
   15      last = " ".join(parts[last_start:])
   16      if not first:
   17          raise ValueError("need a first and last name")
   18      return first, last
   19  
   20  
   21  def initials(full):
   22      first, last = split_name(full)
   23      return "".join(w[0].upper() for w in (first + " " + last).split() if w.lower() not in PARTICLES)
[people.py: lines 1-23 of 23]
```
## ASSISTANT -> read_file
```json
{"path":"tests/test_people.py"}
```
## TOOL
```
    1  from people import initials, split_name
    2  
    3  
    4  def test_simple():
    5      assert split_name("Ada Lovelace") == ("Ada", "Lovelace")
    6  
    7  
    8  def test_middle_names_stay_with_first():
    9      assert split_name("Mary Ann Smith") == ("Mary Ann", "Smith")
   10  
   11  
   12  def test_particles_stay_with_last():
   13      assert split_name("Ludwig van Beethoven") == ("Ludwig", "van Beethoven")
   14      assert split_name("Charles de la Vallee") == ("Charles", "de la Vallee")
   15  
   16  
   17  def test_initials():
   18      assert initials("Ludwig van Beethoven") == "LB"
   19  
   20  
   21  def test_one_word_name():
   22      assert split_name("Cher") == ("Cher", "")
[tests/test_people.py: lines 1-22 of 22]
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
TESTS FAILING (1 failed, 4 passed in 0.30s)
....F                                                                    [100%]
================================== FAILURES ===================================
_____________________________ test_one_word_name ______________________________
tests\test_people.py:22: in test_one_word_name
    assert split_name("Cher") == ("Cher", "")
           ^^^^^^^^^^^^^^^^^^
people.py:17: in split_name
    raise ValueError("need a first and last name")
E   ValueError: need a first and last name
1 failed, 4 passed in 0.30s
```
## ASSISTANT -> update_notes
```json
{"notes":"- [/] One-word names like \"Cher\" or \"Madonna\" return (\"Cher\", \"\") instead of raising ValueError. (Tested in test_people.py)\n- [ ] Extra spaces anywhere should not matter: split_name(\"  Ada   Lovelace \") == (\"Ada\", \"Lovelace\").\n- [ ] An empty or blank string returns (\"\", \"\")."}
```
## TOOL
```
Notes saved.
```
## ASSISTANT -> edit_file
```json
{"path":"people.py","new_text":"def split_name(full):\n    \"\"\"Split a full name into (first, last).\n\n    Middle names stay with the first name. Surname particles such as\n    'van' or 'de la' stay with the last name.\n    \"\"\"\n    parts = full.split()\n    if not parts:\n        return \"\", \"\"\n    if len(parts) == 1:\n        return parts[0], \"\"\n    last_start = len(parts) - 1\n    while last_start \u003e 1 and parts[last_start - 1].lower() in PARTICLES:\n        last_start -= 1\n    first = \" \".join(parts[:last_start])\n    last = \" \".join(parts[last_start:])\n    if not first:\n        return \"\", \"\"\n    return first, last","old_text":"def split_name(full):\n    \"\"\"Split a full name into (first, last).\n\n    Middle names stay with the first name. Surname particles such as\n    'van' or 'de la' stay with the last name.\n    \"\"\"\n    parts = full.split(\" \")\n    last_start = len(parts) - 1\n    while last_start \u003e 1 and parts[last_start - 1].lower() in PARTICLES:\n        last_start -= 1\n    first = \" \".join(parts[:last_start])\n    last = \" \".join(parts[last_start:])\n    if not first:\n        raise ValueError(\"need a first and last name\")\n    return first, last"}
```
## TOOL
```
Edited people.py. The changed region now reads:
    2  
    3  
    4  def split_name(full):
    5      """Split a full name into (first, last).
    6  
    7      Middle names stay with the first name. Surname particles such as
    8      'van' or 'de la' stay with the last name.
    9      """
   10      parts = full.split()
   11      if not parts:
   12          return "", ""
   13      if len(parts) == 1:
   14          return parts[0], ""
   15      last_start = len(parts) - 1
   16      while last_start > 1 and parts[last_start - 1].lower() in PARTICLES:
   17          last_start -= 1
   18      first = " ".join(parts[:last_start])
   19      last = " ".join(parts[last_start:])
   20      if not first:
   21          return "", ""
   22      return first, last
   23  
   24  
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
All tests passed (5 passed in 0.13s).
```
## ASSISTANT -> create_file
```json
{"path":"test_issue_checks.py","content":"from people import split_name, initials\n\ndef test_extra_spaces_and_blank():\n    assert split_name(\"  Ada   Lovelace \") == (\"Ada\", \"Lovelace\")\n    assert split_name(\"\") == (\"\", \"\")\n    assert split_name(\"   \") == (\"\", \"\")\n    assert initials(\"  Ada   Lovelace \") == \"AL\"\n    assert initials(\"   \") == \"\"\n"}
```
## TOOL
```
Created test_issue_checks.py (9 lines).
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
All tests passed (6 passed in 0.12s).
```
## ASSISTANT -> update_notes
```json
{"notes":"- [x] One-word names like \"Cher\" or \"Madonna\" return (\"Cher\", \"\") instead of raising ValueError.\n- [x] Extra spaces anywhere should not matter: split_name(\"  Ada   Lovelace \") == (\"Ada\", \"Lovelace\").\n- [x] An empty or blank string returns (\"\", \"\")."}
```
## TOOL
```
Notes saved.
```
## ASSISTANT -> finish
```json
{"summary":"Updated split_name() in people.py to handle one-word names, extra whitespace, and empty or blank strings correctly."}
```
## TOOL
```
Accepted: all tests pass.
```
## GRADING
```
.........                                                                [100%]
9 passed in 0.08s
```