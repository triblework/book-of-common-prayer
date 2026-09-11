#!/usr/bin/env python3
"""w15_lessons.py — the 1928 tables of lessons (Wave 15): tables/proper-lessons.md

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

The 1928 book moved the daily lessons OUT of the Kalendar into a table keyed
to the church year, so its lessons live in three printed tables:

  ## A TABLE OF LESSONS FOR THE CHRISTIAN YEAR.
     every Sunday AND weekday, Advent 1 -> the Sunday before Advent,
     with the Ember-day optional lessons and the fixed days of Christmastide.
     It succeeds 1892's Sundays table AND its weekday tables (Lent, Rogation,
     Ember), which is why it shares their file (ruling 5).
  ## A TABLE OF LESSONS FOR THE FIXED HOLY DAYS ...
     Eve / Morning / Evening, each with a First and Second Lesson.
  ## A TABLE OF LESSONS FOR SPECIAL OCCASIONS.

ROWS (Wave 14 schema; the 1892 labels "Morning 1" ... "Evening 2"):
  First Sunday in Advent | Morning 1: Isa. 55 | Morning 2: Luke 1:v. 57 | ...
  St. Andrew | Eve 1: ... | Eve 2: ... | Morning 1: ... | ... | Evening 2: ...
  When a Confirmation is to follow | First Lesson: A / B | Second Lesson: C / D
Weekday rows carry the printed label ("Monday"); the Sunday row above them is
what places them, exactly as on the page. Citations are carried as printed,
with typographic normalization only (w15_src.citation). Alternatives stacked
in one Special-Occasions cell are joined with " / " -- supplied punctuation,
since the book stacks them and does not pair them (Missions prints three
first lessons against four second).

STRUCTURE -- RUNS, NOT LAYOUT MODE. Each printed row is its label run(s) plus
ONE run holding all four cells in printed order; a wrapped tail ("18-end") is
its own run at its own x. Layout mode re-placed several of these runs (it put
the Rogation Monday row's last cell on the next row's label), so the parser
works from runs (w15_src.runs):
  * cells are split where a CITATION STARTS -- a book abbreviation, kerning-
    tolerant ("M att.", "I K gs"), including the text layer's misreadings
    ("Lake", "Mail") so they open a cell and can be corrected in place;
  * the label is the text before the first citation, its small capitals set
    to the printed case by RUN SIZE (6 pt capitals, 4.98 pt small capitals);
  * a label-less citation line fills the row's empty cells, or else stacks
    alternatives (the Ember and Eve-of-Ascension lessons) by x;
  * a tail joins the cell that awaits it (ends ",", "-", ":" or "and") when
    the counts agree, otherwise the cell of its column (COLS).

GATES: the row counts (EXPECT) abort the build; every correction in
w15_witness.LESSONS must still match the text-layer reading it replaces.
Every row was compared with the scan of the original printing: 190 cells and
labels are corrected there, each with its book page (w15_lessons_witness.json).
"""
from __future__ import annotations
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import w15_src as S
import w15_witness as W

OUT = os.path.join(WT, "editions", "1928", "tables", "proper-lessons.md")
TITLE = "Tables of Proper Lessons"          # the slug title (1789, 1892)
WEEKDAY = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)$")
LABEL_CONT = re.compile(r"^(IN|AFTER|BEFORE|NEXT|EVANGELIST|EVANGE|LIST|OF)\b"
                        r"|^[a-z]")
FOOTNOTE = re.compile(r"^[*†]")
RUNNING = re.compile(r"Lessons for the (Christian Year|fixed Holy Days)|"
                     r"Lessons for Special Occasions|^DAYS\b|First Les|"
                     r"Concerning the|Service of the Church|^Occasions\b")


# ---------------------------------------------------------------- the table
def _kern(word):
    """A book abbreviation as the text layer may kern it: 'Matt' matches
    'Matt', 'M att', 'M a tt'."""
    return r"\s?".join(re.escape(c) for c in word)


_BOOKS = sorted(S.BOOK_ABBR | {"Philemon", "Haggai", "Deus", "Gem", "Con",
                               "Murk", "Lake", "Lukc", "Joke", "Es", "Cur",
                               "Act", "Kg", "Mail"},
                key=len, reverse=True)
_G = r"[\s\u00a6]*"            # spaces and run-boundary marks
# A citation STARTS at an (optionally ordinal-prefixed) book name followed by
# (the ordinal may follow a digit -- the text layer glues "v. 16I Cor." --
# but never a letter or a dash)
# a chapter number (or an OCR look-alike: "l0", "I"), "v.", the end of the
# cell, or another citation (a whole-book lesson: "Jude  Nahum"). It is never
# preceded by a dash ("I Kgs. 22:51-II Kgs. 1:end" is one citation) nor by
# "v." (an OCR "II" for the verse 11 is not an ordinal). The misread names
# ("Lake", "Mail", "Lukc") must still OPEN a cell so the witness pass can
# correct them in place.
_ORDINAL_BOOKS = ("Cor", "Kgs", "Sam", "Chron", "Thess", "Tim", "Pet", "Esd",
                  "Macc")
_CITE_A = (
    r"(?:(?<![-–—A-Za-z\d])(?<!v\.\s)(?:III|II|I|l)[\s¦]+"
    r"|(?<![-–—\w])(?<![-–—]II )(?<![-–—]I )(?<![-–—]I\u00a0))"
    r"(?:%s)%s(?:[.,:]%s){0,2}"
    r"(?=[\dl]|I\b|v\s?\.|$|[A-Z][a-z]|(?:III|II|I)\s)"
    % ("|".join(_kern(b) for b in _BOOKS), _G, _G))
# the OCR keys a first ordinal as the digit "1" ("16 1 C or."): accepted only
# before a book that TAKES an ordinal, and not John, so that a chapter "1"
# ending the cell before ("Gal. 1 Jer.") is never read as one
_CITE_B = (r"(?<=[\s¦])1[\s¦]+(?:%s)%s(?:[.,:]%s){0,2}(?=[\dl]|v\s?\.)"
           % ("|".join(_kern(b) for b in _ORDINAL_BOOKS), _G, _G))
CITE_START = re.compile(_CITE_A + "|" + _CITE_B)


def run_lines(sheet):
    """-> {page_base: [(y, [(x, text), ...]), ...]} for a sheet: the text runs
    grouped into printed lines, per book page (left page base x=54, right 450).
    RUNS, not layout mode: each row prints as its label run(s) plus ONE run
    holding all four cells in printed order, and a wrapped tail is its own run
    at its own x. Layout mode re-placed several of these runs (sheet 6 put the
    Rogation Monday row's last cell on the NEXT row's label)."""
    pages = {54: [], 450: []}
    for y, x, t, _sz in S.runs("LEC", sheet):
        # SMALL CAPITALS: the page sets a label's large capitals at 6 pt and
        # the rest as small capitals at 4.98 pt, all keyed upper-case. The
        # size is the typeset fact, so it decides the case ("F" + "IRST" ->
        # "First", "IN LENT" -> "in Lent"); a citation run is never small.
        if _sz < 5.5 and re.search(r"[A-Z]", t) and not re.search(r"[a-z]", t):
            t = t.lower()
        base = 450 if x >= 440 else 54
        lines = pages[base]
        hit = next((ln for ln in lines if abs(ln[0] - y) <= 1.5), None)
        if hit is None:
            lines.append((y, [(x, t)]))
        else:
            hit[1].append((x, t))
    for base in pages:
        pages[base] = sorted(((y, sorted(r)) for y, r in pages[base]),
                             key=lambda l: -l[0])
    return pages


# Column boundaries as offsets from the page base, calibrated on the text
# layer's own split runs (sheet 8: "II Esd." opening Evening 1 at +170; sheet
# 6: the Eve-of-Ascension lessons opening Evening 1 at +171). Used only for a
# line that holds fewer than four cells, and as the fallback for tails.
COLS = [0, 42, 108, 165]       # M1 | M2 | E1 | E2 starts (offset - 54): the
                               # clusters of tail-run x across sheets 3-8


def col_of(x, base):
    off = x - base - 54
    return max(k for k in range(4) if off >= COLS[k] - 6) if off >= -6 else 0


INCOMPLETE = re.compile(r"(?:[,:–-]|\band)\s*$")


def split_cells(text, raw=False):
    """Split a run of citations at each citation start. An OCR "II" for a
    verse number ("43:v. II Mark 9") opens the next cell as if an ordinal; a
    chunk ending in "v." takes such a numeral back."""
    st = [m.start() for m in CITE_START.finditer(text)]
    if not st:
        return []
    out = [(text[a:b].strip() if raw else S.norm_ws(text[a:b]))
           for a, b in zip(st, st[1:] + [len(text)])]
    for i in range(len(out) - 1):
        m = re.match(r"^(I{1,3}|l)\s+(.*)$", out[i + 1])
        if m and re.search(r"v\s?\.?$", out[i]):
            out[i], out[i + 1] = out[i] + " " + m.group(1), m.group(2)
    return out


SEP = " \u00a6 "      # run boundary marker inside a joined line


def christian_year():
    rows, notes = [], []
    started = False
    suffix = None
    for sheet in range(3, 9):
        for base, lines in run_lines(sheet).items():
            for y, runs in lines:
                flat = S.norm_ws(" ".join(t for _x, t in runs))
                dk = S.dekern(flat)
                if not started:
                    started = "TABLE OF LESSONS FOR THE CHRISTIAN YEAR" in dk
                    continue
                if RUNNING.search(dk) or re.match(r"^(DAYS\b|First\s*L)", dk):
                    continue
                if FOOTNOTE.match(flat):
                    if dk not in notes:
                        notes.append(dk)
                    continue
                if "OPTIONAL LESSONS" in dk:
                    rows.append({"sub": dk})
                    continue
                if re.fullmatch(r"(th|st|nd|rd)", dk):
                    # an ordinal suffix, set as a superscript a line ABOVE its
                    # numbered Sunday ("th" over "11 SUNDAY")
                    suffix = dk
                    continue
                joined, offs = "", []
                for x, t in runs:
                    if joined:
                        joined += SEP
                    offs.append((len(joined), x, t))
                    joined += t
                m = CITE_START.search(joined)
                end = m.start() if m else len(joined)
                head = joined[:end]
                cells = split_cells(joined[end:].replace(SEP, " ")) if m else []
                label, tails = None, []
                # the head's pieces, each with an x: run x + character offset
                # (an estimate, used only to choose among columns 50+ apart)
                hp = []
                for o, x, t in offs:
                    if o >= end:
                        break
                    part = t[:end - o]
                    for mm in re.finditer(r"\S(?:.*?\S)?(?=\s{3,}|\s*$)", part):
                        hp.append((x + mm.start() * CHAR_W, S.norm_ws(mm.group(0))))
                if hp and runs[0][0] - base < 45:
                    # label pieces first (letters or bare punctuation: the
                    # runs split "ST" "." "S" "TEP HEN"). A piece with a digit
                    # or "end" / "and ch." is a tail sharing the line -- except
                    # a date ("Dec em ber 29", "January" "4") and the number of
                    # a numbered Sunday ("11 S" "UN DA Y").
                    lab = []
                    for x, p in hp:
                        dp = S.dekern(p)
                        date = bool(re.match(r"^(January|December)\s*\d{1,2}$", dp)
                                    or lab and re.fullmatch(r"\d{1,2}", p)
                                    and S.dekern(" ".join(lab)) in ("January", "December"))
                        numsun = not lab and bool(re.match(r"^\d{1,2}\s+S", p))
                        is_tail = bool(re.search(r"\d", p) or re.match(
                            r"^(e ?nd|a ?nd\b|ch\.)", p))
                        if not tails and (date or numsun or not is_tail):
                            lab.append(p)
                        else:
                            tails.append((x, p))
                    label = S.dekern(" ".join(lab)) if lab else None
                    if label:
                        label = re.sub(r"\s*\.\s*", ". ", label).strip()
                        label = re.sub(r"\.$", "", label).strip()
                else:
                    tails = hp
                directive = None
                if label and not cells:
                    lm = re.match(r"^(\d+\s+Sunday)\s+(Use\b.*)$", label, re.I)
                    if lm:
                        label, directive = lm.group(1), lm.group(2)
                prev = rows[-1] if rows and "sub" not in rows[-1] else None
                is_cont = bool(label) and prev is not None and (
                    (not cells and not directive)
                    or " ".join(prev["label"]) == "Rogation"
                    or bool(LABEL_CONT.search(label))
                    # "Ember Day" is never a row of its own: the book prints
                    # it as the second line of the weekday's label, with the
                    # optional Ember lessons stacked under that day's
                    or label.lower().startswith("ember"))
                if label and not is_cont:
                    if suffix and re.match(r"^\d+ ", label):
                        label = re.sub(r"^(\d+)", r"\g<1>" + suffix, label)
                    suffix = None
                    row = {"label": [label], "cells": [[] for _ in range(4)],
                           "sheet": sheet, "directive": directive}
                    rows.append(row)
                    for k, c in enumerate(cells[:4]):
                        row["cells"][k].append(c)
                    if len(cells) not in (0, 4):
                        row["short"] = len(cells)
                    if len(cells) > 4:
                        row["extra"] = cells[4:]
                else:
                    if not rows or "sub" in rows[-1]:
                        raise SystemExit("orphan line, sheet %d: %r" % (sheet, flat))
                    row = rows[-1]
                    if label:
                        row["label"].append(label)
                    empty = [k for k in range(4) if not row["cells"][k]]
                    if cells and not label and empty and len(cells) <= len(empty):
                        # the row above is SHORT and this label-less line holds
                        # its missing cells (sheet 5: a Thursday's last lesson
                        # is set on the next line) -- fill them in order
                        for k, c in zip(empty, cells):
                            row["cells"][k].append(c)
                        row.pop("short", None)
                    elif cells:
                        # stacked alternatives (Ember, Eve of Ascension): the
                        # first goes by the x of its run, the rest follow it
                        cx = next(x for x, t in runs if CITE_START.search(t))
                        k0 = 0 if len(cells) == 4 else col_of(cx, base)
                        for k, c in enumerate(cells):
                            row["cells"][min(3, k0 + k)].append("/ " + c)
                _attach_tails(rows[-1], tails, base)
    return rows, notes


CHAR_W = 2.45        # approx. advance of one character of a 6-pt run


def _attach_tails(row, tails, base):
    """Wrapped tails continue the cells that visibly await them (ending in a
    comma, dash, colon or "and"), in order, when the counts agree; otherwise
    each goes to the column its x falls in."""
    if not tails:
        return
    waiting = [k for k in range(4) if row["cells"][k]
               and INCOMPLETE.search(row["cells"][k][-1])]
    # a tail stays its own FRAGMENT (emit joins fragments with a space), so
    # the fidelity gate can find each piece verbatim in the text layer
    if len(waiting) == len(tails):
        for k, (_x, t) in zip(waiting, tails):
            row["cells"][k].append(t)
        return
    for x, t in tails:
        k = col_of(x, base)
        if row["cells"][k]:
            row["cells"][k].append(t)
        else:
            row.setdefault("unplaced", []).append(t)


def _line(runs):
    joined = SEP.join(t for _x, t in runs)
    m = CITE_START.search(joined)
    end = m.start() if m else len(joined)
    return joined[:end].replace(SEP, " "), (split_cells(
        joined[end:].replace(SEP, " "), raw=True) if m else [])


def fixed_holy_days():
    """Sheet 9, left page (book pp. xxvi-xxvii): a holy day's name, then a
    First-Lesson line and a Second-Lesson line, each ONE run holding the Eve,
    Morning and Evening cells in printed order."""
    rows = []
    started = False
    for y, runs in run_lines(9)[54]:
        head, cells = _line(runs)
        dk = S.dekern(S.norm_ws(head))
        if not started:
            started = "CHRISTIAN" in dk.replace(" ", "")
            continue
        if re.match(r"^EVE\b", dk):
            continue
        which = re.match(r"^(First|Second)\s*L", dk)
        if which and rows:
            k = 0 if which.group(1) == "First" else 1
            # the misread "First Lassos" still opens the line
            if len(cells) != 3:
                rows[-1]["short"] = rows[-1].get("short", []) + [(k, cells)]
            for j, c in enumerate(cells[:3]):
                rows[-1]["cells"][j][k].append(c)
        elif dk and not cells:
            rows.append({"label": dk, "cells": [[[], []] for _ in range(3)]})
        else:
            raise SystemExit("fixed holy days: unexpected line %r" % dk)
    return rows


SO_FIRST, SO_SECOND = 603.0, 661.4      # the two lesson columns (sheet 9)


def special_occasions():
    """Sheet 9, right page (book p. xxviii). A label ends with ':' when it is
    complete; one that does not ("AT THE DEDICATION OR CONSECRATION OF A")
    continues on the next line. A label-less line holds stacked alternatives
    (placed by x) or wrapped tails."""
    rows, parent = [], None
    started = False
    for y, runs in run_lines(9)[450]:
        head, cells = _line(runs)
        flat = S.norm_ws(head)
        if not started:
            started = "SPECIAL OCCASIONS" in S.dekern(flat)
            continue
        if re.match(r"^Occ", flat):
            continue
        # the label is the part before the colon (or the whole head)
        raw = head.replace(SEP, " ")
        lab, tails = flat, []
        if ":" in raw:
            lab, rest = raw.split(":", 1)
            lab = S.norm_ws(lab) + ":"
            tails = [S.norm_ws(t) for t in re.split(r"\s{3,}", rest.strip()) if t.strip()]
        # a cell run may carry a wrapped tail after a wide gap
        # (": Isa. 52:1-10     1 6-end") -- cut it off as a tail
        cut = []
        for c in cells:
            parts = re.split(r"\s{3,}", c)
            cut.append(parts[0])
            tails += [S.norm_ws(t) for t in parts[1:] if t.strip()]
        cells = [S.norm_ws(c) for c in cut]
        # a label is words (not a digit, not a wrapped "and 26:1-4" tail) in
        # the label column, which ends well before First Lesson at x=603
        is_label = (runs[0][0] < 560 and re.search(r"[A-Za-z]{3,}", lab)
                    and not re.match(r"^\s*(and|e ?nd|ch\.)\b|^\s*\d", lab))
        lab = S.dekern(lab).strip() if is_label else ""
        if not lab and flat and not cells:
            tails = [S.norm_ws(t) for t in re.split(r"\s{3,}", raw) if t.strip()]
        cx = next((x for x, t in runs if CITE_START.search(t)), None)
        if lab:
            prev = rows[-1] if rows else None
            if prev and not prev["label"].endswith(":") and re.search(
                    r"\b(of|a|the|and|or|in|to|is)$", prev["label"], re.I):
                prev["label"] += " " + lab
                row = prev
                _place(row, cells, cx, alt=True)
            elif re.match(r"^TO THE\b", lab, re.I) and parent:
                row = {"label": parent + " " + lab, "cells": [[], []]}
                rows.append(row)
                _place(row, cells, cx)
            else:
                row = {"label": lab, "cells": [[], []]}
                rows.append(row)
                parent = lab if not cells else None
                _place(row, cells, cx)
        else:
            row = rows[-1]
            _place(row, cells, cx, alt=True)
        _tails(row, tails, runs)
    return [r for r in rows if r["cells"] != [[], []]]


def _place(row, cells, cx, alt=False):
    if not cells:
        return
    k0 = 0 if len(cells) == 2 or cx is None or cx < (SO_FIRST + SO_SECOND) / 2 \
        else 1
    for k, c in enumerate(cells):
        col = row["cells"][min(1, k0 + k)]
        col.append(("/ " if alt and col else "") + c)


INCOMPLETE_SO = re.compile(r"(?:[,:–-]|\band)\s*$")


def _tails(row, tails, runs):
    """Tails fill the cells that await them, in order, when the counts agree
    ("Isa. 25:1-9," + "Heb. 11:8-16," / "and 26:1-4" + "and 12:28"); a single
    tail goes to the one awaiting cell; otherwise to the last column."""
    if not tails:
        return
    waiting = [k for k in (0, 1) if row["cells"][k]
               and INCOMPLETE_SO.search(row["cells"][k][-1])]
    if len(waiting) == len(tails):
        for k, t in zip(waiting, tails):
            row["cells"][k].append(t)
    else:
        row.setdefault("unplaced", []).extend(tails)


# ---------------------------------------------------------------- emitting
def join_cell(parts):
    """A wrapped citation: continuation fragments join the cell."""
    s = " ".join(parts)
    return S.citation(s)


def _cap(s):
    """Every label in these tables opens with a large capital; the text layer
    sometimes keys the first word at the small-capital size ("FOR NATIONAL")."""
    return s[:1].upper() + s[1:] if s else s


def label_text(parts, row):
    s = _cap(S.dekern(" ".join(parts)))
    # "be fore" / "bef ore": both halves are words, so de-kerning leaves them
    s = re.sub(r"\bbe ?f ?ore\b", "before", s).rstrip(",. ")
    if re.match(r"^\d+(th|st|nd|rd) ", s):       # suffix already rejoined
        return s
    m = re.match(r"^(\d+)\s+(SUNDAY.*)$", s)
    if m:
        # "11 SUNDAY" -- the ordinal suffix is displaced to the end of the
        # row's last cell ("Matt. 19:1-9th"); rejoin it
        last = row["cells"][3]
        suf = re.search(r"(th|st|nd|rd)$", last[-1]) if last else None
        if not suf:
            raise SystemExit("ordinal suffix not found for %r (%r)" % (s, last))
        last[-1] = last[-1][:suf.start()]
        s = "%s%s %s" % (m.group(1), suf.group(1), m.group(2))
    if re.match(r"^(December|January)\s*\d", s):
        return re.sub(r"^(December|January)\s*(\d+)$", r"\1 \2", s)
    return s


def emit_rows(cy, fh, so):
    out = []
    for r in cy:
        if "sub" in r:
            out.append("### " + r["sub"])
            continue
        lab = label_text(r["label"], r)
        if r.get("directive"):
            d = r["directive"]
            suf = re.search(r"(th|st|nd|rd)$", d)
            if suf and re.match(r"^\d+ ", lab):
                d = d[:suf.start()]
                lab = re.sub(r"^(\d+)", r"\1" + suf.group(1), lab)
            out.append("%s | Lessons: %s" % (lab, d.rstrip(".")))
            continue
        cells = []
        for c in r["cells"]:
            alts = []
            for part in c:
                if part.startswith("/ "):
                    alts.append(part[2:])
                elif alts:
                    alts[-1] += " " + part
                else:
                    alts.append(part)
            cells.append(" / ".join(S.citation(a) for a in alts) if alts else "—")
        out.append(" | ".join([lab] + ["%s: %s" % (k, v) for k, v in zip(
            ("Morning 1", "Morning 2", "Evening 1", "Evening 2"), cells)]))
    fhr = []
    for r in fh:
        lab = _cap(S.dekern(r["label"]))
        fields = []
        for name, (first, second) in zip(("Eve", "Morning", "Evening"),
                                         r["cells"]):
            fields.append("%s 1: %s" % (name, join_cell(first) if first else "—"))
            fields.append("%s 2: %s" % (name, join_cell(second) if second else "—"))
        fhr.append(" | ".join([lab] + fields))
    sor = []
    for r in so:
        lab = re.sub(r"\s*:\s*$", "", S.norm_ws(r["label"]))
        lab = re.sub(r"\s*:\s*", ": ", lab)
        lab = _cap(re.sub(r"\s+-", "-", lab))
        cells = []
        for c in r["cells"]:
            alts = []
            for part in c:
                if part.startswith("/ "):
                    alts.append(part[2:])
                elif alts:
                    alts[-1] += " " + part
                else:
                    alts.append(part)
            cells.append(" / ".join(S.citation(a) for a in alts) or "—")
        sor.append("%s | First Lesson: %s | Second Lesson: %s"
                   % (lab, cells[0], cells[1]))
    return out, fhr, sor


# Row counts, read off the scan of the original printing (pp. x-xxviii): the
# Christian-Year table's 407 printed day rows + the two "Use Lessons omitted"
# Sundays; nineteen fixed Holy Days (St. Andrew ... All Saints); seventeen
# Special Occasions (the Ordination entry prints two).
EXPECT = {"cy": 409, "fh": 19, "so": 17}


def structured(rows, fhr, sor):
    """-> [{sec, week, label, fields}] from the emitted lines, so that witness
    corrections can be keyed by (week, day, column) -- a weekday label alone
    ("Monday") is not unique."""
    out, week = [], None
    for sec, lines in (("cy", rows), ("fh", fhr), ("so", sor)):
        for l in lines:
            if l.startswith("### "):
                out.append({"sec": sec, "sub": l[4:]})
                week = l[4:]
                continue
            parts = l.split(" | ")
            label = parts[0]
            if sec == "cy" and not WEEKDAY.match(label.split(" Ember")[0]) \
                    and not label.startswith("Rogation"):
                week = label
            fields = []
            for f in parts[1:]:
                k, v = f.split(": ", 1)
                fields.append([k, v])
            out.append({"sec": sec, "week": week if sec == "cy" else None,
                        "label": label, "orig": label, "fields": fields})
    # a (week, label) pair can repeat -- the text layer keys the Thursday
    # before Advent as a second "Tuesday" -- so number the repeats
    seen = {}
    for r in out:
        if "label" in r:
            k = (r["sec"], r["week"], r["orig"])
            r["dup"] = seen.get(k, 0)
            seen[k] = r["dup"] + 1
    return out


def apply_witness(recs):
    log = []
    for c in W.LESSONS:
        hits = [r for r in recs if "label" in r and r["sec"] == c["sec"]
                and (c.get("week") is None or r["week"] == c["week"])
                and r["orig"] == c["row"] and r["dup"] == c.get("dup", 0)]
        if len(hits) != 1:
            raise SystemExit("witness (lessons): %s/%s/%s matched %d rows"
                             % (c.get("week"), c["row"], c.get("field"), len(hits)))
        r = hits[0]
        if c.get("field") == "label":
            if r["label"] != c["text_layer"]:
                raise SystemExit("witness label %r != %r" % (r["label"], c["text_layer"]))
            r["label"] = c["scan"]
        else:
            f = next((f for f in r["fields"] if f[0] == c["field"]), None)
            if f is None or f[1] != c["text_layer"]:
                raise SystemExit("witness (lessons): %s/%s %s is %r, correction "
                                 "expects %r" % (c.get("week"), c["row"],
                                                 c["field"], f and f[1],
                                                 c["text_layer"]))
            f[1] = c["scan"]
        if c.get("verify"):
            r.setdefault("verify", []).append(c)
        log.append(c)
    return log


HEADINGS = {
    "cy": "## A TABLE OF LESSONS FOR THE CHRISTIAN YEAR.",
    "fh": "## A TABLE OF LESSONS FOR THE FIXED HOLY DAYS WHICH ARE NOT IN THE "
          "TABLE OF LESSONS FOR THE CHRISTIAN YEAR.",
    "so": "## A TABLE OF LESSONS FOR SPECIAL OCCASIONS.",
}


def write(recs, notes):
    lines = ["# " + TITLE, ""]
    sec = None
    for r in recs:
        if r["sec"] != sec:
            if sec == "cy":
                lines += [""] + ["> " + n for n in notes]
            sec = r["sec"]
            lines += ["", HEADINGS[sec], ""]
        if "sub" in r:
            lines += ["", "### " + r["sub"], ""]
            continue
        lines.append(" | ".join([r["label"]] + ["%s: %s" % (k, v)
                                                for k, v in r["fields"]]))
        for c in r.get("verify", []):
            lines.append("<!-- VERIFY: '%s' %s -->" % (c["scan"], c["verify"]))
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).strip("\n")) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text


def main(write_file=True, witness=True):
    cy, notes = christian_year()
    fh = fixed_holy_days()
    so = special_occasions()
    for r in fh:
        if r.get("short") or any(not a or not b for a, b in r["cells"]):
            print("CHECK FH", r["label"], r["cells"])
    for r in so:
        if r.get("unplaced") or not r["cells"][0] or not r["cells"][1]:
            print("CHECK SO", r["label"], r["cells"], r.get("unplaced", ""))
    for r in cy:
        if "sub" in r or r.get("directive"):
            continue
        if any(len(c) == 0 for c in r["cells"]) or r.get("short") or \
                r.get("extra") or r.get("unplaced"):
            print("CHECK", r["sheet"], r["label"], r["cells"],
                  r.get("extra", ""), r.get("unplaced", ""))
    rows, fhr, sor = emit_rows(cy, fh, so)
    recs = structured(rows, fhr, sor)
    log = apply_witness(recs) if witness else []
    notes = [n for n in W.LESSON_NOTES] if hasattr(W, "LESSON_NOTES") else notes
    if write_file:
        write(recs, notes)
    n = {k: sum(1 for r in recs if r["sec"] == k and "label" in r)
         for k in ("cy", "fh", "so")}
    if n != EXPECT:
        raise SystemExit("proper-lessons: row counts %s, want %s" % (n, EXPECT))
    print("1928  proper-lessons: christian-year=%d fixed=%d special=%d "
          "notes=%d witness corrections=%d" % (n["cy"], n["fh"], n["so"],
                                               len(notes), len(log)))
    return recs, notes


if __name__ == "__main__":
    main()
