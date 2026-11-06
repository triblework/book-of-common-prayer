#!/usr/bin/env python3
"""Wave 24 — provenance for the 1892 Psalter's letter case (RULINGS R23).

A FOLLOW-UP to gen_wave22_provenance.py, whose marker ("Wave 22:") makes it a
no-op on this file: each of the three 1892 psalter records gains one sentence
saying that letter case, which Wave 22 keyed and left off, now follows the
book, with this file's counts read from w22_witness (so the note cannot drift
from the switches), and what is still off. The verify_items are untouched:
Wave 24 opens and closes no flag.

Re-runnable: the Wave 24 sentence is the note's last, and a second run
replaces it (so a later ruling on the possessive is a switch, a rebuild and
this).
"""
from __future__ import annotations
import collections
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))
import w22_witness as W

FILES = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')
SENT = re.compile(r' Wave 24: .*$')


def file_of(psalm):
    return 'psalms-1-50' if psalm <= 50 else 'psalms-51-100' if psalm <= 100 else 'psalms-101-150'


def note_for(f, per):
    k = lambda g: per[(f, g)]
    on = W.GROUPS.get('CASE_POSSESSIVE')
    s = (' Wave 24: LETTER CASE, which Wave 22 keyed and left off, now follows the book '
         '(RULINGS R23, maintainer 2026-11-06): %d corrections in this file -- %d of the '
         'small-capital divine name (LORD, GOD, JEHOVAH, either way), %d verse-1 openings (the '
         'book capitalizes only the first word), %d other capitals -- each an eye read with its '
         'scan page in ingest/w22_evidence.json (%d records since Wave 24), switched on in '
         'ingest/w22_witness.py.'
         % (k('CASE_LORD') + k('CASE_OPENING') + k('CASE_CAPS'), k('CASE_LORD'),
            k('CASE_OPENING'), k('CASE_CAPS'), len(W.EVIDENCE)))
    if on:
        s += (' The possessive of small-capital LORD is set as the book prints it, with a '
              'lower-case s ("LORD\'s"; %d in this file; eye record ingest/w24_eye.txt).'
              % k('CASE_POSSESSIVE'))
    else:
        s += (' Not taken: the possessive of small-capital LORD, which the book sets with a '
              'lower-case s ("LORD\'s") where this file prints "LORD\'S" -- %d in this file, read '
              'by eye (ingest/w24_eye.txt) and keyed, switched off until the encoding is ruled '
              '(R23).' % k('CASE_POSSESSIVE'))
    return s


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    per = collections.Counter((file_of(p), g) for p, v, a, b, i, g in W.CASE)
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8')
    for f in FILES:
        m = re.search(r'^  - edition: 1892\n    service: psalter/%s\n' % f, body, re.M)
        if not m:
            raise SystemExit('record not found: %s' % f)
        nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(body) - m.end())
        blk = body[m.start():end]
        nm = re.search(r'^    note: "(.*)"$', blk, re.M)
        if not nm or 'Wave 22:' not in nm.group(1):
            raise SystemExit('Wave 22 note not found: %s' % f)
        was = re.sub(r'\\(.)', r'\1', nm.group(1))
        was = SENT.sub('', was)
        blk = blk[:nm.start()] + '    note: ' + q(was + note_for(f, per)) + blk[nm.end():]
        body = body[:m.start()] + blk + body[end:]
        print('  1892 psalter/%-16s case %d on, possessive %d %s'
              % (f, sum(per[(f, g)] for g in ('CASE_LORD', 'CASE_OPENING', 'CASE_CAPS')),
                 per[(f, 'CASE_POSSESSIVE')],
                 'on' if W.GROUPS.get('CASE_POSSESSIVE') else 'off'))
    p.write_text(body, encoding='utf-8')


if __name__ == '__main__':
    main()
