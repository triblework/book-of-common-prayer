#!/usr/bin/env python3
"""Wave 11 — wire prayers-and-thanksgivings into editions.yaml.

Edits the YAML TEXTUALLY (not via a yaml round-trip) so the file's comments and
flow-sequence style survive. present: = the slugs that edition carries;
absent: = what its PARENT carried and it does not (a real drop, or a
relocation, which NOTICE.md distinguishes).
"""
from __future__ import annotations
import re, sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
FAMILY = 'prayers-and-thanksgivings'
PARENT = {'1549': None, '1552': '1549', '1559': '1552', '1604': '1559',
          '1662': '1604', '1637': '1604', '1764': '1637', '1929': '1764',
          '1789': '1662', '1892': '1789', '1928': '1892', '1979': '1928'}


def carried(year):
    d = WT / 'editions' / year / FAMILY
    return {p.stem for p in d.glob('*.md')} if d.is_dir() else set()


def main(apply=True):
    C = {y: carried(y) for y in PARENT}
    text = (WT / 'editions.yaml').read_text(encoding='utf-8')
    report = []
    for y, par in PARENT.items():
        own = C[y]
        pres = sorted(own)
        absent = sorted(C[par] - own) if par else []
        report.append((y, len(pres), len(absent), absent))
        if not apply:
            continue
        # locate this edition's block
        m = re.search(rf'^  - id: {y}\s*$', text, re.M)
        if not m:
            raise SystemExit(f"edition {y} not found in editions.yaml")
        nxt = re.search(r'^  - id: ', text[m.end():], re.M)
        blk_end = m.end() + (nxt.start() if nxt else len(text) - m.end())
        blk = text[m.start():blk_end]

        def add(field, items):
            nonlocal blk
            # Two traps here, both hit:
            #  * no re.S -- with DOTALL the non-greedy match jumped the newline
            #    and swallowed from 'present: [' to the ']' of 'absent: []'.
            #  * '[ \t]*$' not '\s*$' -- \s* ate the block's TRAILING NEWLINES,
            #    so writing the block back glued the next edition's '- id:'
            #    onto the end of the absent line and the block vanished.
            mm = re.search(rf'^(    {field}: )\[([^\n]*?)\][ \t]*$', blk, re.M)
            if not mm:
                raise SystemExit(f"{y}: no {field}: field")
            cur = [x.strip() for x in mm.group(2).split(',') if x.strip()]
            cur = [x for x in cur if not x.startswith(FAMILY + '/')]
            cur += [f'{FAMILY}/{s}' for s in items]
            blk = blk[:mm.start()] + mm.group(1) + '[' + ', '.join(cur) + ']' + blk[mm.end():]

        add('present', pres)
        add('absent', absent)
        text = text[:m.start()] + blk + text[blk_end:]
    if apply:
        (WT / 'editions.yaml').write_text(text, encoding='utf-8')
    for y, np_, na, ab in report:
        extra = f"  <- drops/relocates: {', '.join(ab)}" if ab else ''
        print(f"  {y}: present {np_:3d}  absent {na}{extra}")


if __name__ == '__main__':
    main(apply='--dry' not in sys.argv)
