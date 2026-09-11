#!/usr/bin/env python3
"""Wave 16 (the backlog pass) — provenance records.

  * REPLACES the 1892 psalter/selections recorded-gap record with a transcribed
    one;
  * ADDS records for the 1892 and 1928 front-matter/concerning-the-service
    cells;
  * AMENDS three records: 1928 and 1892 tables/proper-psalms (notes; their
    VERIFYs are resolved, so verify_items empty) and 1892
    tables/feasts-and-fasts (note).

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))
import w16_witness as W

RETRIEVED = '2026-09-11'
J = 'http://justus.anglican.org/resources/bcp/'
FM = J + '1892/Front_Matter_1892.htm'
STD = J + '1892Standard/front_matter.pdf'
LEC = J + '1928/Lectionary_1928.pdf'
SCAN = J + '1928/BCP1929.pdf'
S1936 = J + '1928/BCP1936.pdf'
MARK = '# --- Wave 16: the backlog pass ---'
VERIFIER = 'claude-opus-5 (scripted ingest; every value checked against a named witness)'

SLOT = ('SLOT: this file holds what each book prints under the title "Concerning '
        'the Service of the Church" -- on the English line the 1549 Preface, '
        'renamed in 1662; on the American line a rules text that 1892 '
        'introduced, 1928 rewrote and 1979 replaced. 1979 was put here in '
        'Wave 9 on that basis; 1892 and 1928 follow it. 1789 prints nothing '
        'under the title and stays absent, so v1789 deletes the file and v1892 '
        're-creates it. ')

SRC = {
 ('front-matter/concerning-the-service', '1892'): (FM,
   SLOT + 'The four paragraphs under the heading, stopping before "The Order '
   'how the Psalter is appointed to be read" (its own cell). WITNESS: the '
   '1892 Standard Book as keyed by justus (%s), which agrees word for word but '
   'for two places: "think lit" (carrier; l keyed for f), where the Standard '
   'Book\'s "fit" is carried; and "the President" / "The President", which no '
   'witness settles (VERIFY). Corrections in ingest/w16_witness.py.' % STD),
 ('front-matter/concerning-the-service', '1928'): (LEC,
   SLOT + 'Printed on book p. vii, before "The Use of the Psalter" (its own '
   'cell): a rewrite of 1892\'s rules -- it names the Holy Communion first '
   'among "the regular Services", drops 1892\'s rule on using the Litany in '
   'place of the Prayers, lets the Minister use other devotions (and, in '
   'Mission Churches or where authorized, in place of Morning or Evening '
   'Prayer), and adds a NOTE on words denoting vocal utterance. Carrier: the text layer (keyed from a later '
   'printing); WITNESS: the scan of the original printing (%s, scan p. 4), '
   'which corrects %d keyed periods to commas. Corrections in '
   'ingest/w16_witness.py.' % (SCAN, len(W.CONCERNING_1928))),
 ('psalter/selections', '1892'): (FM,
   'CLOSES A RECORDED GAP. justus\'s 1892 index links the Selections to the '
   '1789 page, so Wave 13 recorded a gap and let 1892 inherit 1789\'s ten; '
   'but the 1892 front-matter page itself prints the book\'s own "TABLE OF '
   'SELECTIONS OF PSALMS" -- twenty selections, untitled (1928 later gave '
   'each a title). Rows First to Twentieth in numerical order (the book sets '
   'them in two columns, First-Tenth and Eleventh-Twentieth). Checked value '
   'for value against the 1892 Standard Book as keyed by justus (%s): all '
   'twenty agree. Typographic normalization only: "v.7" spaced "v. 7".' % STD),
}

AMEND = {
 ('tables/proper-psalms', '1928'): (
   [('12 corrections from the scan', '11 corrections from the scan')],
   ' Wave 16: Palm Sunday\'s "Also: 24, 130, 131" restored -- the text '
   'layer\'s reading. Wave 15 read the scan\'s damaged last figure as 2 and '
   'carried "132" under a VERIFY; at pixel level the figure has a serifed '
   'top with a centred stem (this face\'s old-style 1, unlike the hooked 2 '
   'of "24" on the same line), and the 1936 printing (%s, scan p. 6, a new '
   'setting in lining figures) prints 131 cleanly. The VERIFY is resolved.'
   % S1936),
 ('tables/proper-psalms', '1892'): (
   [],
   ' Wave 16: %d corrections from the 1892 Standard Book as keyed by justus '
   '(%s, p. 8), at each of which justus\'s separately keyed front-matter copy '
   'of the table (%s) reads the same. They resolve both Wave-13 VERIFYs -- '
   'Ash Wednesday evening "102, 180, 148" is 102, 130, 143 and Ascension '
   'evening "24, 47, 190" is 24, 47, 108 -- and correct a number those '
   'VERIFYs could not see (Transfiguration evening 132 -> 133), plus five day '
   'names whose line-break hyphens the carrier keyed inline (Christ-Mas-day, '
   'Whit-sunday, Transfig-uration) or whose hyphen it dropped (Easter Day, '
   'Trinity Sunday). The carrier is an OCR-grade page; its 180 for 130 shows '
   'the error pattern. Corrections in ingest/w16_witness.py.'
   % (len(W.PROPER_1892), STD, FM)),
 ('tables/feasts-and-fasts', '1892'): (
   [],
   ' Wave 16: REBUILT in the 1928 cell\'s line shape (ingest/w16_build.py) '
   'from the same page, words unchanged. Wave 14 emitted it one HTML fragment '
   'per line, so a wrapped entry ("The Circumcision of our Lord" / "JESUS '
   'CHRIST.") and each column of the two brace tables read as separate lines '
   'and v1892 -> v1928 was mostly re-lining. The brace tables are read across '
   '("Septuagesima Sunday is Nine Weeks before Easter."), repeating the words '
   'the brace prints once for four rows, as 1928 sets these rules. One '
   'keying-noise space restored ("above,the"). The OCR slips "tbe", '
   '"EASTER.DAY" and "Authorlty" stay: no 1892 witness prints this section.'),
}

REPLACED = [('1892', 'psalter/selections')]
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
        if span is None or 'inherited-unreviewed' not in body[span[0]:span[1]]:
            raise SystemExit("gap record not found: %s %s" % (year, service))
        body = body[:span[0]] + body[span[1]:]
    for (service, year), (subs, extra) in AMEND.items():
        span = record_span(body, year, service)
        if span is None:
            raise SystemExit("record to amend not found: %s %s" % (year, service))
        blk = body[span[0]:span[1]]
        m = re.search(r'^    note: "(.*)"$', blk, re.M)
        note = m.group(1).replace('\\"', '"')
        for a, b in subs:
            if note.count(a) != 1:
                raise SystemExit("amend %s %s: %r found %d times"
                                 % (year, service, a, note.count(a)))
            note = note.replace(a, b)
        blk = blk[:m.start()] + '    note: ' + q(note.rstrip() + extra) + blk[m.end():]
        # this wave's cells carry no inline VERIFY for these records any more
        f = WT / 'editions' / year / (service + '.md')
        if VERIFY_RE.search(f.read_text(encoding='utf-8')):
            raise SystemExit("%s still carries a VERIFY" % f)
        blk = re.sub(r'^    verify_items:\n(?:      .*\n|        .*\n)*',
                     '    verify_items: []\n', blk, flags=re.M)
        if 'verify_items' not in blk:
            tail = blk[len(blk.rstrip('\n')):]
            blk = blk.rstrip('\n') + '\n    verify_items: []' + tail
        body = body[:span[0]] + blk + body[span[1]:]
    out, nverify = [], 0
    for (service, year), (url, note) in sorted(SRC.items(),
                                               key=lambda x: (x[0][1], x[0][0])):
        f = WT / 'editions' / year / (service + '.md')
        items = [(m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip())
                 for m in VERIFY_RE.finditer(f.read_text(encoding='utf-8'))]
        rec = ['  - edition: %s' % year, '    service: %s' % service,
               '    source_url: %s' % q(url), '    retrieved: %s' % RETRIEVED,
               '    status: transcribed',
               '    depth: %s' % ('table' if service.startswith('psalter/')
                                  else 'tier-1'),
               '    verifier: %s' % q(VERIFIER), '    note: %s' % q(note)]
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
        '\n  # --- end Wave 16 ---\n'
    p.write_text(body, encoding='utf-8')
    print("replaced %d gap record, amended %d, added %d records, %d verify_items"
          % (len(REPLACED), len(AMEND), len(out), nverify))


if __name__ == '__main__':
    main()
