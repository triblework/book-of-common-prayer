#!/usr/bin/env python3
"""Wave 23 — provenance for the 1979 text read against the publisher's file.

AMENDS every 1979 record whose cell Wave 23 changed (the note gains the
witness pass with that file's counts), ADDS the record for the new cell
tables/daily-office-lectionary-holy-days, and regenerates every 1979
record's verify_items FROM THE CELLS (keeping an existing item's anchor for
the same reading), so the index cannot drift from the inline flags.

Idempotent: a second run finds its own marker and does nothing.
"""
from __future__ import annotations
import collections
import json
import os
import re
import subprocess
import sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
MARK = 'Wave 23:'
BASE = '710f635b7783f1e8188fa334ec75dca3e43a0220'   # authoring before Wave 23
WITNESS = ('https://commons.wikimedia.org/wiki/'
           'File:Book_of_common_prayer_(TEC,_1979).pdf')
NEW_CELL = 'tables/daily-office-lectionary-holy-days'
VERIFY_RE = re.compile(r'<!--\s*VERIFY:?\s*(.*?)-->', re.S)

COMMON = (
    ' Wave 23: READ AGAINST THE PUBLISHER\'S OWN FILE, the rest of the text '
    '(Church Publishing Incorporated\'s PDF of the 1979 book, %s; Wave 19 did '
    'the Psalter). The file is a COMPOSITE (RULINGS R11 addendum): pp. 19-30 '
    'are a 2008 Calendar and pp. 889-932 the 2007 Revised Common Lectionary, '
    'so tables/calendar and tables/eucharistic-lectionary were not touched and '
    'no reading was taken from those pages; its text layer also confuses 1/I '
    'and ]/1, and no case or pointing is taken from it. Every paragraph of '
    'the cell was located in the book word for word (ingest/w23_survey.py); '
    'each difference was keyed to the paragraph it sits in, re-read in its '
    'page context, and applied file to file (ingest/w23_witness.py, '
    'w23_witness_items.py, w23_apply.py; evidence with the page for every item '
    'in ingest/w23_evidence.json). What the keying had lost is restored from '
    'the page, keyed to the fused fragment it replaces (R22); the e-text\'s '
    'own markup published as text is normalized; the prayers\' hard wrap is '
    're-flowed to the book\'s paragraphs; gates in ingest/w23_gates.py.' % WITNESS)

GROUPS = {'WORDS': 'word readings', 'SPELLING': 'spellings', 'PASSAGES': 'restored passages',
          'HEADINGS': 'heading', 'MEDIANT_STOPS': 'stops before the mediant',
          'RUBRIC_STOPS': 'rubric-final stops', 'PUNCT': 'other stops',
          'DOL_ROWS': 'lectionary rows restored', 'DOL_FIX': 'lectionary cells corrected',
          'DOL_MARKS': 'lectionary marks', 'DOL_XMAS': 'Christmas-week rows',
          'DOL_DISPUTED': 'disputed citations settled for the book', 'FLAGS': 'flags',
          'MARKUP': 'markup normalizations'}


def counts():
    ev = json.load(open(WT / 'ingest' / 'w23_evidence.json', encoding='utf-8'))
    per = collections.defaultdict(collections.Counter)
    for k in ev:
        grp, rest = k.split(':', 1)
        f = rest.split('.md')[0]
        per[f][grp] += 1
    return per


def changed_cells():
    out = subprocess.run(['git', '-C', str(WT), 'diff', '--name-only', BASE, 'HEAD', '--',
                          'editions/1979'], capture_output=True, text=True).stdout.split()
    return [p[len('editions/1979/'):-3] for p in out if p.endswith('.md')]


def per_note(service, per, reflowed):
    c = per.get(service, {})
    bits = ['%d %s' % (n, GROUPS.get(g, g.lower())) for g, n in sorted(c.items()) if g != 'FLAGS']
    s = ''
    if bits:
        s += ' In this file: ' + ', '.join(bits) + '.'
    if reflowed:
        s += ' Its hard-wrapped lines are re-flowed to the book\'s paragraphs (ingest/w23_reflow.py).'
    if not bits and not reflowed:
        s += ' In this file the change is the normalization of the e-text\'s markup only.'
    return s


def sig(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def inline_items(service, existing):
    path = WT / 'editions' / '1979' / (service + '.md')
    out = []
    for m in VERIFY_RE.finditer(path.read_text(encoding='utf-8')):
        body = re.sub(r'\s+', ' ', m.group(1)).strip()
        q_ = re.search(r"'([^']+)'", body)
        reading = q_.group(1) if q_ else body[:40]
        note = re.sub(r"^'%s';?\s*" % re.escape(reading), '', body)
        anchor = existing.get(sig(reading), service.split('/')[-1])
        out.append((anchor, reading, note))
    return out


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


NEW_RECORD = '''  - edition: 1979
    service: tables/daily-office-lectionary-holy-days
    source_url: "http://justus.anglican.org/resources/bcp/bcplectn.txt"
    retrieved: 2026-10-16
    status: transcribed
    depth: table
    verifier: "claude-fable-5.1 (Wave 23: ingest/w23_dol_extra.py -- every carrier row checked field by field against Church Publishing's PDF; w23_gates; w14_audit)"
    note: "The Daily Office Lectionary's Holy Days and Special Occasions tables (book pp. 996-1001), which the 1993 e-text carries after its two-year table and which no earlier wave transcribed -- a silent absence, recorded nowhere, found by the Wave 23 survey. 45 rows: 37 from the carrier e-text, each field checked against Church Publishing's PDF (ingest/w23_dol_extra_evidence.json); 8 from the witness, where the e-text had lost or damaged an entry (the Nativity of St. John the Baptist, the Transfiguration and their Eves among them) -- restoration under R22. Rows in the shape of tables/daily-office-lectionary; an Eve carries evening psalms and lessons only, as the book prints it."
    verify_items: []
'''


def main():
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8')
    if MARK in body:
        print('already applied')
        return
    per = counts()
    changed = set(changed_cells())
    # the new record first, after the daily-office-lectionary record
    m = re.search(r'^  - edition: 1979\n    service: tables/daily-office-lectionary\n', body, re.M)
    nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
    at = m.end() + nxt.start()
    body = body[:at] + NEW_RECORD + body[at:]
    # every 1979 record: amend the note if changed; regenerate verify_items
    pos = 0
    n_amend = n_items = 0
    while True:
        m = re.search(r'^  - edition: 1979\n    service: (\S+)\n', body[pos:], re.M)
        if not m:
            break
        start = pos + m.start()
        service = m.group(1)
        nxt = re.search(r'^  (- edition:|# )', body[pos + m.end():], re.M)
        end = pos + m.end() + (nxt.start() if nxt else len(body) - pos - m.end())
        blk = body[start:end]
        if service in changed and service != NEW_CELL:
            nm = re.search(r'^    note: (["\'])(.*)\1$', blk, re.M)
            if nm:
                was = (nm.group(2).replace('\\"', '"') if nm.group(1) == '"'
                       else nm.group(2).replace("''", "'"))
            else:
                nm = re.search(r'^    note: (?!["\'])(.*)$', blk, re.M)
                if not nm:
                    raise SystemExit('note not found: 1979 %s' % service)
                was = nm.group(1)
            reflowed = service.startswith('prayers-and-thanksgivings/')
            blk = (blk[:nm.start()] + '    note: '
                   + q(was.rstrip() + COMMON + per_note(service, per, reflowed))
                   + blk[nm.end():])
            n_amend += 1
        existing = {}
        for am, an in re.findall(r'- anchor: "?([^"\n]+)"?\n\s+source_reading: "?([^"\n]+)"?', blk):
            existing[sig(an)] = am
        if (WT / 'editions' / '1979' / (service + '.md')).exists():
            items = inline_items(service, existing)
            if items:
                lines = ['    verify_items:\n']
                for anchor, reading, note in items:
                    lines += ['      - anchor: %s\n' % q(anchor),
                              '        source_reading: %s\n' % q(reading),
                              '        note: %s\n' % q(note)]
            else:
                lines = ['    verify_items: []\n']
            blk2 = re.sub(r'^    verify_items:(?: \[\])?\n(?:      .*\n|        .*\n)*',
                          ''.join(lines), blk, flags=re.M)
            if blk2 != blk:
                n_items += 1
            blk = blk2
        body = body[:start] + blk + body[end:]
        pos = start + len(blk)
    p.write_text(body, encoding='utf-8')
    print('1979 records amended: %d; verify_items regenerated in %d; new record: %s'
          % (n_amend, n_items, NEW_CELL))


if __name__ == '__main__':
    main()
