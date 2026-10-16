#!/usr/bin/env python3
"""Wave 21 — provenance for the 1928 Psalter read against two page scans.

AMENDS the three 1928 psalter records: each note gains the witness pass, and
the verify_items are regenerated FROM THE CELLS (the three Wave-13 'no
mediant' items are gone; the seven flags Wave 21 opens are indexed), so the
index cannot drift from the inline flags it indexes.

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import collections
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))
import w21_witness as W
import w13_1928

MARK = 'Wave 21:'
SCAN = 'http://justus.anglican.org/resources/bcp/1928/BCP1929.pdf'
FACS = 'https://justus.anglican.org/resources/bcp/1928Standard/1952std.pdf'
FILES = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')
VERIFY_RE = re.compile(r'<!--\s*VERIFY:?\s*(.*?)-->', re.S)


def counts():
    ps = w13_1928.parse()
    log = W.apply(ps)
    per = collections.Counter()
    for kind, psalm, _v, _k in log:
        f = ('psalms-1-50' if psalm <= 50 else
             'psalms-51-100' if psalm <= 100 else 'psalms-101-150')
        per[(f, kind)] += 1
        per[f] += 1
    return per


DISAGREE = {
    'psalms-1-50': ('In this file the two printings differ at 18:10 (1929 prints no '
                    'asterisk), 32:3 (1929 "while", flagged), 37:20 (1929 no comma) and '
                    '37:38 (1929 "being", a misprint); the cell keeps the Standard Book '
                    'reading in each. The facsimile settles 1:3 "water-side", which the '
                    '1929 printing breaks at a line end, as the carrier prints it.'),
    'psalms-51-100': ('In this file the two printings differ at 55:14 (1929 "old", '
                      'flagged), 69:31 (1929 "thanskgiving", a misprint) and 73:20 (1929 '
                      'prints no asterisk); the cell keeps the Standard Book reading in '
                      'each. The facsimile settles 80:10 "cedar-trees" as the carrier '
                      'prints it.'),
    'psalms-101-150': ('In this file the two printings differ at 116:15 (1929 '
                       '"thanskgiving", a misprint), 119:25 (1929 drops the Y of MY after '
                       'the drop capital) and 123:2 (1929 prints no asterisk); the cell '
                       'keeps the Standard Book reading in each. The facsimile settles '
                       '104:17 "fir-trees" as the carrier prints it and 139:1 "up-rising", '
                       'which is corrected. "The End of the Psalter.", which the carrier had '
                       'fused into 150:6, is deleted as book furniture (R20).'),
}


def note_for(f, per):
    k = lambda kind: per[(f, kind)]
    return (
        ' Wave 21: READ AGAINST A SCAN OF THE ORIGINAL 1928 PRINTING -- '
        '1928/BCP1929.pdf (%s), the Cambridge Edition certified in 1929 by the '
        'Custodian against a certified copy of the Standard Book, 319 '
        'two-page JPX spreads; the Psalter is scans 192R-282R (book pp. '
        '345-525). A SECOND WITNESS within limits (RULINGS R19) is the 1952 '
        'facsimile of the Standard Book, 1928Standard/1952std.pdf (%s), which '
        'its own certificate shows to be the text as amended to 1952: it '
        'corroborates where both printings agree and settles a compound the '
        '1929 printing breaks at a line end; where the printings disagree the '
        'cell keeps the Standard Book reading and the difference is recorded, '
        'never imported. Every verse was aligned to both scans on a skeleton '
        'of its words; every mediant was resolved on both (the three Wave-13 '
        '"no mediant" flags are closed: both printings point 18:28, 109:21 and '
        '119:1); every cell word the page OCR did not attest, and every scan '
        'word the cell lacked, was read twice by machine and, where that did '
        'not settle it, by eye off 4400px crops (ingest/w21_eye.txt, '
        'ingest/w21_evidence.json). %d corrections in this file: %d pointing, '
        '%d reading, %d spacing, %d hyphenation (the book hyphenates '
        'compounds the carrier closes: cheek-bone, us-ward, by-word, '
        'mercy-seat, loving-kindness), %d structure. %s Compounds broken at a '
        'line end in BOTH printings keep the carrier\'s form and are flagged. '
        'The corrections are in ingest/w21_witness.py, applied by '
        'ingest/w13_build.py; the scans\' own OCR is kept in '
        'ingest/w21_1929_ocr.json and ingest/w21_1952_ocr.json; the gates are '
        'ingest/w21_gates.py.'
        % (SCAN, FACS, per[f], k('pointing'), k('reading'), k('spacing'),
           k('hyphen'), k('structure'), DISAGREE[f]))


def inline_items(f):
    path = WT / 'editions' / '1928' / 'psalter' / (f + '.md')
    out = []
    for m in VERIFY_RE.finditer(path.read_text(encoding='utf-8')):
        body = re.sub(r'\s+', ' ', m.group(1)).strip()
        q_ = re.search(r"'([^']+)'", body)
        reading = q_.group(1) if q_ else body[:40]
        note = re.sub(r"^'%s';?\s*" % re.escape(reading), '', body)
        out.append((f, reading, note))
    return out


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
        m = re.search(r'^  - edition: 1928\n    service: psalter/%s\n' % f, body, re.M)
        if not m:
            raise SystemExit('record not found: %s' % f)
        nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(body) - m.end())
        blk = body[m.start():end]
        nm = re.search(r'^    note: (["\'])(.*)\1$', blk, re.M)
        if nm:
            was = (nm.group(2).replace('\\"', '"') if nm.group(1) == '"'
                   else nm.group(2).replace("''", "'"))
        else:
            nm = re.search(r'^    note: (?!["\'])(.*)$', blk, re.M)
            if not nm:
                raise SystemExit('note not found: %s' % f)
            was = nm.group(1)
        blk = (blk[:nm.start()] + '    note: ' + q(was.rstrip() + note_for(f, per))
               + blk[nm.end():])
        items = inline_items(f)
        if items:
            lines = ['    verify_items:\n']
            for anchor, reading, note in items:
                lines += ['      - anchor: %s\n' % q(anchor),
                          '        source_reading: %s\n' % q(reading),
                          '        note: %s\n' % q(note)]
        else:
            lines = ['    verify_items: []\n']
        blk = re.sub(r'^    verify_items:(?: \[\])?\n(?:      .*\n|        .*\n)*',
                     ''.join(lines), blk, flags=re.M)
        body = body[:m.start()] + blk + body[end:]
        print('  1928 psalter/%-16s %d corrections, verify_items -> %d'
              % (f, per[f], len(items)))
    p.write_text(body, encoding='utf-8')


if __name__ == '__main__':
    main()
