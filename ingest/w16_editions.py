#!/usr/bin/env python3
"""Wave 16 — declare the three new cells present in editions.yaml.

Same textual edit as w14_editions.py (keeps comments and the flow style).
Idempotent: an entry already listed is not added twice.

  1892 psalter/selections              was inherited from 1789 with a recorded
                                       gap; the book's own table is now sourced
  1892 front-matter/concerning-the-service
  1928 front-matter/concerning-the-service
                                       1789 prints nothing under the title and
                                       keeps its `absent:`; 1892 and 1928 print
                                       the American rules text, so each now
                                       declares its own cell (inheriting would
                                       resolve to 1789's absence)
"""
from __future__ import annotations
import re
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
ADD = {
    '1892': ['front-matter/concerning-the-service', 'psalter/selections'],
    '1928': ['front-matter/concerning-the-service'],
}


def main():
    p = WT / 'editions.yaml'
    text = p.read_text(encoding='utf-8')
    for y, items in ADD.items():
        m = re.search(rf'^  - id: {y}[ \t]*$', text, re.M)
        nxt = re.search(r'^  - id: ', text[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(text) - m.end())
        blk = text[m.start():end]
        mm = re.search(r'^(    present: )\[([^\n]*?)\][ \t]*$', blk, re.M)
        cur = [x.strip() for x in mm.group(2).split(',') if x.strip()]
        new = [s for s in items if s not in cur]
        for s in items:
            if not (WT / 'editions' / y / (s + '.md')).exists():
                raise SystemExit("%s %s: no authored cell" % (y, s))
        ab = re.search(r'^    absent: \[([^\n]*?)\]', blk, re.M)
        if ab and any(s in ab.group(1) for s in items):
            raise SystemExit("%s: a new cell is listed in absent:" % y)
        blk = (blk[:mm.start()] + mm.group(1) + '[' + ', '.join(cur + new) + ']'
               + blk[mm.end():])
        text = text[:m.start()] + blk + text[end:]
        print("  %s present +%s" % (y, new))
    p.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
