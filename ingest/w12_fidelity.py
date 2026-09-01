#!/usr/bin/env python3
"""w12_fidelity.py — Wave-12 anti-FABRICATION gate.

Every word of every authored cell must occur in the source it was built from.
Wave 12 adds exactly two kinds of editorial text, and only these are allowed:

  1. the psalm POINTER line, which is generated, not transcribed
  2. `<!-- VERIFY ... -->` comments

Anything else a cell contains that its source does not is reported and fails.
"""
from __future__ import annotations
import re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w12_spine as S
import w12_build as B

WT = HERE.parent
FAM = 'occasional-offices'

POINTER_WORDS = set("""verses of follow here the psalm text is carried in psalter not
repeated here""".split())


def toks(t):
    return Counter(w for w in re.sub(r'[^a-z0-9]+', ' ', t.lower()).split() if w)


def main():
    total = bad = 0
    for service, plan in B.PLAN.items():
        for edition, (name, ed) in plan.items():
            f = WT / 'editions' / edition / FAM / f'{service}.md'
            if not f.exists():
                continue
            total += 1
            blocks, _ = S.extract(name, ed)
            src = toks(' '.join(t for _, t in blocks))
            md = f.read_text(encoding='utf-8')
            md = re.sub(r'<!--.*?-->', ' ', md, flags=re.S)
            md = re.sub(r'^>\s*\[.*?\]\s*$', ' ', md, flags=re.M)   # psalm pointer lines
            body = ' '.join(l.lstrip('#> ').strip() for l in md.splitlines())
            missing = {w: n for w, n in toks(body).items()
                       if w not in src and w not in POINTER_WORDS}
            mark = 'CLEAN' if not missing else f'UNATTESTED {list(missing)[:6]}'
            if missing:
                bad += 1
            print(f"  {edition} {service:26s} {mark}")
    print(f"\nfidelity: {total} cells, {bad} with unattested words — "
          f"{'PASS' if bad == 0 else 'REVIEW NEEDED'}")
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
