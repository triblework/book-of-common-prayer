#!/usr/bin/env python3
"""w11_audit.py — Wave-11 anti-LOSS gate (ingest/AUDIT_METHOD.md).

The fidelity gate proves nothing was invented; it is structurally blind to text
that quietly failed to arrive. This asks the other question.

This block GROWS across the editions, so a plain cross-edition majority test
would flag a great deal of perfectly real absence. The sharp signal here is
CONTIGUITY along a lineage: a prayer present, then absent, then present again is
almost certainly a parser miss, because a book that drops a prayer and a later
book that independently restores it is rare and always noteworthy. Every such
gap is either a real, documented restoration or a bug.

Also checks:
  * every present: entry in editions.yaml resolves to an authored file
  * no slug appears in both present: and absent:
  * counts per edition match the authored cells

Reports; does not fail the build (legitimate absence is common in this corpus).
"""
from __future__ import annotations
import sys
from pathlib import Path
import yaml

WT = Path(__file__).resolve().parent.parent
FAMILY = 'prayers-and-thanksgivings'

CHAINS = [
    ('English', ['1549', '1552', '1559', '1604', '1662']),
    ('Scottish', ['1604', '1637', '1764', '1929']),
    ('American', ['1662', '1789', '1892', '1928', '1979']),
]

# A gap that is genuinely the books, with a source-checked reason.
KNOWN_GOOD = {
    ('English', 'in-time-of-dearth-and-famine-2'):
        "REAL drop-and-restore. 1552 prints a second dearth prayer under 'Or thus'; "
        "1559 and 1604 drop it; 1662 restores it as 'In the time of Dearth and "
        "Famine. (ii)'. Checked by text: the 1552 and 1662 forms share an opening "
        "modulo period spelling, and each matches the other far better than either "
        "matches the first dearth prayer — so the slug is right and the gap is history.",
    ('American', 'for-all-conditions-of-men'):
        "REAL round-trip, not a parse gap. 1662 prints it in this section; the "
        "American line 1789-1928 moves it into BOTH Morning and Evening Prayer "
        "(verified: '## A Prayer for all Conditions of Men' is an MP/EP anchor "
        "there); 1979 brings it back here (#2) and its MP/EP carry the anchor no "
        "longer. Recorded in NOTICE.md as a relocation, not a deletion.",
    ('American', 'thanksgiving-general'):
        "REAL round-trip, same as for-all-conditions-of-men: in this section at "
        "1662, an MP/EP anchor across 1789-1928, back in this section at 1979 "
        "(Thanksgiving #1) with no MP/EP anchor. Verified in daily-office/.",
}

# Editions that carry none of this block at all, categorically.
EXPECTED_EMPTY = {
    '1549': 'the block does not exist yet — the 1549 Litany ends at the Chrysostom collect',
    '1764': 'the Communion-only "Wee Bookie"',
    '1929': 'inherits the Communion-only Scottish line',
}


def carried(year):
    d = WT / 'editions' / year / FAMILY
    return {p.stem for p in d.glob('*.md')} if d.is_dir() else set()


def main():
    ed = {e['id']: e for e in yaml.safe_load((WT / 'editions.yaml').read_text())['editions']}
    anomalies = 0

    # 1. editions.yaml <-> authored files
    print("== declaration vs authored files ==")
    for y, e in ed.items():
        pres = {x.split('/', 1)[1] for x in (e.get('present') or []) if x.startswith(FAMILY + '/')}
        ab = {x.split('/', 1)[1] for x in (e.get('absent') or []) if x.startswith(FAMILY + '/')}
        files = carried(str(y))
        both = pres & ab
        missing = pres - files
        extra = files - pres
        if both or missing or extra:
            anomalies += 1
            print(f"  !! {y}: both={sorted(both)} declared-but-no-file={sorted(missing)} "
                  f"file-but-not-declared={sorted(extra)}")
    if not anomalies:
        print("  OK — every present: entry resolves to a file; no slug in both lists")

    # 2. contiguity along each lineage
    print("\n== contiguity along each lineage ==")
    for name, chain in CHAINS:
        sets = {y: carried(y) for y in chain}
        allslugs = sorted(set().union(*sets.values()))
        gaps = []
        for s in allslugs:
            pat = [1 if s in sets[y] else 0 for y in chain]
            first, last = pat.index(1), len(pat) - 1 - pat[::-1].index(1)
            if 0 in pat[first:last + 1]:
                if (name, s) in KNOWN_GOOD:
                    continue
                gaps.append((s, ''.join(str(x) for x in pat)))
        if gaps:
            anomalies += len(gaps)
            print(f"  {name} ({'->'.join(chain)}): {len(gaps)} DISCONTINUOUS slug(s)")
            for s, pat in gaps:
                print(f"      !! {s:46s} {pat}")
        else:
            print(f"  {name} ({'->'.join(chain)}): OK — no slug disappears and returns")

    # 3. categorically empty editions
    print("\n== editions carrying none of the block ==")
    for y, why in EXPECTED_EMPTY.items():
        n = len(carried(y))
        ok = 'OK' if n == 0 else f'!! carries {n}'
        print(f"  {y}: {ok} — {why}")
        if n:
            anomalies += 1

    print(f"\naudit: {anomalies} anomal{'y' if anomalies == 1 else 'ies'}")
    return anomalies


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 1)
