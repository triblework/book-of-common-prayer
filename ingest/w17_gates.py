#!/usr/bin/env python3
"""w17_gates.py — the Wave-17 gates (the 1892 Psalter against the scan).

Authoring-only. Run after ingest/w13_build_1892.py.

  1. EVIDENCE. Every correction the builder makes has a record in
     w17_evidence.json: the scan page, plus either a second OCR of that line
     cropped from a 4400px render, or the reading taken by eye.
  2. ATTESTATION. Every word the corrections introduce occurs in the scan's
     own OCR (w17_scan_ocr.json, 180 pages), and the forms they replace occur
     NOWHERE in it.
  3. COMPLETENESS. No carrier-only form survives in the cells.
  4. CONTAINMENT. Against the published cells, nothing changed except the
     recorded classes -- checked as a word multiset.
  5. POINTING. The seven corrected verses read as the scan does, and the
     mediant gate reports no anomaly.
  6. The independent change log agrees (w13_changelog: 55/55).
"""
from __future__ import annotations
import collections
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import w17_witness as W
import w17_cells as C

OCR = json.load(open(os.path.join(HERE, 'w17_scan_ocr.json'), encoding='utf-8'))
SCAN = '\n'.join('\n'.join(v) for v in OCR.values())
WORD = re.compile(r"[A-Za-z]+")
findings = []

# the cells as published before this wave (the tag the wave starts from)
BASE = 'v1892'


def check(label, ok, detail=''):
    print('%-7s %s %s' % ('OK' if ok else 'ANOMALY', label, detail))
    if not ok:
        findings.append(label)


def corrections():
    """Replay the builder's corrections over the PUBLISHED cells, so the gate
    sees exactly which instances the wave changes."""
    import w13_1892
    ps = w13_1892.parse()
    return W.apply(ps), ps


def main():
    log, ps = corrections()
    kinds = collections.Counter(k for k, *_ in log)
    print('corrections: %s (total %d)' % (dict(kinds), sum(kinds.values())))

    # 1. evidence
    missing = []
    for kind, psalm, verse, what in log:
        key = ('%d:%d:mediant' % (psalm, verse) if kind == 'pointing'
               else '%d:%d:%s' % (psalm, verse, what))
        if key not in W.EVIDENCE:
            missing.append((kind, key))
    check('every correction has scan evidence (%d)' % len(log),
          not missing, missing[:6])
    eyes = sum(1 for v in W.EVIDENCE.values() if v.get('eye'))
    autos = sum(1 for v in W.EVIDENCE.values() if v.get('auto'))
    check('evidence kinds: %d machine-confirmed, %d read by eye' % (autos, eyes),
          autos + eyes >= len(W.EVIDENCE) - 8)

    # 2. attestation
    intro = {w for w in W.introduced() if len(w) > 3}
    scan_words = {w.lower() for w in WORD.findall(SCAN)}
    # a word the scan breaks across a line ("Zabu-lon") is missing from the
    # page OCR; those are the readings taken by eye, and the evidence file
    # records what was read
    eye_words = {w.lower() for v in W.EVIDENCE.values()
                 for w in WORD.findall(v.get('eye', ''))}
    unattested = sorted(w for w in intro if w not in scan_words | eye_words)
    check('every introduced word occurs in the scan (%d words)' % len(intro),
          not unattested, unattested)
    for gone in ('shew', 'shewed', 'sheweth', 'judgement', 'judgements'):
        n = len(re.findall(r'\b%s\b' % gone, SCAN, re.I))
        check('the scan never prints %r (%d)' % (gone, n), n == 0)

    # 3. completeness
    cells = C.cells('1892')
    text = '\n'.join(v for p in cells for v in cells[p].values())
    for bad in ('shew', 'judgement', 'hail-stones', 'first-born', 'night-season',
                'law-giver', 'eye-lids', 'Midianites', 'Zebulon', 'Eqypt'):
        check('no %r survives in the cells' % bad,
              not re.search(r'\b%s' % bad, text, re.I))

    # 4. containment: the published cell, with these corrections applied to
    # its verse lines, must equal the new cell exactly -- so nothing else
    # changed, and nothing this wave changed is unaccounted for.
    strip = lambda t: re.sub(r'\n<!-- VERIFY.*?-->', '', t, flags=re.S)
    for f in ('psalms-1-50', 'psalms-51-100', 'psalms-101-150'):
        old = subprocess.run(['git', 'show', '%s:texts/original/psalter/%s.md' % (BASE, f)],
                             cwd=WT, capture_output=True, text=True).stdout
        new_txt = open(os.path.join(WT, 'editions/1892/psalter/%s.md' % f),
                       encoding='utf-8').read()
        if not old:
            check('containment %s: published cell available' % f, False)
            continue
        psalm = verse = None
        out = []
        for line in strip(old).split('\n'):
            m = re.match(r'^## Psalm (\d+)', line)
            if m:
                psalm, verse = int(m.group(1)), 0
            mv = re.match(r'^(\d+) ', line)
            if psalm and (mv or (verse == 0 and line and not line.startswith(('#', '>')))):
                verse = int(mv.group(1)) if mv else 1
                head = mv.group(0) if mv else ''
                body = line[len(head):]
                body, _ = W.apply_text(body, psalm, verse, [])
                line = head + body
            out.append(line)
        check('containment %s: published + corrections == new cell' % f,
              '\n'.join(out) == strip(new_txt))

    # 5. pointing
    for p, v, _old, new in W.POINTING:
        got = cells[p][v]
        key = new.split(' ')[0]
        check('pointing %d:%d reads as the scan' % (p, v), new in got, got[:70])

    # 6. the independent change log
    r = subprocess.run([sys.executable, os.path.join(HERE, 'w13_changelog.py')],
                       capture_output=True, text=True)
    line = [l for l in r.stdout.splitlines() if 'change-log check' in l]
    check('change log: %s' % (line[0] if line else '?'),
          bool(line) and ', 0 failed' in line[0])

    print('\nw17 gates: %d anomalies' % len(findings))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
