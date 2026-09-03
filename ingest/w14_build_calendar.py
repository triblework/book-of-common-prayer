#!/usr/bin/env python3
"""w14_build_calendar.py — write tables/calendar.md per edition (Wave 14).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

Editions written: 1549, 1552, 1559, 1789.

RECORDED GAPS (never reconstructed):
  * 1604 -- no allow-listed 1604 source exists (the Wave-10 precedent).
  * 1662 -- the Church of England serves only the post-1922 recension of the
    Kalendar (WAVE14_SCOPING §1.1), so 1662's own table is unobtainable.
  * 1892 -- the justus HTML has LOST the table's row structure: several days
    are packed into one <br> slot ("5 6 7") with the packing differing column
    by column and continuation lines interleaved. There is no structural
    discriminator that recovers per-day rows, and a wrong reconstruction would
    silently misdate a year of lessons.
  * 1928 -- its Kalendar is PDF-only and, unlike its predecessors, prints NO
    lesson columns (1928 moved the lessons into a separate table).
Each gap is carried in provenance as `inherited-unreviewed` and stated in
NOTICE.md and SOURCES.md, so a reader cannot mistake inheritance-by-omission
for "this edition reprinted its parent's table unchanged" (GUIDE ruling D).
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

EMPTY = "—"

EDITIONS = ["1549", "1552", "1559", "1789"]
VERIFY_JSON = os.path.join(HERE, "wave14_calendar_verifies.json")


def cell_path(edition):
    return os.path.join(WT, "editions", edition, "tables", "calendar.md")


def build(edition, verifies):
    html = K.fetch(edition)
    rows = K.rows_for(edition, html)
    raw_holy, _short = K.holy_days(edition, html)
    holy, _joined = K.join_holy_days(raw_holy, edition)

    lines = ["# The Kalendar", ""]
    month = None
    dropped_seen = set()
    labels = [l for _j, l in K._emitted(edition)]
    for m, day, vals, dropped in rows:
        if m != month:
            month = m
            lines += ["## " + m, ""]
        # Stable column order (spec §10). The Holy Day goes LAST because its
        # printed form often ends in an abbreviating period ("Circumci."), and
        # a period followed by " | " is a sentence boundary to
        # sentence_split.py, which would break the row in half (GUIDE §3.1).
        # At end of line the same period is harmless.
        fields = ["%s %d" % (m, day)]
        got = dict(vals)
        for label in labels:
            v = (got.get(label) or "").strip()
            if not v:
                fields.append("%s: %s" % (label, EMPTY))
                continue
            # Citations are carried EXACTLY AS THE EDITION PRINTS THEM
            # ("Gene. 17", not "Genesis 17"). That is the repo's standing rule:
            # editions/ holds period spelling and tools/normalize.py does the
            # spelling work downstream in texts/normalized/. Canonicalizing here
            # would flatten 1552's "Gene." and 1789's "Gen." into one form and
            # quietly destroy a real orthographic difference between editions.
            #
            # The Kalendar also ELIDES the book name on continuation days: after
            # "Gene. 1" a bare "3" means Genesis 3. That is the book's own
            # convention and is likewise left as printed.
            # A citation's TERMINAL period is dropped ("Gen. 1." -> "Gen. 1").
            # It is typography, not a reading: what follows in the row is
            # another column, and a period before " | " is a sentence boundary
            # to sentence_split.py, which would break the row in half. Interior
            # periods (the abbreviation marks) are untouched.
            fields.append("%s: %s" % (label, v.rstrip(".")))
        fields.append("Kalendar Note: " + (holy.get((m, day)) or EMPTY))
        lines.append(" | ".join(fields))
        if dropped and (edition, m) not in dropped_seen:
            dropped_seen.add((edition, m))
            key = "%s %s" % (m, ", ".join(dropped))
            note = ("the source column(s) %s carry one entry fewer than this "
                    "month has days, so they are omitted for %s rather than "
                    "aligned on a guess, which would misdate every following "
                    "day of the month" % (", ".join(dropped), m))
            lines.append("<!-- VERIFY: '%s'; %s -->" % (key, note))
            verifies.append({"edition": edition, "service": "tables/calendar",
                             "anchor": m, "source_reading": key, "note": note})
    return lines


def main():
    verifies = []
    for ed in EDITIONS:
        lines = build(ed, verifies)
        p = cell_path(ed)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).rstrip("\n")) + "\n"
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        body = text.split("\n")
        print("%s  rows=%3d  months=%2d  holydays=%2d  verify=%d"
              % (ed, sum(1 for l in body if " | " in l),
                 sum(1 for l in body if l.startswith("## ")),
                 sum(1 for l in body if "Kalendar Note:" in l and EMPTY not in l.split("Kalendar Note:")[1]),
                 sum(1 for l in body if l.startswith("<!-- VERIFY"))))
    with open(VERIFY_JSON, "w", encoding="utf-8") as fh:
        json.dump(verifies, fh, indent=1)
    print("verify manifest: %d items" % len(verifies))


if __name__ == "__main__":
    main()
