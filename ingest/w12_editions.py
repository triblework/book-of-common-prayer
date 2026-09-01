#!/usr/bin/env python3
"""Wave 12 — wire the four deferred sections into editions.yaml.

Same textual-edit approach as w11_editions.py (preserves comments and the
flow-sequence style), and the same two traps avoided: no re.S, and [ \t]*$
rather than \s*$ so the block's trailing newlines survive.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
FAM = 'occasional-offices'
SERVICES = ['prayers-at-sea', 'penitential-office', 'family-prayer', 'prayer-and-thanksgiving']
# Carried by an edition that authors NO file of its own, because it reprints its
# parent's text unchanged -- inheritance by omission. Declaring this explicitly
# matters: computing presence from authored files alone put 1892 family-prayer
# into `absent:`, which would have asserted that 1892 DROPPED Family Prayer. It
# does not; its index links straight to the 1789 page.
INHERITS = {
 '1892': {'family-prayer'},   # 1892 index links ../1789/Family_Prayer_1789.htm
}

PARENT = {'1549': None, '1552': '1549', '1559': '1552', '1604': '1559',
          '1662': '1604', '1637': '1604', '1764': '1637', '1929': '1764',
          '1789': '1662', '1892': '1789', '1928': '1892', '1979': '1928'}


def carried(year):
    d = WT / 'editions' / year / FAM
    have = {s for s in SERVICES if (d / f'{s}.md').exists()} if d.is_dir() else set()
    return have | INHERITS.get(year, set())


def main(apply=True):
    C = {y: carried(y) for y in PARENT}
    text = (WT / 'editions.yaml').read_text(encoding='utf-8')
    for y, par in PARENT.items():
        # an inherited service is PRESENT but authors no file, so it must not be
        # emitted into present: as if a file backed it -- the builder resolves it
        # from the parent. It simply must not land in absent:.
        pres = sorted(C[y] - INHERITS.get(y, set()))
        absent = sorted(C[par] - C[y]) if par else []
        inh = sorted(INHERITS.get(y, set()))
        print(f"  {y}: present {len(pres)} {pres}"
              + (f"  inherits {inh}" if inh else '')
              + (f"  absent {absent}" if absent else ''))
        if not apply:
            continue
        m = re.search(rf'^  - id: {y}\s*$', text, re.M)
        nxt = re.search(r'^  - id: ', text[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(text) - m.end())
        blk = text[m.start():end]

        def add(field, items):
            nonlocal blk
            mm = re.search(rf'^(    {field}: )\[([^\n]*?)\][ \t]*$', blk, re.M)
            cur = [x.strip() for x in mm.group(2).split(',') if x.strip()]
            cur = [x for x in cur if x.split('/')[-1] not in SERVICES or not x.startswith(FAM + '/')]
            cur += [f'{FAM}/{s}' for s in items]
            blk = blk[:mm.start()] + mm.group(1) + '[' + ', '.join(cur) + ']' + blk[mm.end():]

        add('present', pres)
        add('absent', absent)
        text = text[:m.start()] + blk + text[end:]
    if apply:
        (WT / 'editions.yaml').write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main(apply='--dry' not in sys.argv)
