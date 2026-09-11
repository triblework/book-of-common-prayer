#!/usr/bin/env python3
"""w15_audit.py — gate 2 for Wave 15: did anything the sources attest fail to arrive?

Authoring-only. Fidelity (w15_fidelity.py) is blind to loss; this asks the
other question, by COUNTS and by STRUCTURE (AUDIT_METHOD: "a count that comes
up short is a finding"). Run w14_audit.py as well: it carries the
cross-edition anchor and field-shape checks for tables/ and front-matter/.

  1. Row counts for every 1928 table, as read off the scan of the original
     printing.
  2. Every calendar cell, every edition: twelve months, each a run 1..N;
     no Kalendar Note is a bare number (the 1979 "February 28 | ... | 29"
     class of defect); the Sunday letters keep the seven-day cycle.
  3. 1928: the Calendar's holy days and the Table of Feasts' fixed days
     name the same days (the Wave-14 names gate, applied to 1928).
  4. 1928 Christian-Year table: every week is its Sunday and six weekdays,
     unless exempted with a reason read off the scan.
  5. Field shapes: every Christian-Year row four lessons (or the printed
     "Use Lessons omitted..." direction), every Fixed-Holy-Day row six,
     every Special-Occasions row two.
  6. The witness table: every entry was applied (the builders abort on a
     stale one; this re-counts).
Reports; exits 1 on any anomaly.
"""
from __future__ import annotations
import datetime
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import w15_witness as W

E = lambda *p: os.path.join(WT, "editions", *p)
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
NDAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
findings = []


def rows(path, section=None):
    out, cur = [], None
    for l in open(path, encoding="utf-8").read().split("\n"):
        if l.startswith("## "):
            cur = l[3:]
            continue
        if " | " in l and not l.startswith("<!--"):
            if section is None or (cur or "").startswith(section):
                out.append(l)
    return out


def expect(name, got, want):
    mark = "OK " if got == want else "ANOMALY"
    print("%-7s %-58s %4d (want %4d)" % (mark, name, got, want))
    if got != want:
        findings.append("%s: %d, want %d" % (name, got, want))


# ------------------------------------------------------------------ 1
def counts():
    t = E("1928", "tables")
    expect("1928 calendar rows", len(rows(os.path.join(t, "calendar.md"))), 366)
    pp = os.path.join(t, "proper-psalms.md")
    lines = open(pp, encoding="utf-8").read().split("\n")
    head = lines.index(next(l for l in lines if l.startswith("## ")))
    expect("1928 Proper Psalms for Seasons and Days",
           sum(1 for l in lines[:head] if " | " in l), 22)
    expect("1928 Table of Psalms for the Sundays",
           len(rows(pp, "A TABLE OF PSALMS FOR THE SUNDAYS")), 57)
    expect("1928 Psalms for Special Occasions",
           len(rows(pp, "PSALMS FOR SPECIAL OCCASIONS")), 10)
    expect("1928 Selections of Psalms",
           len(rows(E("1928", "psalter", "selections.md"))), 20)
    pl = os.path.join(t, "proper-lessons.md")
    expect("1928 Table of Lessons for the Christian Year",
           len(rows(pl, "A TABLE OF LESSONS FOR THE CHRISTIAN YEAR")), 409)
    expect("1928 Table of Lessons for the Fixed Holy Days",
           len(rows(pl, "A TABLE OF LESSONS FOR THE FIXED")), 19)
    expect("1928 Table of Lessons for Special Occasions",
           len(rows(pl, "A TABLE OF LESSONS FOR SPECIAL")), 17)
    # the Tables and Rules: entries between their printed headings
    ff = [l for l in open(os.path.join(t, "feasts-and-fasts.md"),
                          encoding="utf-8").read().split("\n") if l.strip()]
    def between(a, b):
        i = next(k for k, l in enumerate(ff) if l.startswith(a))
        j = next(k for k, l in enumerate(ff[i + 1:], i + 1) if l.startswith(b))
        return ff[i + 1:j]
    expect("1928 Table of Feasts entries",
           len(between("TO BE OBSERVED", "A TABLE OF FASTS")), 29)
    expect("1928 Table of Fasts entries",
           len(between("A TABLE OF FASTS", "OTHER DAYS OF FASTING")), 2)
    expect("1928 Tables of Precedence, first list",
           len(between("The Holy Days following", "If any other")), 14)
    expect("1928 Tables of Precedence, second list",
           len(between("The following Holy Days", "On these Holy Days")), 11)
    expect("1928 Table of occasions not in the Calendar",
           len(ff[ff.index(next(l for l in ff if l.startswith("OF THOSE DAYS"))) + 1:]), 7)


# ------------------------------------------------------------------ 2
def letter(mi, day):
    return "Abcdefg"[(datetime.date(1927, mi + 1, day)
                      - datetime.date(1927, 1, 1)).days % 7]


def calendars():
    for ed in sorted(os.listdir(E())):
        p = E(ed, "tables", "calendar.md")
        if not os.path.exists(p):
            continue
        per = {m: [] for m in MONTHS}
        bare, off = [], []
        for r in rows(p):
            m = re.match(r"^([A-Z][a-z]+) (\d{1,2}) \|", r)
            if not m:
                continue
            mo, d = m.group(1), int(m.group(2))
            per[mo].append(d)
            note = re.search(r"Kalendar Note: (.*?)(?: \||$)", r)
            if note and re.fullmatch(r"\d+\W*", note.group(1).strip()):
                bare.append("%s %d" % (mo, d))
            lt = re.search(r"Sunday Letter: (\S+)", r)
            if lt and not (mo == "February" and d == 29):
                if lt.group(1) != letter(MONTHS.index(mo), d):
                    off.append("%s %d=%s" % (mo, d, lt.group(1)))
        bad_months = [mo for mi, mo in enumerate(MONTHS)
                      if per[mo] != list(range(1, len(per[mo]) + 1))
                      or len(per[mo]) not in ((28, 29) if mi == 1 else (NDAYS[mi],))]
        ok = not (bad_months or bare or off)
        print("%-7s %-5s calendar: %d days, months %s, bare-number notes %d, "
              "letters off-cycle %d %s" % ("OK " if ok else "ANOMALY", ed,
                                            sum(map(len, per.values())),
                                            "ok" if not bad_months else bad_months,
                                            len(bare), len(off),
                                            (bare + off)[:4] if not ok else ""))
        if not ok:
            findings.append("%s calendar: months %s bare %s letters %s"
                            % (ed, bad_months, bare[:4], off[:4]))


# ------------------------------------------------------------------ 3
STOP = {"of", "the", "and", "st", "day", "our", "lord", "jesus", "christ",
        "blessed", "apostle", "apostles", "evangelist", "martyr", "deacon",
        "virgin", "mary", "all", "a", "in"}
# (calendar name -> Table-of-Feasts entry) where the two books' wording differs
ALIAS = {"Christmas Day": "The Nativity of our Lord JESUS CHRIST"}
# Read off the scan (pp. xxix-xxxi): the Calendar prints Independence Day;
# the Table of Feasts "to be observed" does not list it.
CAL_ONLY = {"Independence Day":
            "printed in the Calendar (4 July, scan p. xxx) but not in the Table "
            "of Feasts (scan p. xxxi); a genuine difference between the tables"}
MOVABLE = ("All Sundays", "The Ascension", "Monday and Tuesday")


def key(s):
    return {w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP}


def feasts_vs_calendar():
    cal = [re.search(r"Kalendar Note: (.*)$", r).group(1)
           for r in rows(E("1928", "tables", "calendar.md"))]
    cal = [c for c in cal if c != "—"]
    ff = [l for l in open(E("1928", "tables", "feasts-and-fasts.md"),
                          encoding="utf-8").read().split("\n") if l.strip()]
    i = next(k for k, l in enumerate(ff) if l.startswith("TO BE OBSERVED"))
    j = next(k for k, l in enumerate(ff) if l.startswith("A TABLE OF FASTS"))
    table = [l for l in ff[i + 1:j] if not l.startswith(MOVABLE)]
    unmatched_cal = []
    for c in cal:
        if c in CAL_ONLY:
            continue
        target = ALIAS.get(c)
        hit = [t for t in table if (t == target) or (not target and key(c) <= key(t))]
        if not hit:
            unmatched_cal.append(c)
    unmatched_tab = [t for t in table if not any(
        ALIAS.get(c) == t or key(c) <= key(t) for c in cal)]
    ok = not unmatched_cal and not unmatched_tab
    print("%-7s 1928 Calendar holy days %d vs Table of Feasts fixed days %d "
          "(exempt: %s) %s" % ("OK " if ok else "ANOMALY", len(cal), len(table),
                               ", ".join(CAL_ONLY), "" if ok else
                               (unmatched_cal, unmatched_tab)))
    if not ok:
        findings.append("calendar/feasts names: %s / %s"
                        % (unmatched_cal, unmatched_tab))


# ------------------------------------------------------------------ 4, 5
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
# A "week" here is what follows a row that is not a plain weekday. Where the
# book's weeks are not Sunday + six weekdays, the reason (scan pp. x-xxvi):
WEEK_EXEMPT = {
    "Christmas": "the fixed days of Christmastide follow, not weekdays",
    "St. Stephen": "Christmastide fixed day", "St. John Evangelist":
    "Christmastide fixed day", "Holy Innocents": "Christmastide fixed day",
    "First Sunday after Christmas": "followed by December 29-31",
    "December 29": "a dated day", "December 30": "a dated day",
    "December 31": "a dated day", "Circumcision": "1 January",
    "Second Sunday after Christmas": "followed by January 2-5",
    "January 2": "a dated day", "January 3": "a dated day",
    "January 4": "a dated day", "January 5": "a dated day",
    "Quinquagesima": "the week runs Monday, Tuesday, then Ash Wednesday",
    "Ash Wednesday": "Thursday-Saturday complete Quinquagesima's week",
    "Sixth Sunday in Lent": "Holy Week: 'Monday before Easter' ... Easter Even",
    "Good Friday": "Holy Week", "Easter Even": "Holy Week",
    "Easter": "Easter Monday and Tuesday are named days",
    "Easter Monday": "Easter week", "Easter Tuesday":
    "Wednesday-Saturday of Easter week follow",
    "Fifth Sunday after Easter": "the Rogation Days follow",
    "Rogation Monday": "Rogation", "Rogation Tuesday": "Rogation",
    "Rogation Wednesday": "Ascension Day follows",
    "Ascension Day": "Friday and Saturday complete the week",
    "Whitsunday": "Whit Monday and Whit Tuesday are named days",
    "Whit Monday": "Whitsun week", "Whit Tuesday":
    "Wednesday-Saturday (Ember days) complete the week",
}


def base(label):
    return re.sub(r"\s+(Ember Day|before Easter)$", "", label)


def lessons_structure():
    pl = E("1928", "tables", "proper-lessons.md")
    cy = rows(pl, "A TABLE OF LESSONS FOR THE CHRISTIAN YEAR")
    weeks, cur = [], None
    shapes = Counter()
    for r in cy:
        f = r.split(" | ")
        lab = f[0]
        shapes[len(f) - 1 if not f[1].startswith("Lessons:") else "direction"] += 1
        if base(lab) in WEEKDAYS:
            if cur is not None:
                cur[1].append(base(lab))
        else:
            cur = (lab, [])
            weeks.append(cur)
    odd = []
    for lab, days in weeks[:-1] if weeks[-1][0] == "Sunday before Advent" \
            else weeks:
        if days == WEEKDAYS or lab in WEEK_EXEMPT:
            continue
        odd.append((lab, days))
    # the last three rows are the Autumnal Ember Days' optional lessons,
    # printed under their own heading after the Sunday before Advent's week
    last = weeks[-1]
    if last[0] == "Sunday before Advent" and last[1] != WEEKDAYS + [
            "Wednesday", "Friday", "Saturday"]:
        odd.append(last)
    ok = not odd
    print("%-7s 1928 Christian Year: %d weeks, %d exempt with a reason %s"
          % ("OK " if ok else "ANOMALY", len(weeks),
             sum(1 for l, _d in weeks if l in WEEK_EXEMPT), odd[:3] if odd else ""))
    if odd:
        findings.append("christian year weeks: %s" % odd[:6])
    # 404 printed days + the 3 Autumnal Ember rows carry four lessons; the
    # 25th and 26th Sundays after Trinity carry the printed direction
    got = Counter(shapes)
    ok = got == Counter({4: 407, "direction": 2})
    print("%-7s 1928 Christian Year field shapes %s" % ("OK " if ok else
                                                        "ANOMALY", dict(got)))
    if not ok:
        findings.append("christian year shapes %s" % dict(got))
    for sec, n in (("A TABLE OF LESSONS FOR THE FIXED", 6),
                   ("A TABLE OF LESSONS FOR SPECIAL", 2)):
        bad = [r for r in rows(pl, sec) if len(r.split(" | ")) - 1 != n]
        print("%-7s 1928 %s: every row %d lessons %s"
              % ("OK " if not bad else "ANOMALY", sec[2:].title(), n,
                 bad[:2] if bad else ""))
        if bad:
            findings.append("%s shapes: %s" % (sec, bad[:2]))


# ------------------------------------------------------------------ 6
def witness():
    n = {"calendar": len(W.CALENDAR), "feasts": len(W.FEASTS),
         "psalms": len(W.PSALMS), "rubrics": len(W.RUBRICS),
         "lessons": len(W.LESSONS)}
    expect("witness corrections (calendar 13, feasts 10, psalms 14, "
           "rubrics 2, lessons 190)", sum(n.values()), 229)


def main():
    counts()
    calendars()
    feasts_vs_calendar()
    lessons_structure()
    witness()
    print("\nw15 audit: %d anomalies" % len(findings))
    for f in findings:
        print("  - " + f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
