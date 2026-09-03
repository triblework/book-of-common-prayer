#!/usr/bin/env python3
"""w14_cite.py — canonicalize a calendar / lectionary citation (Wave 14).

Authoring-only; NOT published. EXTENDS `w10_cite` rather than modifying it, so
Wave 10 cannot regress. See ingest/WAVE14_GUIDE.md §3.2.

Two things Wave 10 never needed:

1. **The whole Bible.** Wave 10 carried Epistles and Gospels, so `w10_cite.BOOKS`
   has no Samuel, Chronicles, Joshua, Judges, Nehemiah, Lamentations, Esdras or
   Maccabees. The daily calendar reads through the entire canon plus the
   Apocrypha, so EXTRA_BOOKS below completes the table.

2. **Partial-chapter extents.** The calendar prints spans Wave 10 never met:

       "Gen. 9 to v. 20"     -> "Genesis 9 to v. 20"
       "Eze. 20 v. 27"       -> "Ezekiel 20 v. 27"
       "Mal. 3 & 4"          -> "Malachi 3 & 4"
       "Luke 4 v.14 to 33"   -> "Luke 4 v. 14 to 33"
       "Jude."               -> "Jude"

   The extent is PRESERVED AS PRINTED, never expanded: "Genesis 9 to v. 20" and
   not "Genesis 9:1-20", because the book does not print verse 1 and the extent
   is exactly where revision between editions shows.

Trailing periods are stripped — `sentence_split.py` splits on `.` + whitespace
and would otherwise break a row in half (GUIDE §3.1).

An unrecognized book still RAISES, so a new printed form fails the build instead
of being silently invented.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w10_cite

# Forms the calendar/lectionary prints that Wave 10 never met. Additive only.
EXTRA_BOOKS = {
    "josh": "Joshua", "joshua": "Joshua", "jos": "Joshua",
    "judg": "Judges", "judges": "Judges", "judge": "Judges",
    "ruth": "Ruth",
    "sam": "Samuel", "samuel": "Samuel",
    "1 sam": "1 Samuel", "2 sam": "2 Samuel",
    "1 samuel": "1 Samuel", "2 samuel": "2 Samuel",
    "chron": "Chronicles", "chronicles": "Chronicles", "chro": "Chronicles",
    "1 chron": "1 Chronicles", "2 chron": "2 Chronicles",
    "ezra": "Ezra", "esdras": "Esdras",
    "1 esdras": "1 Esdras", "2 esdras": "2 Esdras",
    "neh": "Nehemiah", "nehemiah": "Nehemiah",
    "esth": "Esther", "esther": "Esther",
    "job": "Job",
    "ps": "Psalm", "psa": "Psalm", "psal": "Psalm", "psalm": "Psalm",
    "psalms": "Psalm",
    "eccl": "Ecclesiastes", "eccle": "Ecclesiastes",
    "song": "Song of Solomon", "canticles": "Song of Solomon",
    "lam": "Lamentations", "lament": "Lamentations",
    "eze": "Ezekiel", "ezec": "Ezekiel", "ezech": "Ezekiel",
    "hos": "Hosea", "obad": "Obadiah", "jon": "Jonah",
    "mic": "Micah", "nah": "Nahum", "hagg": "Haggai",
    "zac": "Zechariah", "zec": "Zechariah",
    "macc": "Maccabees", "1 macc": "1 Maccabees", "2 macc": "2 Maccabees",
    "tob": "Tobit", "jud": "Judith", "judith": "Judith",
    "susanna": "Susanna", "bel": "Bel and the Dragon",
    "manasses": "Prayer of Manasses",
    "apoc": "Revelation", "apocalips": "Revelation",
    "apocalypse": "Revelation", "revelation": "Revelation",
    "philip": "Philippians", "phili": "Philippians",
    "colos": "Colossians", "coloss": "Colossians",
    "thes": "Thessalonians", "1 thes": "1 Thessalonians",
    "2 thes": "2 Thessalonians",
    "act": "Acts",
}

BOOKS = dict(w10_cite.BOOKS)
BOOKS.update(EXTRA_BOOKS)

# Books the calendar prints with no chapter number.
_NO_CHAPTER = {"Jude", "2 John", "3 John", "Philemon", "Obadiah",
               "Prayer of Manasses", "Susanna", "Bel and the Dragon"}

_ORD = r"(?:(?P<ord>[123lI])\s*\.?\s+)?"
_BOOK = r"(?P<book>(?:St\.?\s+)?[A-Za-z]+\.?)"
_CH = r"(?P<ch>[0-9]+|[ivxlcIVXLC]+)"
_HEAD = re.compile(r"^\s*" + _ORD + _BOOK + r"\.?\s*(?:" + _CH + r")?\b")

# OCR: lowercase L standing in for the digit 1 (the 1789 page does this).
_OCR_L = re.compile(r"(?<![A-Za-z])l(?=[0-9])"
                    r"|(?<![A-Za-z])l(?=\s+(?:Kings|Sam|Chron|Cor|Thess|Tim|Pet|John|Esdras))")


class CiteError(ValueError):
    pass


def _norm_extent(rest):
    """Normalize whitespace inside a printed extent without changing its words."""
    s = rest.strip().rstrip(".").strip()
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\bver\.?\s*", "v. ", s)
    s = re.sub(r"\bv\.?\s*(?=[0-9])", "v. ", s)
    s = re.sub(r"\s*&\s*", " & ", s)
    return re.sub(r"\s+", " ", s).strip()


def canonical(printed):
    """Canonicalize one printed citation. Raises CiteError on an unknown book."""
    if printed is None:
        raise CiteError("empty citation")
    s = printed.replace("\xa0", " ").replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if not s or s in {"-", "--", "—"}:
        raise CiteError("empty citation: %r" % printed)
    s = _OCR_L.sub("1", s)

    m = _HEAD.match(s)
    if not m:
        raise CiteError("unparsed citation: %r" % printed)

    raw_book = m.group("book").rstrip(".").strip()
    key = re.sub(r"^St\.?\s+", "st ", raw_book, flags=re.I).lower().strip()
    ordn = m.group("ord")
    if ordn in ("l", "I"):
        ordn = "1"

    book = None
    if ordn:
        book = BOOKS.get("%s %s" % (ordn, key))
    if book is None:
        book = BOOKS.get(key)
    if book is None:
        raise CiteError("unknown book abbreviation %r in %r"
                        % (("%s %s" % (ordn, key)).strip(), printed))
    if ordn and not book[0].isdigit():
        book = "%s %s" % (ordn, book)

    ch = m.group("ch")
    rest = _norm_extent(s[m.end():])

    if ch is None:
        if book not in _NO_CHAPTER and not rest:
            raise CiteError("citation has no chapter: %r" % printed)
        return ("%s %s" % (book, rest)).strip()

    if re.fullmatch(r"[0-9]+", ch):
        num = int(ch)
    else:
        num = w10_cite.roman_to_int(ch)
        if not num:
            raise CiteError("bad chapter numeral %r in %r" % (ch, printed))

    out = "%s %d" % (book, num)
    if rest:
        out += rest if rest.startswith(":") else " " + rest
    return out.strip()


def try_canonical(printed):
    """Return (canonical, None) or (None, reason)."""
    try:
        return canonical(printed), None
    except CiteError as exc:
        return None, str(exc)


_CASES = {
    "Gen. 1.": "Genesis 1",
    "Matt. 1": "Matthew 1",
    "Gen. 9 to v. 20": "Genesis 9 to v. 20",
    "Isa. 20 to v.27": "Isaiah 20 to v. 27",
    "Eze. 20 v. 27": "Ezekiel 20 v. 27",
    "Mal. 3 & 4": "Malachi 3 & 4",
    "1 Sam. 12": "1 Samuel 12",
    "l Kings 8 to v. 22": "1 Kings 8 to v. 22",
    "2 Kings 5": "2 Kings 5",
    "Prov 1": "Proverbs 1",
    "Joel 3 v. 9": "Joel 3 v. 9",
    "Deut. 4 to v. 41": "Deuteronomy 4 to v. 41",
    "Jude.": "Jude",
    "Luke 4 v.14 to 33": "Luke 4 v. 14 to 33",
    "Rom. xiii.": "Romans 13",
    "St. Matt. xxi.": "Matthew 21",
    "Jos. 23": "Joshua 23",
    "Judges 4": "Judges 4",
    "2 Sam. 19": "2 Samuel 19",
    "Lam. 1": "Lamentations 1",
    "Hag. 2 to v. 10": "Haggai 2 to v. 10",
    "Ecclus. 2": "Ecclesiasticus 2",
    "Neh. 8": "Nehemiah 8",
    "1 Chron. 29": "1 Chronicles 29",
}


def _self_check():
    bad = 0
    for src, want in _CASES.items():
        got, err = try_canonical(src)
        if got != want:
            print("FAIL %-22r got %r want %r (%s)" % (src, got, want, err))
            bad += 1
    print("w14_cite self-check: %d/%d" % (len(_CASES) - bad, len(_CASES)))
    return bad


if __name__ == "__main__":
    sys.exit(1 if _self_check() else 0)
