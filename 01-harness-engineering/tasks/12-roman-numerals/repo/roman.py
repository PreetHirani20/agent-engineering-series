NUMERALS = [(1000, "M"), (500, "D"), (100, "C"), (50, "L"), (10, "X"), (5, "V"), (1, "I")]


def to_roman(n):
    out = ""
    for value, letter in NUMERALS:
        while n >= value:
            out += letter
            n -= value
    return out


def from_roman(s):
    lookup = {letter: value for value, letter in NUMERALS}
    return sum(lookup[ch] for ch in s)
