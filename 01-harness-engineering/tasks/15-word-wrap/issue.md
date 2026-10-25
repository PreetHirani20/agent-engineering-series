`wrap(text, width)` in `wrapping.py` cuts text every `width` characters, even in the middle of a word. It should wrap like a text editor:

- Break lines only at whitespace; no line may be longer than `width`.
- A single word longer than `width` is split into pieces of `width` characters: `wrap("abcdefghij", 4)` -> `"abcd\nefgh\nij"`.
- Runs of spaces and tabs collapse to one space, and lines have no leading or trailing spaces.
- Paragraphs are separated by blank lines (lines with only whitespace count as blank). In the output, paragraphs are separated by exactly one empty line. A single newline inside a paragraph is treated as a space.
- `width < 1` raises `ValueError`. Empty or whitespace-only text returns `""`.

Example: `wrap("one two\nthree\n\n\n  four  ", 20)` -> `"one two three\n\nfour"`.
