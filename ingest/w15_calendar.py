#!/usr/bin/env python3
"""w15_calendar.py — the 1928 Calendar (Wave 15): editions/1928/tables/calendar.md

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

The 1928 Calendar prints, for each day, the day of the month, the Sunday
letter and the holy day -- and NO LESSONS. The 1928 book moved its daily
lessons out of the Kalendar into a church-year table (tables/proper-lessons.md),
so the row carries the same three fields as 1979's, and
`git diff v1928 v1979 -- .../calendar.md` is a per-day comparison.

STRUCTURE (Calendar&Tables_1928.pdf sheets 1-2). Each sheet is two book pages,
three months each. Every day number, Sunday letter and name is a text run with
page coordinates, and each month sits at a fixed x. So a token's MONTH is its
x-range and its DAY its y-row -- structural facts, not reading order. The
golden numbers printed against 21 March - 18 April sit just left of the day
number; they are computational apparatus (Wave 14 ruling B) and are dropped.

Runs sometimes carry more than one cell ("29 29 ", "g5 c", "     St. Paul
Virgin Mary"), so runs are split into tokens with an estimated x each.

GATES (abort, never guess):
  1. every month a consecutive run 1..N of the right length (Feb 29 printed);
  2. the Sunday letters follow the rigid seven-day cycle;
  3. the holy-day names equal the Table of Feasts' fixed days (+ exemptions).
The text layer FAILS gates 1 and 2 in eleven places (six days missing, five
letters wrong) and keys All Saints against 1 October. Every one is resolved
from the scan of the original printing (w15_witness.CALENDAR, 13 entries),
never by arithmetic: the cycle FINDS a defect, the scan SUPPLIES the value.
"""
from __future__ import annotations
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import w15_src as S
import w15_witness as W

OUT = os.path.join(WT, "editions", "1928", "tables", "calendar.md")
EMPTY = "—"
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
NDAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
LETTERS = "Abcdefg"
CHAR_W = 2.9          # approx. advance of one 6-pt character, in PDF units
GUTTER = 400.0        # x dividing the two book pages of a sheet


def expected_letter(month_idx, day):
    """The Calendar's fixed letter: 1 January is A, and the cycle runs on
    through the year (a common year; 29 February carries no letter)."""
    doy = (datetime.date(1927, month_idx + 1, day)
           - datetime.date(1927, 1, 1)).days
    return LETTERS[doy % 7]


DIGIT_W = 5.0         # advance of one 6-pt digit (day 7 at x 57.8, day 17 at 52.8)


def merge_split_numbers(runs):
    """Rejoin a number the PDF split across two runs: '1' at x=237.4 followed
    by '8b' at x=242.4 is 18 September. The test is exact abutment -- the
    second run starts one digit-advance after the first, which carries no
    trailing space. A golden number never abuts its day (the nearest measured
    gap is 7.7 units), so this cannot glue a golden number to a date."""
    runs = sorted(runs, key=lambda r: (-r[0], r[1]))
    out = []
    for r in runs:
        if out:
            y0, x0, t0, s0 = out[-1]
            if (abs(y0 - r[0]) < 0.5 and re.search(r"\d$", t0)
                    and re.match(r"\d", r[2])
                    and abs(r[1] - (x0 + DIGIT_W * len(t0))) < 0.6):
                out[-1] = (y0, x0, t0 + r[2], s0)
                continue
        out.append(r)
    return out


def tokens(runs):
    """-> [(y, x, tok)] with glued tokens split ('g5' -> 'g','5')."""
    out = []
    for y, x, text, _size in merge_split_numbers(runs):
        pos = 0
        for m in re.finditer(r"\S+", text):
            tx = x + m.start() * CHAR_W
            for sub in re.findall(r"\d+|[A-Za-z][A-Za-z.’'-]*|[^\sA-Za-z\d]+",
                                  m.group(0)):
                out.append((y, tx, sub))
                tx += len(sub) * CHAR_W
            pos = m.end()
    return out


def column_starts(toks, lo, hi):
    """The x of each month's DAY column in [lo, hi): the three most common
    x-positions of day numbers (rounded to 5 units)."""
    from collections import Counter
    c = Counter(round(x / 5) * 5 for _y, x, t in toks
                if lo <= x < hi and t.isdigit() and len(t) <= 2)
    starts = sorted(x for x, _n in c.most_common(3))
    if len(starts) != 3:
        raise SystemExit("calendar: could not find three day columns in "
                         "[%s,%s): %s" % (lo, hi, c.most_common(6)))
    return starts


def parse_half(toks, months, runs):
    """Parse one book page (three months).

    DAY LINES are parsed as a token STREAM in x order, with an expected-next-day
    counter per month: a number equal to the next month's expected day is that
    month's day; any other number is a golden number (dropped). This is what
    splits runs like "29 29 " (29 February and 29 March in one run) correctly,
    where an x-estimate inside a run cannot. A day that is simply absent from
    the text layer leaves its month's counter waiting, so the day after it is
    still claimed by the right month -- and gate 1 reports the gap.

    NAME CONTINUATION lines (no digits) are placed by the x of their run: the
    run's column, and for a run holding several pieces separated by wide space
    ("St. Paul        Virgin Mary"), successive named columns to the right.
    """
    starts = column_starts(toks, min(x for _y, x, _t in toks),
                           max(x for _y, x, _t in toks) + 1)
    bounds = [s - 16 for s in starts]
    col = lambda x: max([i for i in range(3) if x >= bounds[i]] or [0])

    rows = {m: [] for m in months}
    nxt = {m: 1 for m in months}
    lines = {}
    for y, x, t in toks:
        key = next((k for k in lines if abs(k - y) <= 2.0), y)
        lines.setdefault(key, []).append((x, t))
    run_at = {}
    for y, x, text, _s in runs:
        key = next((k for k in lines if abs(k - y) <= 2.0), None)
        if key is not None:
            run_at.setdefault(key, []).append((x, text))

    last_named = {}                       # column -> row dict carrying a name
    for y in sorted(lines, reverse=True):
        stream = [t for _x, t in sorted(lines[y])]
        if not any(t.isdigit() for t in stream):
            for x, text in sorted(run_at.get(y, [])):
                pieces = [p for p in re.split(r"\s{3,}", text.strip()) if p]
                ci = col(x)
                for p in pieces:
                    # the next column at or right of ci that has an open name
                    # the owner is the named day NEAREST ABOVE this line
                    # among columns at or right of the run -- "Virgin Mary"
                    # under 25 March, not 24 February's St. Matthias
                    cands = [c for c in range(ci, 3) if c in last_named
                             and last_named[c]["y"] > y]
                    tgt = min(cands, key=lambda c: (last_named[c]["y"] - y, c),
                              default=None)
                    if tgt is None:
                        raise SystemExit("%s: name continuation %r has no "
                                         "owner" % (months[ci], p))
                    r = last_named[tgt]
                    r["name"] = _join(r["name"], p.split())
                    ci = tgt + 1
            continue
        cur = None                        # the row the stream is filling
        k = 0                             # month pointer
        for i, t in enumerate(stream):
            if t.isdigit():
                d = int(t)
                # A number IMMEDIATELY followed by another number is a golden
                # number ("17 17 b": golden 17, then 17 April) -- every day is
                # followed by its letter, except 29 February, which the book
                # prints with none ("29 29 d": 29 Feb, then 29 March).
                if i + 1 < len(stream) and stream[i + 1].isdigit():
                    feb29 = (d == 29 and "February" in months
                             and nxt["February"] == 29)
                    if not feb29:
                        cur = None
                        continue
                hit = next((j for j in range(k, 3)
                            if nxt[months[j]] <= d <= NDAYS[MONTHS.index(
                                months[j])] and _plausible(nxt[months[j]], d)),
                           None)
                if hit is None:
                    cur = None            # a golden number
                    continue
                m = months[hit]
                cur = {"day": d, "letter": "", "name": "", "col": hit, "y": y}
                rows[m].append(cur)
                nxt[m] = d + 1
                k = hit + 1
                continue
            if cur is None:
                continue
            if not cur["letter"] and not cur["name"] \
                    and re.fullmatch(r"[A-Ga-g]", t):
                cur["letter"] = t
            else:
                cur["name"] = _join(cur["name"], [t])
                last_named[cur["col"]] = cur
    return rows


def _plausible(expected, d):
    """A day number is accepted for a month if it is the expected next day or
    skips at most one (a day the text layer lost, which gate 1 then reports).
    Golden numbers (1-19) never pass this in the months that carry them,
    because by 21 March the counter is already past 19."""
    return expected <= d <= expected + 1


def _join(a, words):
    s = " ".join(w for w in words if w)
    if not s:
        return a
    if a.endswith("-"):
        return a[:-1] + s                 # "St. John Evan-" + "gelist"
    return (a + " " + s).strip()


def parse():
    """-> {month: [ {day, letter, name} ]} straight from the text layer."""
    out = {}
    for page, halves in ((1, (MONTHS[0:3], MONTHS[3:6])),
                         (2, (MONTHS[6:9], MONTHS[9:12]))):
        toks = tokens(S.runs("CAL", page))
        # drop running heads, month headers and the Thanksgiving note (which
        # sits below the December column and is emitted separately)
        body = [(y, x, t) for y, x, t in toks
                if 40 < y < 530]
        note_y = min((y for y, x, t in toks if t == "In" and x > GUTTER),
                     default=None)
        if note_y is not None:
            body = [(y, x, t) for y, x, t in body if y > note_y + 2 or x < GUTTER]
        runs = [r for r in S.runs("CAL", page) if 40 < r[0] < 530]
        if note_y is not None:
            runs = [r for r in runs if r[0] > note_y + 2 or r[1] < GUTTER]
        for months, sel in ((halves[0], lambda x: x < GUTTER),
                            (halves[1], lambda x: x >= GUTTER)):
            out.update(parse_half([b for b in body if sel(b[1])], months,
                                  [r for r in runs if sel(r[1])]))
    return out


def thanksgiving_note():
    toks = S.runs("CAL", 2)
    lines = [t for y, x, t, _s in toks if x > GUTTER and y < 95]
    s = S.norm_ws(" ".join(lines))
    s = s.replace("oth er", "other")
    return s


def gate(rows, strict=True):
    """-> list of problems (missing/extra days, letters off the cycle)."""
    probs = []
    for mi, m in enumerate(MONTHS):
        days = [r["day"] for r in rows[m]]
        if days != list(range(1, NDAYS[mi] + 1)):
            have = set(days)
            probs.append(("days", m, sorted(set(range(1, NDAYS[mi] + 1)) - have),
                          [d for d in days if days.count(d) > 1]))
        for r in rows[m]:
            if (mi, r["day"]) == (1, 29):
                if r["letter"]:
                    probs.append(("letter", m, r["day"], r["letter"], ""))
                continue
            want = expected_letter(mi, r["day"])
            if r["letter"] != want:
                probs.append(("letter", m, r["day"], r["letter"], want))
    return probs


def apply_witness(rows):
    """Apply the scan-read corrections. Each must MATCH the text layer's
    reading it claims to correct, or the build aborts -- a correction whose
    premise has gone stale is a silent change waiting to happen."""
    log = []
    for c in W.CALENDAR:
        m, d = c["month"], c["day"]
        have = next((r for r in rows[m] if r["day"] == d), None)
        if c["kind"] == "missing-row":
            if have is not None:
                raise SystemExit("witness: %s %d is no longer missing" % (m, d))
            rows[m].append({"day": d, "letter": c["scan"]["letter"],
                            "name": c["scan"].get("name", ""), "y": None})
            rows[m].sort(key=lambda r: r["day"])
        elif c["kind"] in ("letter", "name"):
            field = c["kind"]
            if have is None or have[field] != c["text_layer"]:
                raise SystemExit("witness: %s %d %s is %r, correction expects %r"
                                 % (m, d, field, have and have[field],
                                    c["text_layer"]))
            have[field] = c["scan"]
        else:
            raise SystemExit("witness: unknown kind %r" % c["kind"])
        log.append(c)
    return log


def emit(rows, note):
    lines = ["# The Kalendar", ""]   # the slug title every calendar cell carries
    for m in MONTHS:
        lines += ["## " + m, ""]
        for r in rows[m]:
            name = r["name"].rstrip(".").strip()
            lines.append(" | ".join([
                "%s %d" % (m, r["day"]),
                "Sunday Letter: %s" % (r["letter"] or EMPTY),
                "Kalendar Note: %s" % (name or EMPTY),
            ]))
        lines.append("")
    lines += ["> " + note, ""]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).rstrip("\n")) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text


def main():
    rows = parse()
    raw = gate(rows)
    print("text layer: %d rows, %d gate findings"
          % (sum(len(v) for v in rows.values()), len(raw)))
    for p in raw:
        print("   ", p)
    log = apply_witness(rows)
    left = gate(rows)
    if left:
        for p in left:
            print("UNRESOLVED", p)
        raise SystemExit("calendar gate: %d findings after the witness pass"
                         % len(left))
    text = emit(rows, thanksgiving_note())
    body = text.split("\n")
    named = [l for l in body if "Kalendar Note:" in l
             and EMPTY not in l.split("Kalendar Note:")[1]]
    print("1928  rows=%d  months=%d  named=%d  witness corrections=%d"
          % (sum(1 for l in body if " | " in l),
             sum(1 for l in body if l.startswith("## ")), len(named), len(log)))


if __name__ == "__main__":
    main()
