#!/usr/bin/env python3
"""Wave 12 — provenance records + verify_items + SOURCES.md rows."""
from __future__ import annotations
import re, sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
FAM = 'occasional-offices'
RETRIEVED = '2026-09-01'
VERIFIER = 'claude-opus-5 (scripted ingest + two gates)'

SRC = {
 ('prayers-at-sea', '1662'): ('https://www.churchofengland.org/prayer-and-worship/'
   'worship-texts-and-resources/book-common-prayer/prayers-be-used-sea',
   'A 1662 addition: the 1549/1552/1559 indexes carry no Sea forms at all (zero matching '
   'links, zero mentions). 1604 was not directly confirmed — its justus index 404s — so 1604 '
   'inherits 1559, which carries none. Psalm bodies are NOT transcribed here: per the locked '
   'ruling they collapse to a pointer carrying the printed psalm label, the Psalter being its '
   'own wave.'),
 ('prayers-at-sea', '1789'): ('http://justus.anglican.org/resources/bcp/1789/Prayer_at_Sea_1789.htm',
   'American Sea forms. This page prints 1789 and 1892 SIDE BY SIDE in labelled parallel '
   'columns; this cell takes only the 1789 side. Psalms collapse to a pointer per the ruling.'),
 ('prayers-at-sea', '1892'): ('http://justus.anglican.org/resources/bcp/1789/Prayer_at_Sea_1789.htm',
   'Taken from the 1892 side of the same page\'s parallel columns — the two texts genuinely '
   'differ, so 1892 is not simply the 1789 page reprinted.'),
 ('penitential-office', '1892'): ('http://justus.anglican.org/resources/bcp/1892/Pray&Thanks_1892.htm',
   'Printed at the end of the Prayers and Thanksgivings page. Given its OWN slug, NOT mapped '
   'onto occasional-offices/commination: it keeps the first day of Lent and Psalm 51 but '
   'carries none of the Commination\'s eight denounced curses and drops the name (whole-text '
   'overlap 0.33). The occasion relationship is recorded in NOTICE.md. Psalm 51 is carried in '
   'full, following the published commination.md precedent for the same psalm on the same day.'),
 ('penitential-office', '1928'): ('http://justus.anglican.org/resources/bcp/1928/Litany.htm',
   '1928 MOVES this office onto the Litany page, where 1892 prints it with Prayers and '
   'Thanksgivings — a placement change recorded in NOTICE.md. The 1928 text is substantially '
   'longer than 1892\'s.'),
 ('family-prayer', '1789'): ('http://justus.anglican.org/resources/bcp/1789/Family_Prayer_1789.htm',
   'Morning and Evening forms for household use. 1892 reprints this unchanged and so authors '
   'no file of its own (inheritance by omission).'),
 ('family-prayer', '1928'): ('http://justus.anglican.org/resources/bcp/1928/Family_Prayer.htm',
   '1928 greatly expands this section (a shorter form plus many additional prayers). SIX of '
   'these prayers are PROMOTED by 1979 into its main Prayers and Thanksgivings section — '
   'verified by text, overlaps 0.92–1.00 (see ingest/WAVE12_SCOPING.md §6). They are kept '
   'here, where the 1928 book prints them; the 1979 cells keep their own slugs and the '
   'promotion is recorded in NOTICE.md.'),
 ('prayer-and-thanksgiving', '1789'): ('http://justus.anglican.org/resources/bcp/1789/Prayer&Thanksgiving_1789.htm',
   'A harvest form with its own Collect, Epistle and Gospel. This page prints 1789 and 1892 '
   'side by side in labelled parallel columns; this cell takes the 1789 side. Readings are '
   'carried as citations, per the Wave-10 depth decision.'),
 ('prayer-and-thanksgiving', '1892'): ('http://justus.anglican.org/resources/bcp/1789/Prayer&Thanksgiving_1789.htm',
   'The 1892 side of the same page\'s parallel columns.'),
}

VERIFY_RE = re.compile(r"<!--\s*VERIFY:\s*'([^']*)'(.*?)-->", re.S)


def q(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    out, rows = [], []
    for (service, year), (url, note) in sorted(SRC.items(), key=lambda x: (x[0][1], x[0][0])):
        f = WT / 'editions' / year / FAM / f'{service}.md'
        if not f.exists():
            raise SystemExit(f"missing cell {f}")
        items = [(m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip())
                 for m in VERIFY_RE.finditer(f.read_text(encoding='utf-8'))]
        rec = [f'  - edition: {year}', f'    service: {FAM}/{service}',
               f'    source_url: {q(url)}', f'    retrieved: {RETRIEVED}',
               '    status: transcribed', '    depth: tier-1',
               f'    verifier: {q(VERIFIER)}', f'    note: {q(note)}']
        if items:
            rec.append('    verify_items:')
            for reading, text in items:
                rec += [f'      - anchor: {q(service)}',
                        f'        source_reading: {q(reading)}',
                        f'        note: {q(text)}']
                rows.append((service, year, reading, text))
        out.append('\n'.join(rec))
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8').rstrip('\n')
    body += ('\n\n  # --- Wave 12: the four deferred sections ---\n'
             + '\n'.join(out) + '\n  # --- end Wave 12 ---\n')
    p.write_text(body, encoding='utf-8')
    print(f"appended {len(out)} records, {len(rows)} verify_items")
    return rows


if __name__ == '__main__':
    for r in main():
        print("  VERIFY:", r[1], r[0], '::', r[2])
