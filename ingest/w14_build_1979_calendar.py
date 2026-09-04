#!/usr/bin/env python3
"""w14_build_1979_calendar.py — the 1979 Kalendar cell (Wave 14).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

CORRECTS AN EARLIER RULING. The wave's first pass put `tables/calendar.md` in
`absent:` at 1979, on the reasoning that 1979 had abolished the civil-date
Kalendar in favour of a lectionary keyed to the liturgical week. That is wrong.
1979's "The Calendar of the Church Year" (bcpoffce.txt, pp. 15-33) prints a
full twelve-month, day-by-day Kalendar -- day number, Sunday letter and
commemoration -- and drops only the four LESSON columns, which move into the
two-year Daily Office Lectionary.

So 1979 belongs on the same path, and `git diff v1789 v1979 -- .../calendar.md`
becomes a flagship: the lesson columns vanish, the days and Sunday letters
persist, the sanctoral changes almost entirely. Marking it absent would have
asserted something the book contradicts and thrown that diff away.
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

URL = "http://justus.anglican.org/resources/bcp/bcpoffce.txt"
OUT = os.path.join(WT, "editions", "1979", "tables", "calendar.md")
EMPTY = "—"

# A day line is "<day> <letter>[ : entry]", optionally preceded by the GOLDEN
# NUMBER in the left margin ("14 22 d : James De Koven..."). Missing that
# margin column dropped seven of March's days and fired the day-count gate.
# The golden number is computational apparatus and is not emitted (ruling B).
DAY = re.compile(r"^\s*(?:(\d{1,2})\s+)?(\d{1,2})\s+([A-Ga-g])\s*(?::\s*(.*))?$")
PAGE = re.compile(r"^<page \d+>\s*$")
MONTH = re.compile(r"^\*(%s)\*\s*$" % "|".join(K.MONTHS))


def parse():
    import scrape
    t = scrape.fetch(URL)
    i = t.find("<The Calendar\nof the Church Year>")
    if i < 0:
        raise SystemExit("1979: Calendar of the Church Year not found")
    j = t.find("*January*", i)
    k = t.find("<", t.find("*December*", j))
    lines = t[j:k].split("\n")

    out = []
    month = None
    cur = None
    for l in lines:
        m = MONTH.match(l.strip())
        if m:
            month, cur = m.group(1), None
            continue
        if PAGE.match(l.strip()):
            continue
        d = DAY.match(l)
        if d:
            cur = {"month": month, "day": int(d.group(2)),
                   "letter": d.group(3), "entry": (d.group(4) or "").strip()}
            out.append(cur)
            continue
        # A long commemoration wraps to column 0; it continues the day above.
        if l.strip() and cur is not None:
            cur["entry"] = (cur["entry"] + " " + l.strip()).strip()
    return out


def main():
    rows = parse()
    # GATE: twelve months, each a consecutive run 1..N of the right length.
    seen = {}
    for r in rows:
        seen.setdefault(r["month"], []).append(r["day"])
    if len(seen) != 12:
        raise SystemExit("1979 calendar: %d months, want 12" % len(seen))
    for m, days in seen.items():
        want = K.DAYS_IN[m] if m != "February" else max(days)
        if days != list(range(1, len(days) + 1)) or len(days) != want:
            raise SystemExit("1979 calendar: %s has %d days %s, want 1..%d"
                             % (m, len(days), days[:4], want))

    lines = ["# The Kalendar", ""]
    month = None
    for r in rows:
        if r["month"] != month:
            month = r["month"]
            lines += ["## " + month, ""]
        entry = r["entry"].replace("*", "").strip()
        lines.append(" | ".join([
            "%s %d" % (month, r["day"]),
            "Sunday Letter: %s" % r["letter"],
            "Kalendar Note: %s" % (entry or EMPTY),
        ]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).rstrip("\n")) + "\n"
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    body = text.split("\n")
    print("1979  rows=%3d  months=%2d  named=%3d"
          % (sum(1 for l in body if " | " in l),
             sum(1 for l in body if l.startswith("## ")),
             sum(1 for l in body if "Kalendar Note:" in l
                 and EMPTY not in l.split("Kalendar Note:")[1])))


if __name__ == "__main__":
    main()
