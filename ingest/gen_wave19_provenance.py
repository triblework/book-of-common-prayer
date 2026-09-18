#!/usr/bin/env python3
"""Wave 19 — provenance for the 1979 text read against the publisher's file.

AMENDS nine 1979 records: each note gains the witness pass, and the
verify_items are regenerated FROM THE CELLS, keeping the anchor an existing
item used for the same reading, so the index cannot drift from the flags it
indexes.

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))

MARK = 'Wave 19:'
WITNESS = ('https://commons.wikimedia.org/wiki/'
           'File:Book_of_common_prayer_(TEC,_1979).pdf')

COMMON = (
    ' Wave 19: READ AGAINST THE PUBLISHER\'S OWN FILE -- Church Publishing '
    'Incorporated\'s PDF of the 1979 book, from the Episcopal Church (%s: '
    '1001 pages with an exact text layer, no OCR; the US Book of Common '
    'Prayer has never been under copyright, which the publisher states). That '
    'is a witness of a different CLASS from justus\'s 1993 ASCII e-text, '
    'which is this file\'s carrier, so where the two disagree the publisher\'s '
    'file is the book. Two things it cannot testify about: the small-capital '
    'LORD, which its text layer renders "Lord", and the pointing asterisk, '
    'which it drops in about ten verses -- no case and no pointing is taken '
    'from it. The corrections are in ingest/w19_witness.py and '
    'ingest/w19_cells.py, each evidenced with its page in '
    'ingest/w19_evidence.json.' % WITNESS)

PER = {
    'psalter/psalms-1-50':
        ' Collated verse by verse: 2,507 verses parsed from the book and '
        'compared word for word. In this file the e-text misread "you Name" '
        'for "your Name" (8:10), "this throne" for "his throne" (9:7), "the '
        'people" for "the peoples" (9:17), "plowed" for "ploughed" (9:6), '
        'dropped "shall" (22:26) and an extra "who" (38:13), and truncated '
        'the Latin incipits of Psalms 34 and 19/37/49 (the ligature). All of '
        'Wave 13\'s truncated-incipit VERIFYs are resolved.',
    'psalter/psalms-51-100':
        ' Collated verse by verse. Corrections here: "to the grave" -> "into '
        'the grave" (55:16), "to Edom" -> "into Edom" (60:9), "from of the '
        'clutches" -> "from the clutches" (71:4), "winge!d" -> "wingèd" '
        '(78:27), "The grieved him ... they provoked" -> "They grieved him '
        '... and provoked" (78:58), "and son of man" -> "the son of man" '
        '(80:16), "Zee%b" -> "Zeëb" (83:11), "All the nations" -> "All '
        'nations" (86:9), "in vision" -> "in a vision" (89:19), "the lion and '
        'the adder" -> "the lion and adder" (91:13), and the incipits of '
        'Psalms 76, 77 and 94.',
    'psalter/psalms-101-150':
        ' Collated verse by verse. Corrections here: "Issac" -> "Isaac" '
        '(105:9), "firstfruits" -> "first fruits" (105:36), "from everlasting '
        'to everlasting" -> "from everlasting and to everlasting" (106:48), '
        '"Hosanna" -> "Hosannah" twice (118:25), "confort" -> "comfort" '
        '(119:52), "the kingdoms of Bashan ... the kings of Canaan" -> "the '
        'king of Bashan ... the kingdoms of Canaan" (135:11), "winge!d" -> '
        '"winged" (148:10), nine incipits, three of Psalm 119\'s portion '
        'headings -- and, at the end of Psalm 150, the 1993 keying\'s own '
        'end-of-file marker ("(end of BCPSALTER.TXT)"), which had been '
        'published as part of the last verse.',
    'front-matter/concerning-the-service':
        ' The e-text\'s "fulfull" is corrected to "fulfill", which is what the '
        'book prints (page 13); the VERIFY that guessed "fulfil" is closed.',
    'daily-office/evening-prayer':
        ' Three keying defects corrected against the book: "Almighty god" -> '
        '"Almighty God" (page 79), "Let my payer be set forth" -> "prayer" '
        '(page 61), and "the Pleides and Orion" -> "the Pleiades" (page 62).',
    'collects-epistles-gospels/easter-4':
        ' The contemporary collect broke off mid-sentence in the e-text ("to '
        'be the way, t Amen."); the rest is restored from the book (page '
        '225). The traditional collect also lost its opening "O", read "god" '
        'for "God", and "leads" for "leadeth" (page 173).',
    'collects-epistles-gospels/annunciation':
        ' Both collects lost the stop before "Amen", and the traditional one '
        'read "to the glory" where the book has "unto the glory" (pages 188 '
        'and 240). The two VERIFYs that reported them as breaking off '
        'mid-sentence are closed.',
    'occasional-offices/matrimony':
        ' Two dropouts repaired. The banns lost the clause "If any of you '
        'know just cause why they may not be joined together in Holy '
        'Matrimony", and printed em dashes where the book prints blanks to be '
        'filled in (page 437). In The Prayers the e-text collapsed "to which '
        'the People respond, saying, Amen." into "saying, Am the ordering of '
        'their common life", swallowing a rubric, the bidding "Let us pray" '
        'and the first prayer; all are restored from page 429.',
    'occasional-offices/churching':
        ' The adoption form lost a sentence, a rubric, a question and two '
        'answers, collapsing "here assembled" into "asbrant"; the passage is '
        'restored from pages 440-441. "wwe" is corrected to "we".',
}

VERIFY_RE = re.compile(r'<!--\s*VERIFY:?\s*(.*?)-->', re.S)


def sig(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def inline_items(service, existing):
    path = WT / 'editions' / '1979' / (service + '.md')
    out = []
    for m in VERIFY_RE.finditer(path.read_text(encoding='utf-8')):
        body = re.sub(r'\s+', ' ', m.group(1)).strip()
        q = re.search(r"'([^']+)'", body)
        reading = q.group(1) if q else body[:40]
        note = re.sub(r"^'%s';?\s*" % re.escape(reading), '', body)
        anchor = existing.get(sig(reading), service.split('/')[-1])
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
        m = re.search(r'^  - edition: 1979\n    service: %s\n'
                      % re.escape(service), body, re.M)
        if not m:
            raise SystemExit('record not found: 1979 %s' % service)
        nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(body) - m.end())
        blk = body[m.start():end]
        # records were written by different generators: double-quoted,
        # single-quoted, or a bare scalar. Read any of the three, write
        # double-quoted.
        nm = re.search(r'^    note: (["\'])(.*)\1$', blk, re.M)
        if nm:
            was = (nm.group(2).replace('\\"', '"') if nm.group(1) == '"'
                   else nm.group(2).replace("''", "'"))
        else:
            nm = re.search(r'^    note: (?!["\'])(.*)$', blk, re.M)
            if not nm:
                raise SystemExit('note not found (or not one line): 1979 %s'
                                 % service)
            was = nm.group(1)
        existing = {sig(x): y for x, y in re.findall(
            r'source_reading: "?([^"\n]+)"?\n\s+note:.*?\n', blk)} if False else {}
        for am, an in re.findall(r'- anchor: "?([^"\n]+)"?\n\s+source_reading: "?([^"\n]+)"?',
                                 blk):
            existing[sig(an)] = am
        blk = (blk[:nm.start()] + '    note: ' + q(was.rstrip() + COMMON + extra)
               + blk[nm.end():])
        items = inline_items(service, existing)
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
        print('  1979 %-40s verify_items -> %d' % (service, len(items)))
    p.write_text(body, encoding='utf-8')


if __name__ == '__main__':
    main()
