#!/usr/bin/env python3
"""w10_cite.py — canonicalize a printed reading citation (Wave 10).

Authoring-only; NOT published. Implements the citation rule in
ingest/WAVE10_GUIDE.md §3: a reading is carried as its appointed citation only,
written to the precision THAT EDITION'S BOOK PRINTS, in one house form:

    "Rom. xiii."          (1549/1552/1559: chapter only)  -> "Romans 13"
    "Rom. xiii. 8."       (1604+/1662/American)           -> "Romans 13:8"
    "St. Matt. xxi. 1."                                   -> "Matthew 21:1"
    "Rom. 13.8."          (1637, arabic already)          -> "Romans 13:8"
    "Romans 13.8-14"      (CoE renders 1662 with an end   -> "Romans 13:8"
                           verse; the book does not, so
                           the range is dropped here and
                           recorded in provenance.yaml)

Nothing is guessed: an abbreviation outside BOOKS raises, so a new form fails the
build instead of being silently invented.
"""
import re, sys

# Printed abbreviation (lower-cased, dots stripped) -> canonical modern book name.
BOOKS = {
    "gen": "Genesis", "genesis": "Genesis",
    "exod": "Exodus", "exodus": "Exodus",
    "deut": "Deuteronomy", "deuteronomy": "Deuteronomy",
    "kings": "Kings", "1 kings": "1 Kings", "2 kings": "2 Kings",
    "prov": "Proverbs", "proverbs": "Proverbs",
    "eccles": "Ecclesiastes", "ecclesiasticus": "Ecclesiasticus",
    "cant": "Song of Solomon",
    "esa": "Isaiah", "esay": "Isaiah", "isai": "Isaiah", "isaiah": "Isaiah",
    "hiere": "Jeremiah", "jere": "Jeremiah", "jerem": "Jeremiah",
    "jeremiah": "Jeremiah", "jeremy": "Jeremiah",
    "ezek": "Ezekiel", "ezekiel": "Ezekiel",
    "dan": "Daniel", "daniel": "Daniel",
    "joel": "Joel", "amos": "Amos", "jonah": "Jonah", "micah": "Micah",
    "hab": "Habakkuk", "zeph": "Zephaniah", "hag": "Haggai",
    "zech": "Zechariah", "zachary": "Zechariah", "mal": "Malachi",
    "wisd": "Wisdom", "wisdom": "Wisdom", "baruch": "Baruch",
    "tobit": "Tobit", "ecclus": "Ecclesiasticus",

    "matt": "Matthew", "mat": "Matthew", "matth": "Matthew",
    "matthew": "Matthew", "st matt": "Matthew", "st matth": "Matthew",
    "st matthew": "Matthew",
    "mark": "Mark", "marke": "Mark", "st mark": "Mark", "st marke": "Mark",
    "luke": "Luke", "luc": "Luke", "st luke": "Luke", "st luc": "Luke",
    "john": "John", "st john": "John",
    "1 john": "1 John", "1 st john": "1 John",
    "2 john": "2 John", "3 john": "3 John",
    "acts": "Acts", "the actes": "Acts", "actes": "Acts",

    "rom": "Romans", "roma": "Romans", "romans": "Romans",
    "1 cor": "1 Corinthians", "1 corinthians": "1 Corinthians",
    "2 cor": "2 Corinthians", "2 corinthians": "2 Corinthians",
    "gal": "Galatians", "galat": "Galatians", "galatians": "Galatians",
    "eph": "Ephesians", "ephes": "Ephesians", "ephesians": "Ephesians",
    "phil": "Philippians", "philipp": "Philippians",
    "philippians": "Philippians",
    "col": "Colossians", "coloss": "Colossians", "colossians": "Colossians",
    "1 thess": "1 Thessalonians", "1 thessalonians": "1 Thessalonians",
    "2 thess": "2 Thessalonians", "2 thessalonians": "2 Thessalonians",
    "1 tim": "1 Timothy", "2 tim": "2 Timothy",
    "tit": "Titus", "titus": "Titus",
    "philemon": "Philemon",
    "heb": "Hebrews", "hebr": "Hebrews", "hebrews": "Hebrews",
    "james": "James", "st james": "James",
    "1 pet": "1 Peter", "1 peter": "1 Peter",
    "2 pet": "2 Peter", "2 peter": "2 Peter",
    "jude": "Jude",
    "apoc": "Revelation", "revelation": "Revelation", "rev": "Revelation",
}

ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def roman_to_int(s):
    s = s.lower()
    if not s or any(ch not in ROMAN for ch in s):
        return None
    total, prev = 0, 0
    for ch in reversed(s):
        val = ROMAN[ch]
        total = total - val if val < prev else total + val
        prev = max(prev, val)
    return total or None


def _number(token):
    """A chapter/verse token: roman numeral or arabic digits -> int."""
    token = token.strip().strip(".").strip()
    if token.isdigit():
        return int(token)
    return roman_to_int(token)


def canonical(printed):
    """Printed citation -> 'Book Chapter' or 'Book Chapter:verse'."""
    s = printed.strip()
    s = re.sub(r"\[[^\]]*\]", "", s)          # drop editorial [-14] ranges
    # The Church of England renders 1662 with a closing verse ("Romans 13.8-14")
    # that the printed book does not carry; drop it per WAVE10_GUIDE.md §3. The
    # full modern range is recorded in provenance.yaml instead.
    s = re.sub(r"(\d)\s*[-\u2013]\s*(?:\d+|end)\s*\.?\s*$", r"\1", s,
               flags=re.I)
    s = s.replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip().rstrip(".").strip()
    if not s:
        raise ValueError(f"empty citation: {printed!r}")

    # Split the trailing chapter/verse numerals off the book name.
    m = re.match(
        r"^(?P<book>.*?)[ ,.]+(?P<nums>[0-9ivxlcdmIVXLCDM]+\.?(?:[ .][0-9ivxlcdmIVXLCDM]+\.?)?)$",
        s)
    if not m:
        raise ValueError(f"unparsed citation: {printed!r}")

    book_raw = m.group("book").strip().rstrip(".").strip()
    key = re.sub(r"[.,]", "", book_raw).lower().strip()
    key = re.sub(r"\s+", " ", key)
    if key not in BOOKS:
        raise ValueError(f"unknown book abbreviation {book_raw!r} in {printed!r}")
    book = BOOKS[key]

    parts = [p for p in re.split(r"[ .]+", m.group("nums")) if p]
    nums = [_number(p) for p in parts]
    if any(n is None for n in nums):
        raise ValueError(f"unparsed chapter/verse in {printed!r}")
    if len(nums) == 1:
        return f"{book} {nums[0]}"
    return f"{book} {nums[0]}:{nums[1]}"


SELF_CHECK = {
    "Rom. xiii.": "Romans 13",
    "Rom. xiii. 8.": "Romans 13:8",
    "Rom. 13.8.": "Romans 13:8",
    "Rom. 13.8. [-14]": "Romans 13:8",
    "Romans 13.8-14": "Romans 13:8",
    "St. Matt. xxi. 1.": "Matthew 21:1",
    "St. Matthew 21.1-13": "Matthew 21:1",
    "The Gospell. Matt. xxi.": None,      # label must be stripped by the caller
    "1 Cor. iv.": "1 Corinthians 4",
    "1 St. John iii. 1.": "1 John 3:1",
    "Apoc. xiv.": "Revelation 14",
    "Isaiah lxi. 1.": "Isaiah 61:1",
    "Philippians ii. 9.": "Philippians 2:9",
    "Luc. ii.": "Luke 2",
    "Coloss. iii.": "Colossians 3",
    "Heb. 1. 1.": "Hebrews 1:1",          # source prints arabic 1 for roman i
}


def _self_check():
    bad = 0
    for printed, want in SELF_CHECK.items():
        if want is None:
            continue
        try:
            got = canonical(printed)
        except ValueError as exc:
            print(f"  FAIL {printed!r}: {exc}")
            bad += 1
            continue
        if got != want:
            print(f"  FAIL {printed!r}: got {got!r}, want {want!r}")
            bad += 1
    print("w10_cite self-check:", "OK" if not bad else f"{bad} failure(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(_self_check())
    for arg in sys.argv[1:]:
        print(f"{arg!r} -> {canonical(arg)!r}")
