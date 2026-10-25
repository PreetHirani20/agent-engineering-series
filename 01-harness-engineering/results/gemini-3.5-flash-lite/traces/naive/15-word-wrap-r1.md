# 15-word-wrap / naive / run 1
solved=True end=finished steps=9 tokens=12629+1606

## SYSTEM
```
You are a helpful coding assistant with tools for working with a code repository. Solve the user's issue.
```
## USER
```
`wrap(text, width)` in `wrapping.py` cuts text every `width` characters, even in the middle of a word. It should wrap like a text editor:

- Break lines only at whitespace; no line may be longer than `width`.
- A single word longer than `width` is split into pieces of `width` characters: `wrap("abcdefghij", 4)` -> `"abcd\nefgh\nij"`.
- Runs of spaces and tabs collapse to one space, and lines have no leading or trailing spaces.
- Paragraphs are separated by blank lines (lines with only whitespace count as blank). In the output, paragraphs are separated by exactly one empty line. A single newline inside a paragraph is treated as a space.
- `width < 1` raises `ValueError`. Empty or whitespace-only text returns `""`.

Example: `wrap("one two\nthree\n\n\n  four  ", 20)` -> `"one two three\n\nfour"`.
```
## ASSISTANT -> list_files
```json
{}
```
## TOOL
```
wrapping.py
tests/test_wrapping.py
```
## ASSISTANT -> read_file
```json
{"path":"wrapping.py"}
```
## TOOL
```
def wrap(text, width):
    """Wrap text so that no line is longer than `width`."""
    lines = []
    for i in range(0, len(text), width):
        lines.append(text[i:i + width])
    return "\n".join(lines)

```
## ASSISTANT -> read_file
```json
{"path":"tests/test_wrapping.py"}
```
## TOOL
```
from wrapping import wrap


def test_breaks_at_spaces():
    assert wrap("the quick brown fox", 10) == "the quick\nbrown fox"

```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\Temp\harness-engineering-work\gemini-3.5-flash-lite\naive\15-word-wrap-r1
plugins: anyio-4.15.1
collecting ... collected 1 item

tests/test_wrapping.py::test_breaks_at_spaces FAILED                     [100%]

================================== FAILURES ===================================
____________________________ test_breaks_at_spaces ____________________________

    def test_breaks_at_spaces():
>       assert wrap("the quick brown fox", 10) == "the quick\nbrown fox"
E       AssertionError: assert 'the quick \nbrown fox' == 'the quick\nbrown fox'
E         
E         - the quick
E         + the quick 
E         ?          +
E           brown fox

tests\test_wrapping.py:5: AssertionError
============================== 1 failed in 0.09s ==============================
```
## ASSISTANT -> write_file
```json
{"path":"wrapping.py","content":"def wrap(text, width):\n    \"\"\"Wrap text so that no line is longer than `width`.\"\"\"\n    if width \u003c 1:\n        raise ValueError(\"width must be at least 1\")\n    \n    if not text or text.isspace():\n        return \"\"\n\n    # Split into paragraphs by blank lines (lines with only whitespace count as blank)\n    # Paragraphs are separated by blank lines. A single newline inside a paragraph is treated as a space.\n    # Runs of spaces and tabs collapse to one space, and lines have no leading or trailing spaces.\n    \n    # Let's normalize whitespace and newlines per paragraph.\n    # First, let's split the text into raw paragraphs or lines.\n    # Wait, how are paragraphs separated? Paragraphs are separated by blank lines (one or more lines containing only whitespace/newlines).\n    # Let's inspect how to split paragraphs correctly.\n    # If we replace any run of whitespace (including newlines) that contains at least one blank line (two or more consecutive newlines with optional spaces/tabs) as paragraph separator, or split by regex of multiple newlines.\n    \n    import re\n    \n    # Let's normalize tabs and spaces first or handle them.\n    # \"Runs of spaces and tabs collapse to one space, and lines have no leading or trailing spaces.\"\n    # \"A single newline inside a paragraph is treated as a space.\"\n    # This means inside a paragraph, newlines, spaces, and tabs all act as whitespace separators between words!\n    #...[trace truncated]
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
rootdir: <home>\Temp\harness-engineering-work\gemini-3.5-flash-lite\naive\15-word-wrap-r1
plugins: anyio-4.15.1
collecting ... collected 1 item

tests/test_wrapping.py::test_breaks_at_spaces PASSED                     [100%]

============================== 1 passed in 0.07s ==============================
```
## ASSISTANT -> write_file
```json
{"path":"tests/test_wrapping.py","content":"from wrapping import wrap\nimport pytest\n\n\ndef test_breaks_at_spaces():\n    assert wrap(\"the quick brown fox\", 10) == \"the quick\\nbrown fox\"\n\n\ndef test_width_validation():\n    with pytest.raises(ValueError):\n        wrap(\"hello\", 0)\n    with pytest.raises(ValueError):\n        wrap(\"hello\", -5)\n\n\ndef test_empty_or_whitespace():\n    assert wrap(\"\", 5) == \"\"\n    assert wrap(\"   \\n\\t  \", 5) == \"\"\n\n\ndef test_long_word_splitting():\n    assert wrap(\"abcdefghij\", 4) == \"abcd\\nefgh\\nij\"\n\n\ndef test_whitespace_collapse_and_newlines_in_paragraph():\n    assert wrap(\"one two\\nthree\\n\\n\\n  four  \", 20) == \"one two three\\n\\nfour\"\n\n\ndef test_multiple_paragraphs():\n    assert wrap(\"para one\\n\\npara two\", 10) == \"para one\\n\\npara two\"\n"}
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
rootdir: <home>\Temp\harness-engineering-work\gemini-3.5-flash-lite\naive\15-word-wrap-r1
plugins: anyio-4.15.1
collecting ... collected 6 items

tests/test_wrapping.py::test_breaks_at_spaces PASSED                     [ 16%]
tests/test_wrapping.py::test_width_validation PASSED                     [ 33%]
tests/test_wrapping.py::test_empty_or_whitespace PASSED                  [ 50%]
tests/test_wrapping.py::test_long_word_splitting PASSED                  [ 66%]
tests/test_wrapping.py::test_whitespace_collapse_and_newlines_in_paragraph PASSED [ 83%]
tests/test_wrapping.py::test_multiple_paragraphs PASSED                  [100%]

============================== 6 passed in 0.05s ==============================
```
## ASSISTANT
```
I have successfully updated `wrap(text, width)` in `wrapping.py` to meet all the specified requirements:

- Breaks lines only at whitespace, ensuring no line exceeds `width` characters.
- Splits words longer than `width` into pieces of `width` characters.
- Collapses runs of spaces and tabs to one space and trims leading/trailing spaces on lines.
- Treats single newlines inside paragraphs as spaces and separates paragraphs with exactly one empty line.
- Raises `ValueError` if `width < 1` and returns `""` for empty or whitespace-only text.
```
## GRADING
```
.......                                                                  [100%]
7 passed in 0.02s
```