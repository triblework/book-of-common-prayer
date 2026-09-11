#!/usr/bin/env python3
"""Wave 15 — provenance records for the 1928 tables and the rubric corrections.

  * REPLACES the five 1928 recorded-gap records (calendar, proper-lessons,
    feasts-and-fasts, proper-psalms, psalter/selections) with transcribed ones;
  * ADDS records for the 1928 and 1892 rubric cells (1892's had none: Wave 14
    put those sections in `absent:`, which Wave 15 corrects);
  * APPENDS a note to the three existing records Wave 15 changes (1789's two
    rubric cells, 1979's calendar).

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))
import w15_witness as W

RETRIEVED = '2026-09-11'
VERIFIER = ('claude-opus-5 (scripted ingest from the text layer; every row '
            'compared with the scan of the original 1928 printing)')
J = 'http://justus.anglican.org/resources/bcp/'
CAL = J + '1928/Calendar&Tables_1928.pdf'
LEC = J + '1928/Lectionary_1928.pdf'
SCAN = J + '1928/BCP1929.pdf'
WITNESS = (' WITNESS: the scan of the original 1928 printing (%s), read as page '
           'images; the text layer was keyed from a LATER printing (its page '
           'numbers are not the original\'s) and is unproofread. Where the two '
           'disagree the scan\'s reading is carried and the correction is '
           'recorded, with its book page, in ingest/w15_witness.py. ' % SCAN)
MARK = '# --- Wave 15: the 1928 tables ---'

SRC = {
 ('tables/calendar', '1928'): (CAL,
   'The Calendar (book pp. xxix-xxx): day, Sunday letter and holy day, and NO '
   'lesson columns -- the 1928 book moves the daily lessons into a table keyed '
   'to the church year (tables/proper-lessons). Rows carry the same three '
   'fields as 1979\'s, so v1928 -> v1979 is a per-day diff. Parsed from text-run '
   'coordinates (a month is an x-range, a day a y-row); golden numbers are '
   'excluded as apparatus. The text layer LOSES six days (15 April/May/June, '
   '11 July/August/September), keys five Sunday letters wrongly and puts All '
   'Saints against 1 October: the seven-day letter cycle found each defect and '
   'the scan supplied each value -- %d corrections, none computed.'
   % len(W.CALENDAR) + WITNESS),
 ('tables/feasts-and-fasts', '1928'): (CAL,
   'Tables and Rules for the Movable and Immovable Feasts (book pp. xxxi-xxxii): '
   'the Rules, the Table of Feasts, the Table of Fasts, Other Days of Fasting, '
   'Days of Solemn Supplication, the Tables of Precedence, and the table of '
   'occasions with a proper Collect not in the Calendar. The Tables for finding '
   'Holy Days (Easter and golden-number grids) are excluded apparatus, as for '
   '1892. %d corrections from the scan, among them the heading '
   '"COLLECT, EPISTLE, GOSPEL" (the transcription reads "EPISTLE, AND '
   'GOSPEL").' % len(W.FEASTS) + WITNESS),
 ('tables/proper-psalms', '1928'): (LEC,
   'Proper Psalms for Seasons and Days (22, with its two NOTEs), A Table of '
   'Psalms for the Sundays of the Church Year (57) and Psalms for Special '
   'Occasions (10), book pp. vii-ix. The Morning/Evening split follows the '
   'book\'s own NOTE ("those for the Morning separated by the semi-colon from '
   'those for the Evening"); rows printed without that shape are carried '
   'whole. %d corrections from the scan, including Good Friday "22:1-9" (the '
   'transcription prints 1-19) and the Sunday table\'s Easter Day evening '
   '"113, 114, 118" (it prints 113, 116, 117).'
   % sum(c['table'] != 'selections' for c in W.PSALMS) + WITNESS),
 ('psalter/selections', '1928'): (LEC,
   'Selections of Psalms I-XX (book p. viii). Closes the recorded gap: justus '
   'links 1928\'s Selections to the 1789 page, so 1928 had inherited 1789\'s ten; '
   'the 1928 book prints twenty of its own. %d corrections from the scan.'
   % sum(c['table'] == 'selections' for c in W.PSALMS) + WITNESS),
 ('tables/proper-lessons', '1928'): (LEC,
   'The ORIGINAL 1928 lectionary (in use 1928-1944), book pp. x-xxviii: A Table '
   'of Lessons for the Christian Year (409 rows: every Sunday and weekday, with '
   'the Ember and Eve-of-Ascension optional lessons stacked as " / " '
   'alternatives, and the Autumnal Ember Days\' optional lessons), A Table of '
   'Lessons for the Fixed Holy Days (19; Eve, Morning, Evening) and A Table of '
   'Lessons for Special Occasions (17). The 1945 revision (Psalms and Lessons '
   'for the Christian Year, used 1945-1978) is deliberately NOT carried. Parsed '
   'from text runs; every row compared with the scan page by page: %d cells '
   'and labels corrected -- OCR misreadings ("Lak e" for Luke, "Heb." for '
   'Hab.), old-style figures confused (3 read as 5 and back, 25 cells), '
   'dropped tails and stacked lessons. The witness records each correction '
   'without guessing whether it is a keying slip or a reading of the later '
   'printing.' % len(W.LESSONS) + WITNESS),
 ('front-matter/order-how-psalter-appointed', '1928'): (LEC,
   'Printed as "THE USE OF THE PSALTER" (book p. vii), in the same place and '
   'doing the same job as the historic rubric; carried under its printed title, '
   'so v1892 -> v1928 shows the rename as a heading change.' + WITNESS),
 ('front-matter/order-how-rest-of-scripture', '1928'): (LEC,
   'Printed under the historic title (book p. x). The original printing '
   'differs from the transcription (a later printing) in two sentences, and '
   'the original is carried: the Gospel lesson "appointed for that day of the '
   'month", and "Upon any day for which no Proper Lessons are provided, the '
   'Lessons appointed in the Calendar..." -- older wording, pointing to a '
   'Calendar that no longer carries lessons, which the later printing '
   'rewrote.' + WITNESS),
 ('front-matter/order-how-psalter-appointed', '1892'):
   (J + '1892/Front_Matter_1892.htm',
    'CORRECTS WAVE 14, which put this section in 1892\'s `absent:` on the '
    'strength of the book\'s TABLE OF CONTENTS ("Concerning the Service of the '
    'Church, with the Order how the Psalter and the rest of the Holy Scripture '
    'is appointed to be read"). The page itself prints it, titled.'),
 ('front-matter/order-how-rest-of-scripture', '1892'):
   (J + '1892/Front_Matter_1892.htm',
    'As the Psalter-order rubric: printed and titled on the page; Wave 14\'s '
    '`absent:` is corrected. The source runs "EveningPrayer" together; the '
    'space is restored (obvious keying noise).'),
}

AMEND = {
 ('front-matter/order-how-psalter-appointed', '1789'):
   ' Wave 15: the slice\'s end marker now takes the whole following heading; '
   'the Wave-14 cell ended with the stray fragment "> Proper", now removed.',
 ('front-matter/order-how-rest-of-scripture', '1789'):
   ' Wave 15: the slice now ends before the pilcrow that opens the next '
   'heading; the Wave-14 cell ended with the stray fragment "¶ <a", now removed.',
 ('tables/calendar', '1979'):
   ' Wave 15: 29 February restored. The e-text prints a bare "29" with no '
   'Sunday letter; the Wave-14 parser read it as a continuation, publishing '
   '"February 28 | ... | Kalendar Note: 29".',
}

REPLACED = [('1928', s) for s in ('tables/calendar', 'tables/proper-lessons',
                                  'tables/feasts-and-fasts',
                                  'tables/proper-psalms', 'psalter/selections')]
VERIFY_RE = re.compile(r"<!--\s*VERIFY:\s*'([^']*)'(.*?)-->", re.S)


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def record_span(body, year, service):
    m = re.search(r'^  - edition: %s\n    service: %s\n' % (year, re.escape(service)),
                  body, re.M)
    if not m:
        return None
    nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
    end = m.end() + (nxt.start() if nxt else len(body) - m.end())
    return m.start(), end


def main():
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8')
    if MARK in body:
        print("already applied")
        return
    for year, service in REPLACED:
        span = record_span(body, year, service)
        if span is None:
            raise SystemExit("gap record not found: %s %s" % (year, service))
        if 'inherited-unreviewed' not in body[span[0]:span[1]]:
            raise SystemExit("not a gap record: %s %s" % (year, service))
        body = body[:span[0]] + body[span[1]:]
    for (service, year), extra in AMEND.items():
        span = record_span(body, year, service)
        if span is None:
            raise SystemExit("record to amend not found: %s %s" % (year, service))
        blk = body[span[0]:span[1]]
        m = re.search(r'^    note: "(.*)"$', blk, re.M)
        blk = blk[:m.start()] + '    note: ' + q(
            m.group(1).replace('\\"', '"') + extra) + blk[m.end():]
        body = body[:span[0]] + blk + body[span[1]:]
    out, nverify = [], 0
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
               '    verifier: %s' % q(VERIFIER if year == '1928'
                                     else 'claude-opus-5 (scripted ingest)'),
               '    note: %s' % q(note)]
        if items:
            rec.append('    verify_items:')
            for reading, text in items:
                rec += ['      - anchor: %s' % q(service.split('/')[-1]),
                        '        source_reading: %s' % q(reading),
                        '        note: %s' % q(text)]
                nverify += 1
        else:
            rec.append('    verify_items: []')
        out.append('\n'.join(rec))
    body = body.rstrip('\n') + '\n\n  ' + MARK + '\n' + '\n'.join(out) + \
        '\n  # --- end Wave 15 ---\n'
    p.write_text(body, encoding='utf-8')
    print("replaced %d gap records, amended %d, added %d records, %d verify_items"
          % (len(REPLACED), len(AMEND), len(out), nverify))


if __name__ == '__main__':
    main()
