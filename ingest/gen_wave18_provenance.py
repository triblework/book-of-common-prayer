#!/usr/bin/env python3
"""Wave 18 — provenance for the 1662 text read against the Annexed Book.

AMENDS ten 1662 records: each note gains the witness pass, and the
verify_items are regenerated FROM THE CELLS themselves, so the index cannot
drift from the inline flags it indexes.

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))

MARK = 'Wave 18:'
WITNESS = ('https://commons.wikimedia.org/wiki/File:The_Book_of_Common_Prayer.pdf')

COMMON = (
    ' Wave 18: READ AGAINST THE ANNEXED BOOK -- the manuscript annexed to the '
    'Act of Uniformity 1662, which is the legal standard of this text, '
    'reproduced in type "verbatim et literatim" by Her Majesty\'s Printing '
    'Office in 1892 after a word-by-word, stop-by-stop comparison with the '
    'photographs of the MS (%s: 577 page images, PD-US, read with Vision OCR; '
    'the readings are in ingest/w18_evidence.json and the corrections in '
    'ingest/w18_witness.py). That witness is NOT one of the printed Sealed '
    'Books, and its own preface records that those "differ considerably from '
    'that original standard in various details of orthography and '
    'punctuation" and that the MS was "not to be a standard of orthography", '
    'so this pass collates substance and structure only: no spelling is '
    'imported from the manuscript into this modernized text.' % WITNESS)

PER = {
    'psalter/psalms-1-50':
        ' The book points Psalm 2:12 -- "from the [right] way : if his wrath be '
        'kindled" (scan page 346) -- where the Church of England text prints no '
        'mediant; the mediant is restored, and with it every one of this '
        'Psalter\'s 2,508 verses now carries exactly one. The whole Psalter was '
        'aligned verse by verse against scan pages 345-507: of the 1,893 verses '
        'whose alignment is sound, the page OCR shows the witness\'s mediant at '
        'the carrier\'s own pivot word in 1,561, and the remainder are OCR '
        'damage rather than absence -- a 30-verse sample of them, re-read line '
        'by line at 4400px, showed the mediant legible and in the same place in '
        '25 of 30. Only two verses in the whole Psalter carried no mediant at '
        'all, and the book points both.',
    'psalter/psalms-51-100':
        ' The book points Psalm 68:1 -- "let his enemies be scattered : let them '
        'also that hate him flee before him" (scan page 413) -- where the '
        'Church of England text prints no mediant; it is restored. Psalm 89:50 '
        'is CONFIRMED as printed: the doxology that closes Book III stands '
        'inside verse 50 after a single mediant, and Psalm 90 follows at once, '
        'with no verse 51 (scan page 443). Wave 13 doubted that reading against '
        'the 1928 book; the 1662 authority settles it for 1662.',
    'psalter/psalms-101-150':
        ' This third of the Psalter needed no correction: the alignment against '
        'scan pages 470-507 found no verse where the carrier\'s pointing '
        'structure differs from the book\'s.',
    'daily-office/morning-prayer':
        ' The Prayer for the King\'s Majesty is attested: the book prays for '
        '"our most gracious soveraign Lord King Charles" (scan page 70), so the '
        'name the source prints is period-correct and that flag is closed. The '
        'Prayer for the Royal Family is a different matter -- the MS leaves the '
        'names BLANK, and breaks the title off at "A Prayer for". The living '
        'names the source prints are carried as printed and the flag now '
        'records the blank.',
    'daily-office/evening-prayer':
        ' Attested as in Morning Prayer: "King Charles" is printed, and the '
        'Prayer for the Royal Family is left blank in the MS, title and all '
        '(scan page 80).',
    'the-litany/litany':
        ' The Litany\'s monarch is attested -- "thy servant Charles our most '
        'gracious King and Governour" (scan page 86) -- and that flag is '
        'closed. The petition for the rest of the Royal Family breaks off after '
        '"That it may please thee to blesse and preserve" and the response '
        'follows a blank (scan page 87).',
    'ordinal/ordering-deacons':
        ' The Ordinal\'s litany prints the same two readings: "thy servant '
        'Charles our most gratious King and Governour" (scan page 526), and a '
        'blank after "That it may please thee to bless and preserve" (scan page '
        '527).',
    'holy-communion/holy-communion':
        ' Two findings. The monarch is attested -- "thy servant Charles our '
        'King" in the prayer for the Church Militant (scan page 254) -- so that '
        'flag is closed. The admission rubric is NOT 1662: where the Church of '
        'England text prints a modern statutory rubric (an account to the '
        'Ordinary, seven days, an opportunity for interview), the Annexed Book '
        'prints the "open and notorious evil liver" rubric of 1549-1604 (scan '
        'page 246). It is retained as the source prints it, and the flag now '
        'says what it is.',
    'occasional-offices/public-baptism':
        ' "Foreasmuch" was checked: the MS reads "Forasmuch as this childe hath '
        'promised" (scan page 277) and "Forasmuch" in the private form (scan '
        'page 283). The spelling stands as the Church of England prints it -- '
        'this witness disclaims its own orthography, so it can settle a word '
        'but not a spelling.',
    'occasional-offices/prayers-at-sea':
        ' Two lines of Church of England WEBSITE CHROME had been published as '
        'text in this file ("...you need to enable JavaScript...", "Popular '
        'search items"); they are removed, and a gate now refuses that furniture '
        'anywhere in the corpus. The psalm-cento flag is closed: the book '
        'labels the one psalm it uses in the margin ("Confitemini Domino. Psal. '
        '107.", scan page 513) and prints no psalm label at all over the '
        'composite hymns (scan page 517), which is exactly what the cell '
        'reflects. A new flag records that the source has left "her Majesty\'s '
        'Navy" unrevised where the book reads "his Majesties Navy" (scan page '
        '508), in the same file that prays for "King CHARLES".',
}

ANCHOR = {
    ('daily-office/morning-prayer', 'Queen Camilla'): 'A Prayer for the Royal Family',
    ('daily-office/evening-prayer', 'Queen Camilla'): 'A Prayer for the Royal Family',
    ('the-litany/litany', 'Queen Camilla'): 'The Litany',
    ('ordinal/ordering-deacons', 'Queen Camilla'): 'The Litany',
    ('holy-communion/holy-communion', 'give an account'): "The Lord's Prayer",
    ('occasional-offices/public-baptism', 'Foreasmuch'): 'The Final Exhortation',
    ('occasional-offices/prayers-at-sea', "her Majesty's Navy"): 'prayers-at-sea',
}

VERIFY_RE = re.compile(r'<!--\s*VERIFY:?\s*(.*?)-->', re.S)


def inline_items(service):
    """(anchor, reading, note) for each VERIFY left in the cell."""
    path = WT / 'editions' / '1662' / (service + '.md')
    out = []
    for m in VERIFY_RE.finditer(path.read_text(encoding='utf-8')):
        body = re.sub(r'\s+', ' ', m.group(1)).strip()
        q = re.search(r"'([^']+)'", body)
        reading = q.group(1) if q else body[:40]
        note = re.sub(r"^'%s';\s*" % re.escape(reading), '', body)
        anchor = next((a for (s, k), a in ANCHOR.items()
                       if s == service and k in reading), service.split('/')[-1])
        out.append((anchor, reading, note))
    return out


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8')
    if MARK in body:
        print('already applied')
        return
    for service, extra in sorted(PER.items()):
        m = re.search(r'^  - edition: 1662\n    service: %s\n' % re.escape(service),
                      body, re.M)
        if not m:
            raise SystemExit('record not found: 1662 %s' % service)
        nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(body) - m.end())
        blk = body[m.start():end]
        # Records were written by different generators, some with
        # double-quoted YAML scalars and some with single-quoted ones; read
        # either, write double-quoted.
        nm = re.search(r'^    note: (["\'])(.*)\1$', blk, re.M)
        if not nm:
            raise SystemExit('note not found (or not one line): 1662 %s' % service)
        was = (nm.group(2).replace('\\"', '"') if nm.group(1) == '"'
               else nm.group(2).replace("''", "'"))
        blk = (blk[:nm.start()] + '    note: '
               + q(was.rstrip() + COMMON + extra)
               + blk[nm.end():])
        items = inline_items(service)
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
        print('  1662 %-38s verify_items -> %d' % (service, len(items)))
    p.write_text(body, encoding='utf-8')


if __name__ == '__main__':
    main()
