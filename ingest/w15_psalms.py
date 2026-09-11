#!/usr/bin/env python3
"""w15_psalms.py — the 1928 psalm tables (Wave 15).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

  editions/1928/tables/proper-psalms.md
      Proper Psalms for Seasons and Days (+ its two NOTEs), then as their own
      `##` tables: A Table of Psalms for the Sundays of the Church Year, and
      Psalms for Special Occasions. One file, several printed tables -- the
      1892 proper-lessons precedent.
  editions/1928/psalter/selections.md
      Selections of Psalms I-XX. Closes a recorded gap: justus links 1892's and
      1928's Selections to the 1789 page, so until now 1928 inherited 1789's
      ten Selections; the 1928 book prints twenty of its own.

Source: Lectionary_1928.pdf sheets 1-3 (layout mode); witness: scan pages
4-5 (book pp. vii-ix).

ROW SHAPES.
  Advent | Morning: 8, 50 | Evening: 96, 97 | Also: 7, 9, 36, 57, 98
The Morning/Evening split is the BOOK'S OWN rule, printed in the NOTE under
the table ("those for the Morning separated by the semi-colon from those for
the Evening; and then additional Psalms"). A row printed without that shape
(Rogation Days, Holy Week, the Ember and Saints' Days) is carried whole as
`Psalms:` -- it is not interpreted.
  First Sunday in Advent | Morning: 8, 50 | Evening: 96, 97
  Missions | Psalms: 2, 46, 47, ...
  I | Godliness | Psalms: 1, 15, 91
A printed list ordinal is its own leading field (Wave 14's rule: "I." before a
space is a sentence boundary to sentence_split.py).
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

OUT_PP = os.path.join(WT, "editions", "1928", "tables", "proper-psalms.md")
OUT_SEL = os.path.join(WT, "editions", "1928", "psalter", "selections.md")
GUT = {2: 124, 3: 140}
NUM = r"\d[\d:,;\s–-]*"


def pages():
    """-> the printed lines in reading order: sheet 1, sheet 2 left, sheet 2
    right, sheet 3 left."""
    s1 = S.layout("LEC", 1).split("\n")
    s2 = S.layout("LEC", 2).split("\n")
    s3 = S.layout("LEC", 3).split("\n")
    return (s1 + [l[:GUT[2]] for l in s2] + [l[GUT[2]:] for l in s2]
            + [l[:GUT[3]] for l in s3])


def between(lines, start, stop):
    a = next(i for i, l in enumerate(lines) if re.search(start, l))
    b = next(i for i, l in enumerate(lines[a + 1:], a + 1) if re.search(stop, l))
    return [l for l in lines[a + 1:b] if l.strip()]


RUNNING = re.compile(r"^\s*(Concerning the|Service of the Church)\s*$")


def proper_rows(lines):
    body = [l for l in between(lines, r"PROPER PSALMS FOR SEASONS",
                               r"^NOTE\.? That Proper") if not RUNNING.match(l)]
    rows = []
    for l in body:
        t = S.norm_ws(l)
        if re.match(r"^[A-Z][A-Z’' ]+[.,]\s", t):
            rows.append(t)
        else:                            # wrapped continuation
            rows[-1] += " " + t
    out = []
    for t in rows:
        m = re.match(r"^([A-Z][A-Z’' ]+?)[.,]\s+(.*)$", t)
        label, rest = S.smallcaps_title(m.group(1)), m.group(2)
        also = None
        a = re.search(r"\.\s+Also\s+(.*)$", rest)
        if a:
            also, rest = a.group(1), rest[:a.start()]
        parts = rest.split(";")
        if len(parts) == 2 and all(re.fullmatch(NUM + r"\.?", p.strip())
                                   for p in parts):
            fields = ["Morning: " + S.psalm_list(parts[0]),
                      "Evening: " + S.psalm_list(parts[1])]
        else:
            fields = ["Psalms: " + (S.psalm_list(rest) if re.fullmatch(
                NUM + r"\.?", rest.strip()) else S.norm_ws(rest).rstrip("."))]
        if also:
            fields.append("Also: " + S.psalm_list(also))
        out.append(" | ".join([label] + fields))
    return out


def notes(lines):
    body = between(lines, r"^\s*SAINTS’ DAYS", r"SELECTIONS OF PSALMS")
    paras = []
    for l in body:
        t = S.norm_ws(l)
        if re.match(r"^(NOTE|And NOTE)", t) or not paras:
            paras.append(t)
        else:
            paras[-1] += " " + t
    return paras


def sunday_rows(lines):
    a = next(i for i, l in enumerate(lines) if "A TABLE OF PSALMS FOR THE SUNDAYS" in l)
    out = []
    for l in lines[a:]:
        if "PSALMS FOR SPECIAL OCCASIONS" in l:
            break
        t = l.strip()
        m = re.match(r"^([A-Z][A-Z -]+?)\s{2,}(" + NUM + r"[\d.,\s]*)\s{2,}(" +
                     NUM + r"[\d.,\s]*)$", t)
        if not m:
            continue
        label = S.smallcaps_title(S.dekern(S.norm_ws(m.group(1))))
        out.append("%s | Morning: %s | Evening: %s"
                   % (label, S.psalm_list(m.group(2)), S.psalm_list(m.group(3))))
    return out


def sunday_heading(lines):
    a = next(i for i, l in enumerate(lines) if "A TABLE OF PSALMS FOR THE SUNDAYS" in l)
    return S.dekern(S.norm_ws(" ".join(lines[a:a + 3])))


def special_rows(lines):
    body = between(lines, r"PSALMS FOR SPECIAL OCCASIONS",
                   r"THE ORDER HOW THE REST")
    out = []
    for l in body:
        m = re.match(r"^([A-Z][A-Za-z ]+?)\.\s+(.*)$", S.norm_ws(l))
        out.append("%s | Psalms: %s" % (m.group(1), S.psalm_list(m.group(2))))
    return out


def selections(lines):
    body = between(lines, r"SELECTIONS OF PSALMS", r"^\s*$|zzzz")
    a = next(i for i, l in enumerate(lines) if "SELECTIONS OF PSALMS" in l)
    b = next(i for i, l in enumerate(lines[a:], a)
             if "A TABLE OF PSALMS FOR THE SUNDAYS" in l or
             re.search(r"^\s*Concerning the\s*$", l) and i > a + 3)
    body = [l for l in lines[a + 1:b] if l.strip() and not RUNNING.match(l)]
    # two columns: I-X left, XI-XX right; split at a gap of 6+ spaces and
    # place a piece by whether it opens with an ordinal and by its position
    first = next(l for l in body if re.search(r"\S\s{6,}XI\b", l))
    right_x = first.index("XI")
    cols = [[], []]
    for l in body:
        for m in re.finditer(r"\S(?:.*?\S)?(?=\s{6,}|$)", l):
            piece = S.norm_ws(m.group(0))
            c = 0 if m.start() < right_x - 12 else 1
            if re.match(r"^[IVX]+\b", piece):
                cols[c].append(piece)
            else:
                cols[c][-1] += " " + piece
    out = []
    for e in cols[0] + cols[1]:
        m = re.match(r"^([IVX]+)\.?\s*([A-Z][^.]*?)\.\s+(.*)$", e)
        if not m:
            raise SystemExit("selections: cannot parse %r" % e)
        out.append("%s | %s | Psalms: %s"
                   % (m.group(1), S.norm_ws(m.group(2)), S.psalm_list(m.group(3))))
    return out


def apply(rows, table):
    log = []
    for c in [c for c in W.PSALMS if c["table"] == table]:
        hits = [i for i, r in enumerate(rows) if c["text_layer"] in r]
        if len(hits) != 1:
            raise SystemExit("witness (%s): %r found %d times"
                             % (table, c["text_layer"], len(hits)))
        rows[hits[0]] = rows[hits[0]].replace(c["text_layer"], c["scan"], 1)
        if c.get("verify"):
            reading = re.findall(r"\d+", c["scan"])[-1]
            rows[hits[0]] += "\n<!-- VERIFY: '%s' %s -->" % (reading, c["verify"])
        log.append(c)
    return log


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(re.sub(r"\n{3,}", "\n\n", text.rstrip("\n")) + "\n")


EXPECT = {"proper": 22, "sunday": 57, "special": 10, "selections": 20}


def main():
    lines = pages()
    pp, sun, spc, sel = (proper_rows(lines), sunday_rows(lines),
                         special_rows(lines), selections(lines))
    got = {"proper": len(pp), "sunday": len(sun), "special": len(spc),
           "selections": len(sel)}
    if got != EXPECT:
        raise SystemExit("psalm tables: row counts %s, want %s" % (got, EXPECT))
    nts = notes(lines)
    log = (apply(pp, "proper") + apply(sun, "sunday") + apply(spc, "special")
           + apply(sel, "selections") + apply(nts, "notes"))
    body = ["# Proper Psalms for Seasons and Days", ""] + pp + [""]
    body += ["> " + n for n in nts] + [""]
    body += ["## " + sunday_heading(lines), ""] + sun + [""]
    body += ["## PSALMS FOR SPECIAL OCCASIONS.", ""] + spc
    write(OUT_PP, "\n".join(body))
    write(OUT_SEL, "\n".join(["# Selections of Psalms", ""] + sel))
    print("1928  proper-psalms: proper=%d sunday=%d special=%d notes=%d  "
          "selections=%d  witness corrections=%d"
          % (len(pp), len(sun), len(spc), len(nts), len(sel), len(log)))


if __name__ == "__main__":
    main()
