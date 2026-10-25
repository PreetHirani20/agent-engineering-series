`parse_duration()` in `durations.py` needs to handle more inputs. It returns a number of seconds.

- Support days: `"2d"` -> `172800`.
- Allow spaces between parts: `"1h 30m"` -> `5400`.
- Units are case-insensitive: `"1H30M"` -> `5400`.
- Parts can appear in any order: `"30m1h"` -> `5400`.
- Invalid input must raise `ValueError` instead of quietly returning 0 or ignoring junk. Invalid means: an empty or blank string, a number with no unit (`"5"`), an unknown unit (`"10x"`), or any extra text (`"1h and 30m"`).
