`slugify()` in `textutils.py` produces ugly slugs. `slugify("Hello, World!")` returns `"hello-world-"` but should return `"hello-world"`.

What slugify should do:
- Lowercase everything.
- Accented letters become their plain letter: `slugify("Crème Brûlée")` -> `"creme-brulee"`.
- Any run of characters that are not a-z or 0-9 becomes a single `-`.
- No leading or trailing `-`: `slugify("  --Hello--  ")` -> `"hello"`.
- Input with no letters or digits (`""`, `"!!!"`) returns `""`.
- Add an optional `max_length=None` argument. When set, cut the slug to at most that many characters and make sure it does not end with `-`: `slugify("hello world again", max_length=11)` -> `"hello-world"`, `slugify("hello world", max_length=6)` -> `"hello"`.
