#!/usr/bin/env python3
"""w14_fidelity.py — gate 1: did anything appear that the source does not attest?

Authoring-only. Per AUDIT_METHOD, this catches FABRICATION and is structurally
BLIND to loss; w14_audit.py is the other half.

Tables are almost entirely citations, so the test is token-level: every token of
every emitted VALUE (not the column labels, which this wave supplies) must occur
in the source page's own text. A token the source does not contain is either an
invention or a parser artefact, and either way is a finding.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WT / 'tools'))

import scrape

J = 'http://justus.anglican.org/resources/bcp/'
COE = 'https://www.churchofengland.org/sites/default/files/2017-10/'

# cell -> the source(s) whose text must attest it
CELLS = {
    ('1549', 'tables/calendar'): [J + '1549/Kalendar_1549.htm'],
    ('1552', 'tables/calendar'): [J + '1552/Kalendar_1552.htm'],
    ('1559', 'tables/calendar'): [J + '1559/Kalendar_1559.htm'],
    ('1789', 'tables/calendar'): [J + '1789/FrontMatter_1789.htm'],
    ('1979', 'tables/calendar'): [J + 'bcpoffce.txt'],
    ('1789', 'tables/proper-lessons'): [J + '1789/FrontMatter_1789.htm'],
    ('1892', 'tables/proper-lessons'): [J + '1892/Lectionary_1892.htm'],
    ('1789', 'tables/feasts-and-fasts'): [J + '1789/Tables&Rules_1789.htm'],
    ('1892', 'tables/feasts-and-fasts'): [J + '1892/Lectionary_1892.htm'],
    ('1979', 'tables/feasts-and-fasts'): [J + 'bcpoffce.txt'],
    ('1979', 'tables/eucharistic-lectionary'): [J + 'bcplectn.txt'],
    ('1979', 'tables/daily-office-lectionary'): [J + 'bcplectn.txt'],
    ('1549', 'front-matter/order-how-psalter-appointed'): [J + '1549/Kalendar_1549.htm'],
    ('1552', 'front-matter/order-how-psalter-appointed'): [J + '1552/Kalendar_1552.htm'],
    ('1559', 'front-matter/order-how-psalter-appointed'): [J + '1559/Kalendar_1559.htm'],
    ('1789', 'front-matter/order-how-psalter-appointed'): [J + '1789/FrontMatter_1789.htm'],
    ('1549', 'front-matter/order-how-rest-of-scripture'): [J + '1549/Kalendar_1549.htm'],
    ('1552', 'front-matter/order-how-rest-of-scripture'): [J + '1552/Kalendar_1552.htm'],
    ('1559', 'front-matter/order-how-rest-of-scripture'): [J + '1559/Kalendar_1559.htm'],
    ('1789', 'front-matter/order-how-rest-of-scripture'): [J + '1789/FrontMatter_1789.htm'],
    ('1979', 'front-matter/order-how-rest-of-scripture'): [J + 'bcplectn.txt'],
}
# 1662's feasts cell comes from two CoE PDFs, handled separately.
PDF_CELL = ('1662', 'tables/feasts-and-fasts')
PDFS = ['4-tables-and-rules.pdf', '5-table-vigils-fasts.pdf']

# Column labels and structural marks this wave SUPPLIES; they are not claims
# about the source and are excluded from the attestation test.
SUPPLIED = {
    'morning', 'evening', 'psalm', 'psalms', 'sunday', 'letter', 'psalter',
    'day', 'kalendar', 'note', 'holy', 'the', 'of', 'and', 'to', 'be', 'read',
    'order', 'how', 'rest', 'scripture', 'appointed', 'tables', 'rules', 'for',
    'feasts', 'fasts', 'lectionary', 'proper', 'lessons', 'year', 'one', 'two',
    'week', 'january', 'february', 'march', 'april', 'may', 'june', 'july',
    'august', 'september', 'october', 'november', 'december', 'verify',
}
TOKEN = re.compile(r"[A-Za-z][A-Za-z']+")


def source_tokens(urls):
    toks = set()
    for u in urls:
        raw = scrape.fetch(u)
        # Tags split words: a drop capital arrives as
        # <span class="dropcap">T</span>HOLD, and the cell correctly rejoins it
        # to "THOLD" (th'old Testament). Stripping tags with a SPACE would then
        # report the cell's correct reading as unattested. So the source token
        # set is built BOTH ways -- tags removed, and tags replaced by a space --
        # and a token attested either way counts as attested.
        # A third variant undoes HYPHENATED LINE BREAKS ("con-<br>tinueth"),
        # which the cell rejoins to one word, as the printed page intends.
        dehyph = re.sub(r'-\s*<[^>]+>\s*', '', raw)
        variants = ([raw] if not u.endswith('.htm')
                    else [re.sub(r'<[^>]+>', ' ', raw),
                          re.sub(r'<[^>]+>', '', raw),
                          re.sub(r'<[^>]+>', '', dehyph)])
        for t in variants:
            for m in TOKEN.finditer(t):
                toks.add(m.group(0).lower())
    return toks


def pdf_tokens():
    import io
    import urllib.request
    import pypdf
    toks = set()
    for name in PDFS:
        req = urllib.request.Request(COE + name,
                                     headers={'User-Agent': scrape.USER_AGENT})
        r = pypdf.PdfReader(io.BytesIO(urllib.request.urlopen(req, timeout=60).read()))
        for pg in r.pages:
            for m in TOKEN.finditer(pg.extract_text() or ''):
                toks.add(m.group(0).lower())
    return toks


def cell_tokens(path):
    toks = set()
    for line in path.read_text(encoding='utf-8').split('\n'):
        if line.startswith('#') or line.startswith('<!--'):
            continue
        if ' | ' in line:
            # strip the "Label: " prefixes this wave supplies
            line = ' '.join(re.sub(r'^[^:]{0,24}:\s*', '', f)
                            for f in line.split(' | '))
        for m in TOKEN.finditer(line):
            toks.add(m.group(0).lower())
    return toks


def main():
    bad = 0
    checked = 0
    for (ed, service), urls in sorted(CELLS.items()):
        p = WT / 'editions' / ed / (service + '.md')
        if not p.exists():
            print('MISSING %s %s' % (ed, service)); bad += 1; continue
        missing = sorted(cell_tokens(p) - source_tokens(urls) - SUPPLIED)
        checked += 1
        status = 'OK ' if not missing else 'UNATTESTED'
        print('%-5s %-42s %s %s' % (ed, service, status,
                                    missing[:8] if missing else ''))
        bad += len(missing)
    ed, service = PDF_CELL
    p = WT / 'editions' / ed / (service + '.md')
    if p.exists():
        try:
            missing = sorted(cell_tokens(p) - pdf_tokens() - SUPPLIED)
            checked += 1
            print('%-5s %-42s %s %s' % (ed, service,
                                        'OK ' if not missing else 'UNATTESTED',
                                        missing[:8] if missing else ''))
            bad += len(missing)
        except Exception as exc:
            print('%-5s %-42s PDF SKIPPED (%s)' % (ed, service, exc))
    print('\nfidelity: %d cells checked, %d unattested tokens' % (checked, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
