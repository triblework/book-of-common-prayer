#!/usr/bin/env python3
"""w14_build_proper.py — tables/proper-lessons.md per edition (Wave 14).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

The Tables of Proper Lessons appoint the readings for Sundays, Holy Days and
(in the American books) the weekdays of Lent, the Rogation and Ember Days --
the days on which the Kalendar's ordinary course is set aside.

THE STRUCTURE. Like the Kalendar, these tables emit each COLUMN as one <td>
with <br>-separated entries, so a row is recovered by zipping columns. The
occasion column carries the section's own heading as LEADING fragments before
the occasion labels:

    col0: ['Sundays after', 'the Epiphany', 'The first', '2', '3', '4', '5']
    col1: ['44', '51', '55', '57', '59']

The number of heading fragments is therefore exactly len(occasions) minus
len(lessons) -- a structural fact, not a guess about which entries "look like"
a heading. The lesson columns must agree in length or the table is reported.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))

import w14_kalendar as K

# 1892's Lent table numbers its occasions ("1. Ash-wednesd'y", "2. Thursday").
# A bare digit + period is a sentence boundary to sentence_split.py, so the
# printed ordinal becomes its own leading field -- preserved exactly, with only
# its list period moved (the same treatment the 1979 Various Occasions get).
ORDINAL = re.compile(r"^(\d+)\.\s+(.*)$")

J = "http://justus.anglican.org/resources/bcp/"
EMPTY = "—"
VERIFY_JSON = os.path.join(HERE, "wave14_proper_verifies.json")

# (url, start, end) -- the slice of the page holding the proper-lesson tables.
# RECORDED GAP -- 1549, 1552 and 1559 are deliberately absent here.
# Those books print their proper lessons not as one uniform table but as some
# thirty SMALL per-occasion tables whose column heights vary with the occasion
# (Whitsunday 2/5/5, Christmas 1/3/2, Sundays after Trinity 27/26/26). No single
# row model fits them: zipping by index misaligns the small tables, and applying
# the zip only where it succeeds recovers 47 of them and silently drops the
# rest -- which would publish a file that reads as "1559 appointed proper
# lessons for these 47 occasions only", a false historical claim. Per the prime
# directive the gap is recorded in NOTICE.md and SOURCES.md instead.
SOURCES = {
    "1789": (J + "1789/FrontMatter_1789.htm",
             r'name="TABLES of LESSONS"', r'name="Calendar"'),
    "1892": (J + "1892/Lectionary_1892.htm",
             r"TABLES OF LESSONS|PROPER LESSONS", r'name="Calendar"'),
}

LABELS = {
    3: ["Morning", "Evening"],
    5: ["Morning 1", "Morning 2", "Evening 1", "Evening 2"],
}


def slice_page(edition):
    import scrape
    url, start, end = SOURCES[edition]
    h = scrape.fetch(url)
    m = re.search(start, h)
    if not m:
        raise SystemExit("%s: start %r not found" % (edition, start))
    tail = h[m.start():]
    e = re.search(end, tail[1:])
    return tail[:e.start() + 1] if e else tail


HEADINGISH = re.compile(r"<(?:p|td)[^>]*>(.*?)</(?:p|td)>", re.S | re.I)


def _title_before(seg, pos):
    """The nearest short, heading-like block before `pos`."""
    best = None
    for m in HEADINGISH.finditer(seg, 0, pos):
        txt = K._clean(m.group(1))
        # The nearest preceding block is usually a COLUMN HEADER ("2d Lesson.",
        # "EVENING."), so the title is identified by naming itself a table --
        # every one of these does ("A TABLE OF LESSONS FOR SUNDAYS").
        if 4 < len(txt) < 90 and re.search(r"\bTABLE\b", txt, re.I):
            best = txt
    return best or ""


def tables(edition):
    """-> [(heading, [(occasion, [values]), ...], labels, dropped)]"""
    seg = slice_page(edition)
    out = []
    # A table's TITLE ("A TABLE OF LESSONS FOR SUNDAYS") is printed in a
    # preceding single-cell row, not inside the occasion column, so it must be
    # carried forward. Without it every table landed under one anchor and the
    # five-column Sundays table sat beside the three-column Holy-Days table as
    # if they were one -- which the audit gate caught as a column-shape split.
    # Titles appear EITHER in a preceding single-cell row (1789) OR in a <p>
    # element between the tables (1892), so the lookup must be position-aware:
    # take the nearest short heading-like block before this row. Using only the
    # single-cell form gave all three 1892 tables the same title, which the
    # audit gate caught as three differently-shaped tables under one anchor.
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", seg, re.S | re.I):
        cells = K.row_cells(m.group(1))
        if len(cells) == 1:
            continue
        if len(cells) not in LABELS:
            continue
        pending = _title_before(seg, m.start())
        cols = [K.cell_entries(c) for c in cells]
        if max(len(c) for c in cols) < 5:
            continue
        lesson_cols = cols[1:]
        lens = [len(c) for c in lesson_cols]
        modal = max(set(lens), key=lens.count)
        labels = LABELS[len(cells)]
        dropped = [labels[i] for i, n in enumerate(lens) if n != modal]
        keep_idx = [i for i, n in enumerate(lens) if n == modal]
        occ = cols[0]
        nhead = len(occ) - modal
        if nhead < 0:
            continue                     # not a proper-lesson table
        heading = " ".join(x for x in occ[:nhead] if x).strip() or pending or ""
        rows = []
        for r in range(modal):
            name = occ[nhead + r].strip()
            vals = [(labels[i], lesson_cols[i][r].strip()) for i in keep_idx]
            rows.append((name, vals))
        out.append((heading, rows, [labels[i] for i in keep_idx], dropped))
    return out


def build(edition, verifies):
    tabs = tables(edition)
    lines = ["# Tables of Proper Lessons", ""]
    n = 0
    for heading, rows, labels, dropped in tabs:
        lines += ["## " + (heading or "Proper Lessons"), ""]
        if dropped:
            key = "%s: %s" % (heading or "Proper Lessons", ", ".join(dropped))
            note = ("the source column(s) %s do not match the height of the "
                    "others in this table, so they are omitted rather than "
                    "aligned on a guess" % ", ".join(dropped))
            lines += ["<!-- VERIFY: '%s'; %s -->" % (key, note), ""]
            verifies.append({"edition": edition,
                             "service": "tables/proper-lessons",
                             "anchor": heading or "Proper Lessons",
                             "source_reading": key, "note": note})
        for name, vals in rows:
            if not name and not any(v for _l, v in vals):
                continue
            # As in the Kalendar, a TERMINAL period is dropped: it is
            # typography, and a period before " | " is a sentence boundary.
            mo = ORDINAL.match(name)
            fields = ([mo.group(1), mo.group(2).rstrip(".")] if mo
                      else [name.rstrip(".") or EMPTY])
            for label, v in vals:
                fields.append("%s: %s" % (label, v.rstrip(".") or EMPTY))
            lines.append(" | ".join(fields))
            n += 1
        lines.append("")
    return lines, n, len(tabs)


def main():
    verifies = []
    for ed in sorted(SOURCES):
        try:
            lines, n, t = build(ed, verifies)
        except SystemExit as exc:
            print("%-5s SKIPPED -- %s" % (ed, exc))
            continue
        if n == 0:
            print("%-5s no proper-lesson tables recovered" % ed)
            continue
        p = os.path.join(WT, "editions", ed, "tables", "proper-lessons.md")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).rstrip("\n")) + "\n"
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("%-5s rows=%3d tables=%2d" % (ed, n, t))
    with open(VERIFY_JSON, "w", encoding="utf-8") as fh:
        json.dump(verifies, fh, indent=1)
    print("verify manifest: %d" % len(verifies))


if __name__ == "__main__":
    main()
