#!/usr/bin/env python3
"""w15_addw.py — record witness corrections for the tables of lessons.

Authoring-only helper for the witness pass. Reads lines on stdin:

    SEC IDX FIELD | SCAN READING | BOOK PAGE [| VERIFY NOTE]

where SEC is cy / fh / so, IDX the row index as printed by w15_show.py, and
FIELD 1..6 (the column, in printed order) or 0 for the row label. For each it
looks up the row's week, label and CURRENT (text-layer) reading and appends a
complete entry to w15_lessons_witness.json, so the text-layer reading an entry
claims to correct is copied from the parse, never retyped.
"""
import contextlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w15_lessons as L

PATH = os.path.join(HERE, "w15_lessons_witness.json")
BOOK_TO_SCAN = {}          # book page -> scan page, filled below
for n, pages in enumerate([("x", "xi"), ("xii", "xiii"), ("xiv", "xv"),
                           ("xvi", "xvii"), ("xviii", "xix"), ("xx", "xxi"),
                           ("xxii", "xxiii"), ("xxiv", "xxv"),
                           ("xxvi", "xxvii"), ("xxviii", "xxix")], start=6):
    for p in pages:
        BOOK_TO_SCAN[p] = n


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        recs, _notes = L.main(write_file=False)
    by = {sec: [r for r in recs if r["sec"] == sec and "label" in r]
          for sec in ("cy", "fh", "so")}
    have = json.load(open(PATH)) if os.path.exists(PATH) else []
    added = 0
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        head, scan, book, *rest = [x.strip() for x in line.split("|")]
        sec, idx, field = head.split()
        r = by[sec][int(idx)]
        field = int(field)
        if field == 0:
            fname, cur = "label", r["label"]
        else:
            fname, cur = r["fields"][field - 1]
        e = {"sec": sec, "week": r["week"], "row": r["orig"], "dup": r["dup"],
             "field": fname,
             "text_layer": cur, "scan": scan, "book": book,
             "page": BOOK_TO_SCAN[book]}
        if rest and rest[0]:
            e["verify"] = rest[0]
        if any(x["sec"] == sec and x["week"] == e["week"] and x["row"] == e["row"]
               and x.get("dup", 0) == e["dup"] and x["field"] == fname
               for x in have):
            raise SystemExit("already recorded: %s" % line)
        if cur == scan:
            raise SystemExit("no change: %s" % line)
        have.append(e)
        added += 1
        print("%-26s %-12s %-9s %r -> %r" % ((e["week"] or "")[:26], e["row"][:12],
                                          fname, cur, scan))
    json.dump(have, open(PATH, "w"), indent=1, ensure_ascii=False)
    print("added %d (total %d)" % (added, len(have)))


if __name__ == "__main__":
    main()
