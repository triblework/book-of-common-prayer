#!/usr/bin/env python3
"""w15_rubrics.py — the 1928 table-governing rubrics (Wave 15).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

  editions/1928/front-matter/order-how-psalter-appointed.md
      printed as "THE USE OF THE PSALTER." -- the lineal successor of "The
      Order how the Psalter is appointed to be read" (the same position in the
      book, the same job: the monthly course, the Proper Psalms, the discretion
      clause). Its heading is carried AS PRINTED, so `git diff v1892 v1928`
      shows the rename as a heading change (the Wave-9 concerning-the-service
      precedent).
  editions/1928/front-matter/order-how-rest-of-scripture.md
      printed under the historic title. The cell uses the slug title every
      edition of this file carries.

CORRECTS A WAVE-14 CLAIM. Both rubrics were put in `absent:` at 1892 (and so
at 1928) as "merged into Concerning the Service of the Church". That reading
came from the book's table of contents; the pages print both sections, titled.
1892's cells are built by w14_build_rubrics.py (same source type as 1789).

Source: Lectionary_1928.pdf sheet 1 (vii) and sheet 3 left; witness: scan
pages 4 and 6.
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

SCRIPTURE_TITLE = "The Order how the rest of Holy Scripture is appointed to be read"


def paras(lines):
    """Paragraphs from layout lines: an indented line opens a paragraph. A
    drop capital is displaced by layout mode to the start of the SECOND line
    ("  N places ..." / "Imonth."); it is moved back before the first word."""
    body = [l.rstrip() for l in lines if l.strip()]
    out = []
    for i, l in enumerate(body):
        if re.match(r"^\s{2,}", l) or not out:
            out.append(l.strip())
        else:
            out[-1] += " " + l.strip()
    return out


def dropcap(first, second):
    """'N places where' + 'Imonth.' -> 'IN places where' + 'month.'"""
    m = re.match(r"^([A-Z])(\S)", second.strip())
    if not m:
        raise SystemExit("dropcap: no displaced capital in %r" % second)
    return m.group(1) + first.strip(), second.strip()[1:]


def section(lines, start, stop):
    a = next(i for i, l in enumerate(lines) if re.search(start, l))
    b = next(i for i, l in enumerate(lines[a + 1:], a + 1) if re.search(stop, l))
    body = [l for l in lines[a + 1:b] if l.strip()]
    while body and re.match(r"^\s*[A-Z ]+\.$", body[0].rstrip()):   # heading tail
        body = body[1:]
    first, second = dropcap(body[0], body[1])
    body = ["  " + first, second] + body[2:]
    return [S.norm_ws(p) for p in paras(body)]


def apply(ps, key):
    log = []
    for c in [c for c in W.RUBRICS if c["cell"] == key]:
        hits = [i for i, p in enumerate(ps) if c["text_layer"] in p]
        if len(hits) != 1:
            raise SystemExit("witness (%s): %r found %d times"
                             % (key, c["text_layer"], len(hits)))
        ps[hits[0]] = ps[hits[0]].replace(c["text_layer"], c["scan"], 1)
        log.append(c)
    return log


def write(slug, title, ps):
    p = os.path.join(WT, "editions", "1928", "front-matter", slug + ".md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    text = "\n\n".join(["# " + title] + ps) + "\n"
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("1928  %-30s paragraphs=%d words=%d"
          % (slug, len(ps), sum(len(x.split()) for x in ps)))


def main():
    s1 = S.layout("LEC", 1).split("\n")
    s3 = [l[:140] for l in S.layout("LEC", 3).split("\n")]
    psalter = section(s1, r"THE USE OF THE PSALTER", r"PROPER PSALMS FOR SEASONS")
    scripture = section(s3, r"THE ORDER HOW THE REST OF THE HOLY SCRIPTURE",
                        r"HYMNS AND ANTHEMS")
    n = len(apply(psalter, "psalter")) + len(apply(scripture, "scripture"))
    write("order-how-psalter-appointed", "The Use of the Psalter", psalter)
    write("order-how-rest-of-scripture", SCRIPTURE_TITLE, scripture)
    print("witness corrections=%d" % n)


if __name__ == "__main__":
    main()
