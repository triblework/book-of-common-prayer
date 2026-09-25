"""w20_cite.py -- roman chapter numerals to arabic in a 1662 lesson cell (Wave 20).

RULINGS R13: numerals are converted, the printed extent and the book's own
abbreviation and spelling are kept verbatim (R12), whitespace is normalized
and the cell-final stop is dropped. Nothing else is touched.

    to_arabic('i. Cor. i.')          -> '1. Cor. 1'
    to_arabic('xvii. xviii.')        -> '17. 18'
    to_arabic('Luke 1. to 39.')      -> 'Luke 1. to 39'
    to_arabic('xxv a)')              -> '25 a)'
    to_arabic('Lxvi.')               -> '66'
"""
import re

VAL = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}
ROMAN = re.compile(r'^c?(?:xc|xl|l?x{0,4})(?:ix|iv|v?i{0,4})$', re.I)


def roman(tok):
    """int for a well-formed roman numeral token (the MS writes 'iiii'), else None."""
    t = tok.lower()
    if t == 'c':        # '& c. 7' is 'and chapter 7', never 100
        return None
    if not t or not set(t) <= set('ivxlc') or not ROMAN.match(t):
        return None
    total, prev = 0, 0
    for ch in reversed(t):
        v = VAL[ch]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total or None


def to_arabic(cell):
    s = re.sub(r'\s+', ' ', cell.strip())
    out = []
    # tokens: runs of letters, or anything else, kept in order
    for tok in re.findall(r'[A-Za-z]+|[^A-Za-z]+', s):
        n = roman(tok) if tok.isalpha() else None
        out.append(str(n) if n is not None else tok)
    s = ''.join(out)
    return s.rstrip('.').rstrip() if s.endswith('.') else s


def chapters(cell):
    """(book or None, [chapter ints]) for the structural check; the book is the
    leading alphabetic abbreviation (with its '1.'/'2.' prefix), chapters are
    the numbers after it, ignoring an extent ('to 39', 'to vr. 30', '1. 39')."""
    a = to_arabic(cell)
    a = re.sub(r'\s*[a-c]\)|\s*\*', '', a).strip()
    m = re.match(r'^((?:\d[.,]?\s*){0,2}[A-Z][A-Za-z]*(?:[ .:]+(?:of|ye|&|[A-Z][A-Za-z]*))*)[.:]?\s*(.*)$', a)
    book, rest = (m.group(1).strip(' .:'), m.group(2)) if m else (None, a)
    rest = re.split(r'\bto\b', rest)[0]
    nums = [int(n) for n in re.findall(r'\d+', rest)]
    # '1. 39' after 'Luke 1. to 39' is chapter 1 FROM verse 39, not two chapters
    if not book and len(nums) == 2 and nums[1] - nums[0] > 5:
        nums = nums[:1]
    return book, nums
