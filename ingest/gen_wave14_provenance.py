#!/usr/bin/env python3
"""Wave 14 — provenance records + verify_items + SOURCES.md rows.

Emits a record per <service, edition> for every cell this wave AUTHORS, and a
record per RECORDED GAP: an edition whose book carries the table but for which
no allow-listed source gives us its own text, so it inherits its parent's. Those
carry `status: inherited-unreviewed` and a note saying so in terms a reader
cannot mistake for "this edition reprinted its parent unchanged" (GUIDE
ruling D).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
RETRIEVED = '2026-09-02'
VERIFIER = 'claude-opus-5 (scripted ingest + column-count gates)'

J = 'http://justus.anglican.org/resources/bcp/'
COE = 'https://www.churchofengland.org/sites/default/files/2017-10/'

# (service, edition) -> (source_url, note)
SRC = {
 ('tables/calendar', '1549'): (J + '1549/Kalendar_1549.htm',
   'The Kalendar with its daily lesson columns. The day of the month is the row '
   'POSITION, not the numeric column: that column is the thirty-day Psalter '
   'course, which restarts inside the month. The annotation column is labelled '
   '"Kalendar Note" rather than "Holy Day" because the older books print '
   'astronomical and law-term notes there alongside saints\' days. Golden-number '
   'and Kalends columns are excluded as computational apparatus.'),
 ('tables/calendar', '1552'): (J + '1552/Kalendar_1552.htm',
   'As 1549. Month tables cannot be located by heading here: this page labels its '
   'months in Latin ("Octobris"), so they are found by row shape and gated on '
   'day counts.'),
 ('tables/calendar', '1559'): (J + '1559/Kalendar_1559.htm', 'As 1552.'),
 ('tables/calendar', '1789'): (J + '1789/FrontMatter_1789.htm',
   'The American Kalendar. November\'s two First-Lesson columns carry one entry '
   'fewer than the month has days; they are omitted for that month rather than '
   'aligned on a guess, which would misdate every following day. The holy-day '
   'column wraps long names across line breaks and is rejoined by a rule that '
   'refuses to merge genuinely adjacent feasts (St. Stephen, St. John and the '
   'Innocents on 26-28 December).'),
 ('tables/calendar', '1979'): (J + 'bcpoffce.txt',
   '1979 did NOT abolish the civil-date Kalendar: "The Calendar of the Church '
   'Year" prints a full twelve-month day-by-day table. What 1979 drops is the '
   'four lesson columns, which move into the two-year Daily Office Lectionary. '
   'The golden number printed in the left margin is excluded as apparatus.'),
 ('tables/proper-lessons', '1789'): (J + '1789/FrontMatter_1789.htm',
   'Tables of Lessons for Sundays and for Holy-Days. Each column is emitted as a '
   'single cell; the occasion column carries its section heading as leading '
   'fragments, and the count difference against the lesson columns gives exactly '
   'how many.'),
 ('tables/proper-lessons', '1892'): (J + '1892/Lectionary_1892.htm',
   'Its own page, not shared with 1789. 1892 adds three tables 1789 lacks: the '
   'Forty Days of Lent, the Rogation Days and the Ember Days.'),
 ('tables/feasts-and-fasts', '1662'): (COE + '4-tables-and-rules.pdf',
   'Tables and Rules for the moveable and immoveable feasts, with the Table of '
   'the Vigils, Fasts and Days of Abstinence (5-table-vigils-fasts.pdf). These '
   'two Church of England PDFs print the 1662 text; the same site\'s Kalendar and '
   'Proper Lessons do NOT, which is why those are a recorded gap at 1662. The '
   'golden-number and Easter grids that accompany them are excluded as '
   'computational apparatus.'),
 ('tables/feasts-and-fasts', '1789'): (J + '1789/Tables&Rules_1789.htm',
   'Rules to know when the Moveable Feasts begin, the Table of Feasts and the '
   'Table of Fasts. The slice stops before the Tables for finding the Holy-Days, '
   'which are apparatus.'),
 ('tables/feasts-and-fasts', '1892'): (J + '1892/Lectionary_1892.htm',
   'As 1789, from 1892\'s own page. The printed heading carries an OCR slip '
   '("for tbe Movable Feasts").'),
 ('tables/feasts-and-fasts', '1979'): (J + 'bcpoffce.txt',
   'The lineal successor: "The Calendar of the Church Year" rebuilds this '
   'material around a precedence scheme -- Principal Feasts, Sundays, Holy Days, '
   'Days of Special Devotion, Days of Optional Observance.'),
 ('tables/eucharistic-lectionary', '1979'): (J + 'bcplectn.txt',
   'The three-year (A/B/C) eucharistic lectionary, which Wave 10 deferred because '
   'three reading sets per day cannot fit the single-citation slot the historic '
   'propers use. Source is the eleventh part of the public-domain e-text, which '
   'no prior wave had fetched. Its pages 889, 899 and 909 are LOST WITH THEIR '
   'CONTENT, taking Year A\'s first two Sundays of Advent and two bands of '
   'Propers; the gaps are flagged inline and nothing is reconstructed.'),
 ('tables/daily-office-lectionary', '1979'): (J + 'bcplectn.txt',
   'The two-year Daily Office Lectionary, 784 day entries across 108 weeks. It '
   'takes its own path rather than sharing tables/calendar.md: it is keyed by '
   'liturgical week, not civil date, so the two are structurally '
   'incommensurable (Wave-10 Decision C).'),
 ('front-matter/order-how-psalter-appointed', '1549'):
   (J + '1549/Kalendar_1549.htm', 'The rubric governing the monthly Psalter course.'),
 ('front-matter/order-how-psalter-appointed', '1552'):
   (J + '1552/Kalendar_1552.htm',
    'On this page the <a name> anchors mark the psalm TABLE, not the rubric; the '
    'prose precedes them.'),
 ('front-matter/order-how-psalter-appointed', '1559'):
   (J + '1559/Kalendar_1559.htm', 'As 1552.'),
 ('front-matter/order-how-psalter-appointed', '1789'):
   (J + '1789/FrontMatter_1789.htm',
    'The slice stops at the "Proper Psalms on Certain Days" table the 1789 book '
    'prints within this section; that table is not transcribed (recorded gap).'),
 ('front-matter/order-how-rest-of-scripture', '1549'):
   (J + '1549/Kalendar_1549.htm', 'The rubric governing the daily lessons.'),
 ('front-matter/order-how-rest-of-scripture', '1552'):
   (J + '1552/Kalendar_1552.htm', 'As 1549.'),
 ('front-matter/order-how-rest-of-scripture', '1559'):
   (J + '1559/Kalendar_1559.htm', 'As 1552.'),
 ('front-matter/order-how-rest-of-scripture', '1789'):
   (J + '1789/FrontMatter_1789.htm', 'As 1559, in the American recension.'),
 ('front-matter/order-how-rest-of-scripture', '1979'): (J + 'bcplectn.txt',
   '1979 prints this rubric as "Concerning the Daily Office Lectionary", in the '
   'same position in the book and doing the same job. Four of the historic '
   'rubric\'s seven provisions have an analogue: the Old-Testament-first rule, '
   'where to find the day\'s readings, what happens when a feast interrupts the '
   'course, and a discretion clause. Mapped on lineage, per Wave-10 Decision C. '
   'The Psalter-order rubric has NO 1979 successor and is absent.'),
}

# Recorded gaps: the book HAS the table, no allow-listed source gives us its
# own text, so it inherits. Never to be read as "reprinted unchanged".
GAPS = {
 ('tables/calendar', '1604'):
   'No allow-listed 1604 source exists (the same gap Wave 10 recorded for the '
   '1604 propers), so 1604 inherits 1559.',
 ('tables/calendar', '1662'):
   'The Church of England serves only the POST-1922 recension of the Kalendar '
   '(verse-level citations, "or" alternatives, and three PDFs that are '
   'explicitly the Revised Tables of Lessons Measure 1922). No allow-listed '
   'source gives 1662\'s own Kalendar, so 1662 inherits 1559. THE 1662 BOOK DID '
   'PRINT ITS OWN KALENDAR: this is a transcription gap, not a claim that 1662 '
   'reprinted 1559.',
 ('tables/calendar', '1637'):
   'The Scottish line is transcribed for the Communion; the 1637 Kalendar is not '
   'transcribed and 1637 inherits 1604. The 1637 book does print a Kalendar.',
 ('tables/calendar', '1892'):
   'The justus HTML for the 1892 Kalendar has LOST the table\'s row structure: '
   'several days are packed into one line-break slot ("5 6 7"), the packing '
   'differs column by column, and continuation lines interleave. No structural '
   'discriminator recovers per-day rows, and a wrong reconstruction would '
   'silently misdate a year of lessons. 1892 inherits 1789.',
 ('tables/calendar', '1928'):
   '1928\'s Kalendar is PDF-only and, unlike its predecessors, prints no lesson '
   'columns (1928 moved the lessons into a separate table). Not transcribed this '
   'wave; 1928 inherits 1892.',
 ('tables/proper-lessons', '1928'):
   '1928 revised its lectionary twice -- the original (in use 1928-1944) and the '
   '1945 revision. Only PDF sources exist and one edition node cannot carry both, '
   'so 1928 inherits 1892 and the fork is recorded in NOTICE.md.',
 ('tables/feasts-and-fasts', '1928'):
   'PDF-only; not transcribed this wave. 1928 inherits 1892.',
 ('front-matter/order-how-psalter-appointed', '1604'):
   'No allow-listed 1604 source; inherits 1559.',
 ('front-matter/order-how-psalter-appointed', '1662'):
   'The Church of England text of this rubric is the post-1922 recension (it '
   'refers to alternative Second Lessons appointed in the Table). 1662 inherits '
   '1559; the 1662 book did print its own.',
 ('front-matter/order-how-psalter-appointed', '1637'):
   'Not transcribed for the Scottish line; 1637 inherits 1604. The 1637 page does '
   'carry this rubric.',
 ('front-matter/order-how-rest-of-scripture', '1604'):
   'No allow-listed 1604 source; inherits 1559.',
 ('front-matter/order-how-rest-of-scripture', '1662'):
   'Post-1922 recension on the CoE site; 1662 inherits 1559.',
 ('front-matter/order-how-rest-of-scripture', '1637'):
   'Not transcribed for the Scottish line; 1637 inherits 1604.',
}

VERIFY_RE = re.compile(r"<!--\s*VERIFY:\s*'([^']*)'(.*?)-->", re.S)


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    out, rows = [], []
    for (service, year), (url, note) in sorted(SRC.items(),
                                               key=lambda x: (x[0][1], x[0][0])):
        f = WT / 'editions' / year / (service + '.md')
        if not f.exists():
            raise SystemExit("missing cell %s" % f)
        items = [(m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip())
                 for m in VERIFY_RE.finditer(f.read_text(encoding='utf-8'))]
        rec = ['  - edition: %s' % year, '    service: %s' % service,
               '    source_url: %s' % q(url), '    retrieved: %s' % RETRIEVED,
               '    status: transcribed', '    depth: table',
               '    verifier: %s' % q(VERIFIER), '    note: %s' % q(note)]
        if items:
            rec.append('    verify_items:')
            for reading, text in items:
                rec += ['      - anchor: %s' % q(service.split('/')[-1]),
                        '        source_reading: %s' % q(reading),
                        '        note: %s' % q(text)]
                rows.append((service, year, reading, text))
        out.append('\n'.join(rec))
    for (service, year), note in sorted(GAPS.items(),
                                        key=lambda x: (x[0][1], x[0][0])):
        out.append('\n'.join([
            '  - edition: %s' % year, '    service: %s' % service,
            '    source_url: %s' % q('(no allow-listed source for this edition)'),
            '    retrieved: %s' % RETRIEVED,
            '    status: inherited-unreviewed', '    depth: table',
            '    verifier: %s' % q(VERIFIER),
            '    note: %s' % q('RECORDED GAP. ' + note),
            '    verify_items: []']))
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8').rstrip('\n')
    body += ('\n\n  # --- Wave 14: lectionary and calendar tables ---\n'
             + '\n'.join(out) + '\n  # --- end Wave 14 ---\n')
    p.write_text(body, encoding='utf-8')
    print("appended %d records (%d authored, %d recorded gaps), %d verify_items"
          % (len(out), len(SRC), len(GAPS), len(rows)))
    return rows


if __name__ == '__main__':
    main()
