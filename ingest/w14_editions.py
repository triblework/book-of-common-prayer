#!/usr/bin/env python3
"""Wave 14 — wire the table and rubric cells into editions.yaml.

Same textual-edit approach as w11/w12_editions.py (preserves comments and the
flow-sequence style) and the same two traps avoided: no re.S, and [ \\t]*$
rather than \\s*$ so the block's trailing newlines survive.

PRESENCE IS DECLARED, NOT COMPUTED. Wave 12 learned this the hard way: deriving
presence from authored files alone put 1892 family-prayer into `absent:`, which
asserted that 1892 DROPPED it. The same trap is everywhere in this wave, because
several editions carry a table we cannot transcribe:

  * `absent:` means THE BOOK DOES NOT HAVE IT. Only 1764 (the Communion-only
    "Wee Bookie") and the genuinely-dropped rubrics at 1892 use it.
  * PRESENT-BUT-UNAUTHORED means the book has it and we inherit the parent's
    text because no allow-listed source gives us this edition's own. That is a
    TRANSCRIPTION GAP, recorded in provenance as `inherited-unreviewed` and
    stated in NOTICE.md and SOURCES.md so no reader mistakes it for "this
    edition reprinted its parent unchanged".

This is why ruling F (originally: the whole Scottish branch takes `absent:` for
tables) is NOT applied literally. 1637 demonstrably prints a Kalendar, so
marking it absent would be a false claim; it inherits with a recorded gap
instead. Only 1764, which really is Communion-only, is absent.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent

PARENT = {'1549': None, '1552': '1549', '1559': '1552', '1604': '1559',
          '1662': '1604', '1637': '1604', '1764': '1637', '1929': '1764',
          '1789': '1662', '1892': '1789', '1928': '1892', '1979': '1928'}
ORDER = ['1549', '1552', '1559', '1604', '1662', '1637', '1764', '1929',
         '1789', '1892', '1928', '1979']

# service -> the editions whose books CARRY it (authored or inherited).
PRESENT = {
    'tables/calendar': ['1549', '1552', '1559', '1604', '1662', '1637',
                        '1789', '1892', '1928', '1979'],
    'tables/proper-lessons': ['1789', '1892', '1928'],
    'tables/feasts-and-fasts': ['1662', '1789', '1892', '1928', '1979'],
    'tables/eucharistic-lectionary': ['1979'],
    'tables/daily-office-lectionary': ['1979'],
    'front-matter/order-how-psalter-appointed':
        ['1549', '1552', '1559', '1604', '1662', '1637', '1789'],
    'front-matter/order-how-rest-of-scripture':
        ['1549', '1552', '1559', '1604', '1662', '1637', '1789', '1979'],
}
SERVICES = sorted(PRESENT)


def authored(year, service):
    return (WT / 'editions' / year / (service + '.md')).exists()


def main(apply=True):
    text = (WT / 'editions.yaml').read_text(encoding='utf-8')
    for y in ORDER:
        par = PARENT[y]
        have = {s for s in SERVICES if y in PRESENT[s]}
        parent_have = {s for s in SERVICES if par and par in PRESENT[s]}
        # present: only services this edition AUTHORS; an inherited service is
        # resolved from the parent and must merely stay out of absent:.
        pres = sorted(s for s in have if authored(y, s))
        inherited = sorted(s for s in have if not authored(y, s))
        absent = sorted(parent_have - have)
        print("  %-5s present %-2d %s%s%s"
              % (y, len(pres), pres,
                 ("  inherits " + str(inherited)) if inherited else '',
                 ("  ABSENT " + str(absent)) if absent else ''))
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
            cur = [x for x in cur if x not in SERVICES]
            cur += items
            blk = (blk[:mm.start()] + mm.group(1) + '['
                   + ', '.join(cur) + ']' + blk[mm.end():])

        add('present', pres)
        add('absent', absent)
        text = text[:m.start()] + blk + text[end:]
    if apply:
        (WT / 'editions.yaml').write_text(text, encoding='utf-8')
        print("editions.yaml updated")


if __name__ == '__main__':
    main(apply='--dry' not in sys.argv)
