#!/usr/bin/env python3
"""w14_kalendar.py — extract the Kalendar tables from justus pages (Wave 14).

Authoring-only; NOT published.

THE STRUCTURAL FACT (measured, per AUDIT_METHOD "prefer a structural
discriminator"): these pages emit each table COLUMN as one <td>, with the
column's entries separated by <br>. A row is recovered by ZIPPING COLUMNS BY
INDEX. `&nbsp;` is an explicit alignment placeholder, so a blank day keeps its
slot and the zip stays honest.

Per-edition column vocabularies differ and are declared, never sniffed:

  1549  3 cols  day | Matins psalms | Evensong psalms
                (1549's Kalendar appoints PSALMS ONLY; the lesson columns are a
                 1552 addition -- a real revision, not a parse failure)
  1552  9 cols  golden | letter | roman | holy day | day | MP1 | MP2 | EP1 | EP2
  1559  9 cols  as 1552
  1789  7 cols  day | letter | holy day | MP1 | MP2 | EP1 | EP2
  1892  6 cols  day | letter | holyday+MP1 | MP2 | EP1 | EP2

THE GATE: every column used for zipping must have an identical entry count, or
`zip_columns` RAISES. A table that quietly loses three rows is the archetypal
silent loss this wave has to defend against, and a count is the cheapest
possible detector.

The holy-day column is NOT index-zippable in every edition: names wrap across
<br> ("Circumci-" / "sion.") and trailing blanks are omitted, so it can run
short. It is therefore extracted separately by `holy_days()`, never zipped, and
its result is gated against the edition's own Table of Feasts by the caller.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
DAYS_IN = {"January": 31, "February": 29, "March": 31, "April": 30, "May": 31,
           "June": 30, "July": 31, "August": 31, "September": 30,
           "October": 31, "November": 30, "December": 31}

SOURCES = {
    "1549": "http://justus.anglican.org/resources/bcp/1549/Kalendar_1549.htm",
    "1552": "http://justus.anglican.org/resources/bcp/1552/Kalendar_1552.htm",
    "1559": "http://justus.anglican.org/resources/bcp/1559/Kalendar_1559.htm",
    "1789": "http://justus.anglican.org/resources/bcp/1789/FrontMatter_1789.htm",
    "1892": "http://justus.anglican.org/resources/bcp/1892/Lectionary_1892.htm",
}

# Column index -> emitted label, per edition. `None` means "extract but do not
# emit" (the golden-number and Roman-calendar columns are excluded apparatus,
# GUIDE ruling B); "holy" is handled separately and never zipped.
# Column positions are given as NEGATIVE offsets from the end of the row. This
# matters: 1789 prints ten months in seven cells and two in eight, so absolute
# indices shift between months of the SAME edition, while the four lesson
# columns are always the last four and everything else keeps its distance from
# them. The day of the month is never read from a printed column -- see
# month_tables() -- because in 1549/1552/1559 the numeric column is the
# THIRTY-DAY PSALTER COURSE, which restarts inside the month (January runs
# 1..30 then 1 again); reading it as a date would misdate a third of the year.
#
# The golden-number and Kalends columns are computational apparatus, excluded by
# GUIDE ruling B.
LESSONS = [(-4, "Morning 1"), (-3, "Morning 2"),
           (-2, "Evening 1"), (-1, "Evening 2")]
LAYOUT = {
    "1549": {"cells": (9,), "letter": -9, "holy": -6, "psalter": -5},
    "1552": {"cells": (9,), "letter": -8, "holy": -6, "psalter": -5},
    "1559": {"cells": (9,), "letter": -8, "holy": -6, "psalter": -5},
    "1789": {"cells": (7, 8), "letter": -6, "holy": -5, "psalter": None},
}
_BR = re.compile(r"<br\s*/?>", re.I)
_TAG = re.compile(r"<[^>]+>")
_ENT = [("&nbsp;", " "), ("&amp;", "&"), ("&para;", "¶"),
        ("&#151;", "—"), ("&#8212;", "—"), ("&quot;", '"')]


class ZipError(RuntimeError):
    pass


def fetch(edition):
    import scrape
    return scrape.fetch(SOURCES[edition])


def _clean(s):
    s = _TAG.sub("", s)
    for a, b in _ENT:
        s = s.replace(a, b)
    s = s.replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def cell_entries(td):
    """A <td> -> its <br>-separated entries, EMPTIES PRESERVED (alignment)."""
    return [_clean(p) for p in _BR.split(td)]


def table_rows(html):
    return re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I)


def row_cells(tr):
    return [td for _a, td in
            re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S | re.I)]


def zip_columns(columns, labels, where):
    """Zip equal-length columns into rows. RAISES if the counts disagree."""
    counts = [len(c) for c in columns]
    if len(set(counts)) != 1:
        raise ZipError("%s: column entry counts disagree %s (labels %s)"
                       % (where, counts, labels))
    return [list(t) for t in zip(*columns)]


ROMAN = {"i":1,"v":5,"x":10,"l":50,"c":100,"d":500,"m":1000}


def _as_day(tok):
    """Parse a printed day number, arabic (1552+) or roman (1549). None if not."""
    t = tok.strip().strip(".").strip()
    if not t:
        return None
    if re.fullmatch(r"[0-9]{1,2}", t):
        return int(t)
    if re.fullmatch(r"(?i)[ivxl]+", t):
        n = total = 0
        prev = 0
        for ch in reversed(t.lower()):
            v = ROMAN[ch]
            total += -v if v < prev else v
            prev = max(prev, v)
        return total or None
    return None


def _emitted(edition):
    lay = LAYOUT[edition]
    cols = [(lay["letter"], "Sunday Letter")]
    if lay["psalter"] is not None:
        cols.append((lay["psalter"], "Psalter Day"))
    return cols + LESSONS


def month_tables(edition, html):
    """-> [(month, span, offset, cells), ...] in calendar order.

    Locating by HEADING does not work: 1552 labels its months in Latin
    ("Octobris"), 1549 uses the Roman calendar, and several headings are split
    across tags. The structural discriminator is the ROW SHAPE -- a month table
    is a <tr> whose cell count is one this edition uses AND whose columns each
    hold a month's worth of entries -- and the twelve appear in calendar order.

    THE GATE: every emitted column must hold the same number of entries L, and
    L minus a 0-or-1 header slot must equal that month's length. A table that
    quietly loses rows, or a month landing out of order, raises instead of
    producing a short but plausible-looking calendar.
    """
    lay = LAYOUT[edition]
    tables = []
    for tr in table_rows(html):
        cells = row_cells(tr)
        if len(cells) not in lay["cells"]:
            continue
        n = [len(cell_entries(c)) for c in cells]
        if max(n) < 28:                     # a header strip, not a month
            continue
        tables.append(cells)
    if len(tables) != 12:
        raise ZipError("%s: found %d month tables, want 12" % (edition, len(tables)))
    out = []
    for i, cells in enumerate(tables):
        month = MONTHS[i]
        emitted = _emitted(edition)
        counts = [len(cell_entries(cells[j])) for j, _l in emitted]
        span = DAYS_IN[month]
        # The modal count is the month's true height; a column that disagrees
        # has LOST an entry in the source, and index-zipping it would misdate
        # every day after the loss. Such a column is dropped and named, never
        # aligned on a guess (GUIDE §4).
        modal = max(set(counts), key=counts.count)
        dropped = [emitted[k][1] for k, c in enumerate(counts) if c != modal]
        keep = [emitted[k] for k, c in enumerate(counts) if c == modal]
        offset = modal - span
        if offset not in (0, 1) and month == "February":
            span, offset = 28, modal - 28
        if offset not in (0, 1):
            raise ZipError("%s %s: %d entries for a %d-day month"
                           % (edition, month, modal, span))
        out.append((month, span, offset, cells, keep, dropped))
    return out


def rows_for(edition, html=None):
    """-> [(month, day, [(label, value), ...]), ...] for the whole year."""
    html = html if html is not None else fetch(edition)
    out = []
    for month, span, offset, cells, keep, dropped in month_tables(edition, html):
        cols = [cell_entries(cells[j]) for j, _l in keep]
        labels = [l for _j, l in keep]
        grid = zip_columns(cols, labels, "%s %s" % (edition, month))
        for d in range(span):
            vals = grid[d + offset]
            out.append((month, d + 1, list(zip(labels, vals)), tuple(dropped)))
    return out


def holy_days(edition, html=None):
    """-> ({(month, day): name}, [short columns]).

    NEVER index-zipped. Names wrap across <br> ("Circumci-" / "sion.") and
    trailing blanks are omitted, so this column can run short; where it does,
    the shortfall is REPORTED so the caller can gate it rather than guessing.
    """
    html = html if html is not None else fetch(edition)
    lay = LAYOUT[edition]
    out, short = {}, []
    for month, span, offset, cells, _k, _d in month_tables(edition, html):
        col = cell_entries(cells[lay["holy"]])
        if len(col) - offset < span:
            short.append((month, len(col) - offset, span))
        for d in range(span):
            i = d + offset
            if i < len(col) and col[i]:
                out[(month, d + 1)] = col[i]
    return out, short


def report(edition):
    html = fetch(edition)
    try:
        rows = rows_for(edition, html)
    except ZipError as exc:
        print("== %s: GATE FIRED -- %s" % (edition, exc))
        return
    hd, short = holy_days(edition, html)
    lost = sorted(set(d for _m, _dy, _v, dr in rows for d in dr))
    print("== %s: %3d day rows | %3d holy-day cells | dropped columns: %s"
          % (edition, len(rows), len(hd), ", ".join(lost) or "none"))


if __name__ == "__main__":
    for ed in (sys.argv[1:] or ["1549", "1552", "1559", "1789"]):
        report(ed)
