#!/usr/bin/env python3
"""w12_audit.py — Wave-12 anti-LOSS gate (ingest/AUDIT_METHOD.md).

Fidelity proves nothing was invented and is blind to text that never arrived.
This asks the other question, in four ways:

  1. every declared present: resolves to a file OR a declared inheritance
  2. no service disappears along a lineage and returns (a parse miss, not history)
  3. the psalm collapse is ACCOUNTED: pointer verse-counts must sum to exactly the
     psalm blocks the spine found, so no ordinary text was swallowed into a run
  4. no cell is suspiciously empty
"""
from __future__ import annotations
import re, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w12_spine as S
import w12_build as B
import w12_editions as E

WT = HERE.parent
FAM = 'occasional-offices'
SERVICES = E.SERVICES
CHAINS = [('English', ['1549', '1552', '1559', '1604', '1662']),
          ('Scottish', ['1604', '1637', '1764', '1929']),
          ('American', ['1662', '1789', '1892', '1928', '1979'])]


def carried(y):
    d = WT / 'editions' / y / FAM
    return {s for s in SERVICES if (d / f'{s}.md').exists()} if d.is_dir() else set()


def main():
    bad = 0
    ed = {str(e['id']): e for e in yaml.safe_load((WT/'editions.yaml').read_text())['editions']}

    print("== 1. declared presence resolves ==")
    for y, e in ed.items():
        pres = {x.split('/')[-1] for x in (e.get('present') or [])
                if x.startswith(FAM+'/') and x.split('/')[-1] in SERVICES}
        ab = {x.split('/')[-1] for x in (e.get('absent') or [])
              if x.startswith(FAM+'/') and x.split('/')[-1] in SERVICES}
        inh = E.INHERITS.get(y, set())
        missing = pres - carried(y) - inh
        both = pres & ab
        if missing or both:
            bad += 1
            print(f"  !! {y}: declared-but-unresolved={sorted(missing)} both={sorted(both)}")
    if not bad:
        print("  OK")

    print("\n== 2. contiguity along each lineage ==")
    for name, chain in CHAINS:
        eff = {}
        for y in chain:
            eff[y] = carried(y) | E.INHERITS.get(y, set())
        # an inherited service is present at that node; carry it forward
        prev = set()
        for y in chain:
            declared_absent = {x.split('/')[-1] for x in (ed[y].get('absent') or [])
                               if x.startswith(FAM+'/')}
            eff[y] = (eff[y] | (prev - declared_absent)) if y != chain[0] else eff[y]
            prev = eff[y]
        gaps = []
        for s in SERVICES:
            pat = [1 if s in eff[y] else 0 for y in chain]
            if 1 in pat:
                first, last = pat.index(1), len(pat)-1-pat[::-1].index(1)
                if 0 in pat[first:last+1]:
                    gaps.append((s, ''.join(map(str, pat))))
        if gaps:
            bad += len(gaps)
            for s, p in gaps:
                print(f"  !! {name}: {s} discontinuous {p}")
        else:
            print(f"  {name}: OK")

    print("\n== 3. psalm collapse accounted ==")
    for edition, (name, e) in B.PLAN['prayers-at-sea'].items():
        blocks, _ = S.extract(name, e)
        n_psalm = sum(1 for k, _ in blocks if k == 'psalm')
        f = WT/'editions'/edition/FAM/'prayers-at-sea.md'
        counted = sum(int(m.group(1)) for m in
                      re.finditer(r'^>\s*\[(\d+)\s+(?:verses|psalm verses)', f.read_text(encoding='utf-8'), re.M))
        ok = 'OK' if counted == n_psalm else '!! MISMATCH'
        if counted != n_psalm:
            bad += 1
        print(f"  {edition}: spine psalm blocks={n_psalm}  pointer verse-count={counted}  {ok}")

    print("\n== 4. cell size sanity ==")
    for service, plan in B.PLAN.items():
        for edition in plan:
            f = WT/'editions'/edition/FAM/f'{service}.md'
            if not f.exists():
                continue
            n = len(f.read_text(encoding='utf-8'))
            if n < 800:
                bad += 1
                print(f"  !! {edition} {service}: only {n} bytes")
    print("  OK" if not bad else "")
    print(f"\naudit: {bad} anomal{'y' if bad==1 else 'ies'}")
    return bad


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 1)
