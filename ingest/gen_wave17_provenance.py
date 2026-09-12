#!/usr/bin/env python3
"""Wave 17 — provenance for the 1892 Psalter read against the Standard Book scan.

AMENDS the three 1892 psalter records: the note gains the witness pass, and
the fourteen verify_items they carried are replaced by the single reading the
scan cannot settle.

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import collections
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))
import w17_witness as W
import w13_1892

MARK = 'Wave 17:'
SCAN = ('http://justus.anglican.org/resources/bcp/1892Standard/1892standard.pdf')
FILES = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')


def counts():
    ps = w13_1892.parse()
    log = W.apply(ps)
    per = collections.Counter()
    for kind, psalm, _v, _w in log:
        f = ('psalms-1-50' if psalm <= 50 else
             'psalms-51-100' if psalm <= 100 else 'psalms-101-150')
        per[(f, kind)] += 1
        per[f] += 1
    return per


def note_for(f, per):
    k = lambda kind: per[(f, kind)]
    return (
        ' Wave 17: CORRECTED against a SCAN of the 1892 Standard Book, '
        'subscribers\' edition (%s, 596 bitonal page images, no text layer; the '
        'Psalter is scan pp. 357-536). The PDF this file was transcribed from '
        'is NOT the 1892 text in its spelling: it prints "shew" and '
        '"judgement" where the book prints "show" and "judgment" -- neither '
        'older form occurs on any of the 180 scanned pages. %d corrections in '
        'this file: %d spelling, %d hyphenation (the book is not uniform: it '
        'closes "hailstones" and "lawgiver", keeps "wash-pot", spaces "night '
        'season"), %d single readings and %d verses whose mediant the PDF had '
        'lost or altered. All fourteen of Wave 13\'s VERIFYs are resolved, and '
        'the independent change log now agrees with this text 55 of 55 (it was '
        '51 of 55; the scan showed the log right about all four). Every '
        'correction is evidenced in ingest/w17_evidence.json -- the scan page '
        'plus either a second OCR of that line cropped from a 4400px render or '
        'the reading taken by eye; the scan\'s own page OCR is kept in '
        'ingest/w17_scan_ocr.json and the corrections in ingest/w17_witness.py.'
        % (SCAN, per[f], k('spelling'), k('hyphen'), k('word'), k('pointing')))


WATER_SIDE = (
    'water-side',
    "the 1892 Standard Book scan breaks this word across a line (\"water-\" / "
    "\"side\"), so the page cannot say whether the word is hyphenated; the "
    "Standard Book's keyed text (1892Standard/psalter.pdf) prints "
    "\"waterside\". Carried as the 1892 PDF prints it")


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8')
    if MARK in body:
        print('already applied')
        return
    per = counts()
    for f in FILES:
        m = re.search(r'^  - edition: 1892\n    service: psalter/%s\n' % f, body, re.M)
        if not m:
            raise SystemExit('record not found: %s' % f)
        nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(body) - m.end())
        blk = body[m.start():end]
        nm = re.search(r'^    note: "(.*)"$', blk, re.M)
        blk = (blk[:nm.start()] + '    note: '
               + q(nm.group(1).replace('\\"', '"').rstrip() + note_for(f, per))
               + blk[nm.end():])
        items = ['    verify_items: []\n']
        if f == 'psalms-1-50':
            items = ['    verify_items:\n',
                     '      - anchor: %s\n' % q(f),
                     '        source_reading: %s\n' % q(WATER_SIDE[0]),
                     '        note: %s\n' % q(WATER_SIDE[1])]
        blk = re.sub(r'^    verify_items:\n(?:      .*\n|        .*\n)*',
                     ''.join(items), blk, flags=re.M)
        body = body[:m.start()] + blk + body[end:]
        print('  %s: %d corrections, verify_items -> %d'
              % (f, per[f], 1 if f == 'psalms-1-50' else 0))
    p.write_text(body, encoding='utf-8')


if __name__ == '__main__':
    main()
