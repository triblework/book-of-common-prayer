#!/usr/bin/env python3
"""Wave 20 -- provenance for the 1662 Kalendar, Proper Lessons, Proper Psalms
and the two reading rubrics, transcribed from the Annexed Book.

REPLACES the three 1662 records that stood as recorded gaps since Wave 14
(tables/calendar and both rubrics, status inherited-unreviewed) and ADDS
records for tables/proper-lessons and tables/proper-psalms, which v1662 did
not carry at all. verify_items are generated FROM THE CELLS, so the index
cannot drift from the inline flags it indexes.

Idempotent: a second run finds its marker and does nothing.
"""
from __future__ import annotations
import re
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
MARK = 'Wave 20: TRANSCRIBED FROM THE ANNEXED BOOK'
PDF = 'https://commons.wikimedia.org/wiki/File:The_Book_of_Common_Prayer.pdf'
VERIFY_RE = re.compile(r'<!--\s*VERIFY\b:?(.*?)-->', re.S)
VERIFIER = 'claude-opus-5.5 (Wave 20: two machine reads + eye read of every cell off 4400px crops)'

COMMON = (
    MARK + ' -- the manuscript annexed to the Act of Uniformity 1662, in Her '
    'Majesty\'s Printing Office\'s 1892 type-reproduction (%s, PD-US). It is '
    'the ONLY allow-listed source for this section, so every word is taken '
    'from it, in the manuscript\'s own spelling (RULINGS R12): its preface '
    'disclaims the MS as a standard of orthography, so these spellings are the '
    'manuscript\'s, not those of the printed Sealed Books of 1662. Superscript '
    'letters are set inline (Ld, ye), a sign standing for missing letters is '
    'set (Gregorius as Gregori + U+A770; Annunciation\'s n-tilde; Immoveable\'s '
    'm-macron), a mark that only flags an abbreviation is not (R16). '
    'Pages were rendered with pypdf + Quick Look, deskewed, and read with '
    'macOS Vision (language correction off); see ingest/WAVE20_GUIDE.md.' % PDF)

KAL = (
    ' The Kalendar, PDF pp. 44-55, one month a page. Rows are recovered from '
    'PIXEL POSITION (the Roman-date column prints one entry per day and gives '
    'each row its y), never from text order. Every kept cell was read three '
    'ways: OCR of the cell cut out of the local render (A), OCR of the same '
    'cell in Wikimedia\'s own render of the file (B), and an eye read of 4400px '
    'crops, which is what is printed here (ingest/w20_kal_eye.txt; the audit '
    'is ingest/w20_kal_check.json). Structural checks, all clean: every month '
    'has its printed rows (February prints a 29th); the Sunday letters run '
    'A-G unbroken through all 365 days; every row with four blank lesson cells '
    'is a holy day; the second lessons run on chapter by chapter with no gap; '
    'the Old Testament course has 23 skips, each re-read at pixel level and '
    'each the book\'s own omission. Where A and B agreed against the eye read '
    '(39 cells), every one was re-read; the eye read stood in all 39 (Vision '
    'drops an i or reads xv as "AX"). JUNE (p. 49): the local JBIG2 decoder '
    'draws the page blank ("Too many symbols in JBIG2 symbol dictionary"), so '
    'June is read from Wikimedia\'s server-side render of the same file '
    '(page49-1920px thumbnail, fetched by ingest/w20_fetch.py) -- the same '
    'witness through another decoder, never counted as corroboration (R14). '
    'SCHEMA (R13): chapter numerals are converted to arabic with the printed '
    'extent kept (Luke 1. to 39); the cell-final stop is dropped; the Golden '
    'Number, the Roman date and the lunar line are excluded as computational '
    'apparatus, as they were at 1549-1559; 1662 prints no Psalter-day column, '
    'so the rows carry none. The two month footnotes are Footnote rows. SIC, '
    'read clearly and kept: the 29th of February prints Matt. 7 and Rom. 12, '
    'which break both second-lesson sequences; 21 December prints "S Thomos"; '
    '30 September reads Tob. 4 / Tob. 6. Typeface (bold holy days, italic '
    'commemorations) is not encoded (R16).')

PL = (
    ' The Proper Lessons, PDF pp. 36-38: ONE table in two sections (Sundays; '
    'Holy-days), each row an occasion with Mattens and Evensong readings -- '
    'not the ~30 per-occasion tables SOURCES.md recorded for 1549-1662, so '
    'the 1789 row model fits and is used (R15). A Sunday row carries the first '
    'lessons it prints; an occasion\'s "1. Lesson" / "2. Lesson" sub-rows are '
    'folded into its one row. The occasion column is set as printed, ordinals '
    'and all (ii, xiv), since those are labels, not chapters (R13). Every '
    'occasion was read by eye off 4400px crops (ingest/w20_pl_eye.txt). '
    'Machine check (ingest/w20_pl_check.json): each column was OCR\'d as a '
    'strip on both renders and every eye token looked for in its own column '
    'within a 15%% window of its place; 457 of 693 tokens were found, and the '
    'rest are dominated by the italic "vr" and "to" that Vision garbles; the '
    'test\'s sensitivity was proved by injecting readings the table prints '
    'nowhere (all three caught). The Sunday first lessons run on in book order '
    'with no backward step in 56 rows. The mark the type sets over "Ecclus" '
    '(a tilde on p. 26, a cross-like flourish on p. 27, a struck l in the '
    'Kalendar) is taken as the abbreviation flag it sits in place of, and not '
    'carried (R16); "S. Simon" has four minims before "on", the dot of the i '
    'lost.')

PS = (
    ' Proper Psalms on certein Daies, PDF p. 38, printed below the Holy-day '
    'lessons. v1662 carried no Proper Psalms file before this wave, and no gap '
    'was recorded for it -- a silent absence, now closed (R15). Six occasions; '
    'the stacked psalm numbers are joined with ", " and the pilcrows and the '
    '"Psalm." column head are not carried, as in 1789\'s rows (R16). '
    'Ascension evening reads cviii (108).')

RUB = (
    ' %s, PDF p. %d, read twice by machine (A and B) and by eye; every word is '
    'attested by at least one machine read except where both dropped a line, '
    'which the eye read settles (%s). Line-end hyphens are rejoined and the '
    '1892 compositor\'s space before ; and : is closed up, except the Gloria\'s '
    'pointing colon (R16). The build\'s sentence splitter breaks a line after '
    'a numeral\'s stop (%s), exactly as it does in the published 1549 rubric.')

RECORDS = {
    'front-matter/order-how-psalter-appointed':
        COMMON + RUB % ('The Order how the Psalter is appointed to be read', 34,
                        'none dropped', '"K." / "H." / "viii."'),
    'front-matter/order-how-rest-of-scripture':
        COMMON + RUB % ('The Order how the rest of Holy Scripture is appointed '
                        'to be read', 35, 'the last line, "time."',
                        'none in this rubric') +
        ' The accent over the n of "Lessons" is not carried (R16).',
    'tables/calendar': COMMON + KAL,
    'tables/proper-lessons': COMMON + PL,
    'tables/proper-psalms': COMMON + PS,
}


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def items(service):
    path = WT / 'editions' / '1662' / (service + '.md')
    out = []
    for m in VERIFY_RE.finditer(path.read_text(encoding='utf-8')):
        body = re.sub(r'\s+', ' ', m.group(1)).strip()
        r = re.search(r"'([^']+)'", body)
        reading = r.group(1) if r else body[:40]
        note = re.sub(r"^'%s';\s*" % re.escape(reading), '', body)
        out.append((service.split('/')[-1], reading, note))
    return out


def block(service):
    L = ['  - edition: 1662\n', '    service: %s\n' % service,
         '    source_url: %s\n' % q(PDF), '    retrieved: 2026-09-25\n',
         '    status: transcribed\n', '    depth: table\n',
         '    verifier: %s\n' % q(VERIFIER), '    note: %s\n' % q(RECORDS[service])]
    it = items(service)
    if it:
        L.append('    verify_items:\n')
        for a, r, n in it:
            L += ['      - anchor: %s\n' % q(a), '        source_reading: %s\n' % q(r),
                  '        note: %s\n' % q(n)]
    else:
        L.append('    verify_items: []\n')
    return ''.join(L), len(it)


def main():
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8')
    if MARK in body:
        print('already applied')
        return
    for service in ('front-matter/order-how-psalter-appointed',
                    'front-matter/order-how-rest-of-scripture', 'tables/calendar'):
        m = re.search(r'^  - edition: 1662\n    service: %s\n' % re.escape(service), body, re.M)
        if not m:
            raise SystemExit('record not found: 1662 ' + service)
        nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
        end = m.end() + nxt.start()
        assert 'inherited-unreviewed' in body[m.start():end], service
        new, n = block(service)
        if service == 'tables/calendar':
            for extra in ('tables/proper-lessons', 'tables/proper-psalms'):
                b, k = block(extra)
                new += b
                print('  1662 %-42s ADDED     verify_items %d' % (extra, k))
        body = body[:m.start()] + new + body[end:]
        print('  1662 %-42s REPLACED  verify_items %d' % (service, n))
    p.write_text(body, encoding='utf-8')


if __name__ == '__main__':
    main()
