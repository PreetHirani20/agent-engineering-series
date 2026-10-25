NUMERALS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
            (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
VALUES = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}


def to_roman(n):
    if not 1 <= n <= 3999:
        raise ValueError("Roman numerals cover 1 to 3999")
    out = ""
    for value, letters in NUMERALS:
        while n >= value:
            out += letters
            n -= value
    return out


def from_roman(s):
    s = s.upper()
    if not s or any(ch not in VALUES for ch in s):
        raise ValueError(f"not a Roman numeral: {s!r}")
    total = 0
    for i, ch in enumerate(s):
        v = VALUES[ch]
        total += -v if i + 1 < len(s) and VALUES[s[i + 1]] > v else v
    if not 1 <= total <= 3999 or to_roman(total) != s:
        raise ValueError(f"not a correctly written Roman numeral: {s!r}")
    return total
