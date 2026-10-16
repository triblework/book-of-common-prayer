#!/usr/bin/env python3
"""Wave 22 — provenance for the 1892 Psalter's full pointing and punctuation
collation against the Standard Book scan.

AMENDS the three 1892 psalter records: each note gains this pass, and the
verify_items are regenerated FROM THE CELLS (the water-side note is the
corrected one; three flags are new), so the index cannot drift from the
inline flags it indexes.

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import collections
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))
import w22_witness as W
import w17_witness
import w13_1892

MARK = 'Wave 22:'
FILES = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')
VERIFY_RE = re.compile(r'<!--\s*VERIFY:?\s*(.*?)-->', re.S)


def counts():
    ps = w13_1892.parse()
    w17_witness.apply(ps)
    log = W.apply(ps)
    per = collections.Counter()
    verses = collections.defaultdict(set)
    for grp, psalm, verse, _tag in log:
        f = ('psalms-1-50' if psalm <= 50 else
             'psalms-51-100' if psalm <= 100 else 'psalms-101-150')
        per[(f, grp)] += 1
        per[f] += 1
        verses[f].add((psalm, verse))
    return per, {f: len(v) for f, v in verses.items()}


PER = {
    'psalms-1-50': ' In this file: the carrier\'s "our" for "out" (22:7), "thou I walk" (23:4), "more then" (52:4 is in the next file), "rasor" and "cloke" where the book prints razor and cloak, and "strong hold" for the book\'s "stronghold".',
    'psalms-51-100': ' In this file: the mediant moved to the book\'s word at 100:2 ("ourselves") and 39:14 is in the file before; "our" for "out" (68:31), "mixed" for "mixt" (75:9), "intreated", "unperfect", "slipt", "stablished" regularized to the book\'s forms.',
    'psalms-101-150': ' In this file: "thy" for "they" (107:28, 124:2), a "had" the book does not print (106:37), "good will" for "goodwill" (109:4); 107:1 and 139:7, where the book sets a semicolon at the mediant and no colon in the verse, keep the repo\'s " : " and are flagged (R21); 139:11\'s damaged stop is flagged; "THE END OF THE PSALTER", which the carrier had fused into 150:6, is deleted as book furniture (R20).',
}


def note_for(f, per, nverses):
    k = lambda g: per[(f, g)]
    return (
        ' Wave 22: THE FULL POINTING AND PUNCTUATION COLLATION against the same '
        'Standard Book scan. Wave 17 checked pointing only where the mediant gate '
        'flagged an anomaly; this pass read EVERY mediant in all 2,508 verses by '
        'eye off 4400px crops stacked into labelled strips (the machine found '
        'the places; a 150-verse control sample, seed 20261016, disagreed with '
        'the machine in 0 of 150, and the full pass found no further difference). '
        'Four verses differ: at 39:14 and 100:2 the mediant moves to the book\'s '
        'word; at 107:1 and 139:7 the book sets a semicolon where the mediant '
        'stands and no colon in the verse, so the cell keeps the repo\'s " : " '
        'and a flag records the book\'s mark (RULINGS R21). The pass also found '
        'that this carrier was keyed over the 1662 Psalter and carries its '
        'STOPS: 440 places where the page OCR and the cell disagreed were read '
        'by eye, 328 were real, and ordinary punctuation now follows the book '
        '(commas the book adds or lacks, verse-final ":" and ";" for ".", ";" '
        'for ","; non-mediant stops set closed up). An eye pass over the 725 '
        'words the alignment could not match found 32 word forms Wave 17 had '
        'missed (carrier slips and 1662 spellings where the book is modern) and '
        '17 spacing slips. %d edits in %d verses of this file: %d punctuation, '
        '%d word forms, %d spacing, %d pointing moved, %d furniture.%s Every '
        'edit is an eye read with its scan page in ingest/w22_evidence.json '
        '(477 records); the eye record is ingest/w22_eye.txt; the corrections '
        'are ingest/w22_witness.py, applied by ingest/w13_build_1892.py after '
        'Wave 17\'s; the gates are ingest/w22_gates.py. NOT taken: letter case '
        '(94 eye-read differences, keyed and switched off pending a ruling) and '
        'the hyphen at 1:3, which the book breaks at a line end.'
        % (per[f], nverses.get(f, 0), k('PUNCT'), k('WORDS'), k('SPACING'),
           k('POINTING_MOVE'), k('FURNITURE'), PER[f]))


def inline_items(f):
    path = WT / 'editions' / '1892' / 'psalter' / (f + '.md')
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
    per, nverses = counts()
    for f in FILES:
        m = re.search(r'^  - edition: 1892\n    service: psalter/%s\n' % f, body, re.M)
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
        blk = (blk[:nm.start()] + '    note: ' + q(was.rstrip() + note_for(f, per, nverses))
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
        print('  1892 psalter/%-16s %d edits in %d verses, verify_items -> %d'
              % (f, per[f], nverses.get(f, 0), len(items)))
    p.write_text(body, encoding='utf-8')


if __name__ == '__main__':
    main()
