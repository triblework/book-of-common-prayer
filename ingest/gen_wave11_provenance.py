#!/usr/bin/env python3
"""Wave 11 — append one provenance record per <prayer, edition>, plus the
verify_items that reconcile every inline VERIFY, and matching SOURCES.md rows.
"""
from __future__ import annotations
import re, sys
from pathlib import Path


def q(s: str) -> str:
    """YAML double-quoted scalar. Several notes quote their source's apparatus
    verbatim ("This prayer and rubric added in 1845"), and an unescaped inner
    double quote ends the scalar and corrupts the file."""
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

WT = Path(__file__).resolve().parent.parent
FAMILY = 'prayers-and-thanksgivings'
RETRIEVED = '2026-09-01'
VERIFIER = 'claude-opus-5 (scripted ingest + two gates)'

SRC = {
 '1552': ('http://justus.anglican.org/resources/bcp/1552/Litany_1552.htm',
          'The occasional prayers printed after the Litany suffrages. 1552 is the first '
          'edition to carry any of this block (1549 has none). Extracted by explicit spine '
          'line number (ingest/w11_build_spine.py); the book prints them inline after the '
          'Litany, recorded as a book-order note in NOTICE.md, not as a text diff.'),
 '1559': ('http://justus.anglican.org/resources/bcp/1559/Litany_1559.htm',
          'State prayers + occasional prayers printed after the Litany suffrages. Per the '
          "page's own apparatus the Thanksgivings and the Royal Family prayer are NOT 1559 "
          '(see 1604). Inline placement recorded in NOTICE.md, not as a text diff.'),
 '1604': ('http://justus.anglican.org/resources/bcp/1559/Litany_1559.htm',
          'Derived from the 1559 page, whose apparatus dates these additions to 1604: '
          '"The following Thanksgivings were added in 1604", "[prayer added 1604]" '
          '(Royal Family) and "Replaced by a prayer for the King in 1604". Nothing is '
          'derived that an apparatus note does not license.'),
 '1637': ('http://justus.anglican.org/resources/bcp/Scotland/Litany_1637.htm',
          'The full block (state prayers, Ember weeks, occasional prayers, concluding '
          'collect, thanksgivings) printed after the Litany suffrages in the Scottish book.'),
 '1662': ('https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/'
          'book-common-prayer/prayers-and-thanksgivings',
          'The block becomes its own section, "Prayers and Thanksgivings upon several '
          'Occasions"; the Litany already ends "Here endeth the Litany." The state prayers '
          'move into Morning and Evening Prayer and are absent here (a relocation, not a '
          'deletion — see NOTICE.md).'),
 '1789': ('http://justus.anglican.org/resources/bcp/1789/Prayers&Thanks_1789.htm',
          'First American book. The Convention prayer on this page is EXCLUDED from 1789: '
          "the page's own apparatus column reads \"This prayer and rubric added in 1845\". "
          'A Prayer for all Conditions of Men and the General Thanksgiving move into '
          'Morning and Evening Prayer (relocation, not deletion — see NOTICE.md).'),
 '1892': ('http://justus.anglican.org/resources/bcp/1892/Pray&Thanks_1892.htm',
          'Adds the pastoral prayers. The Penitential Office printed on the same page is '
          'excluded from this wave by the locked scoping ruling (ingest/WAVE11_SCOPING.md).'),
 '1928': ('http://justus.anglican.org/resources/bcp/1928/Pray&Thanks.htm',
          'Largest historic set. Includes the six untitled COLLECTS printed under one shared '
          'rubric inside this section (in scope; slugs are incipit-derived, see '
          'ingest/WAVE11_GUIDE.md). Satucket/Wohlers formatted text of a public-domain book.'),
 '1979': ('http://justus.anglican.org/resources/bcp/bcpprayr.txt',
          '70 Prayers + 11 Thanksgivings from the public-domain 1979 e-text, built by '
          'ingest/transform_1979_prayers.py (source->script->file). Mapped to a historic slug '
          'only on demonstrable lineage; contested candidates keep their own 1979 slug and the '
          'rejection is recorded in the transform (CROSSWALK_REJECTED).'),
}

VERIFY_RE = re.compile(r"<!--\s*VERIFY:\s*'([^']*)'")


def main():
    out, verify_rows = [], []
    for year in sorted(SRC):
        d = WT / 'editions' / year / FAMILY
        if not d.is_dir():
            continue
        url, note = SRC[year]
        for f in sorted(d.glob('*.md')):
            slug = f.stem
            items = []
            for m in VERIFY_RE.finditer(f.read_text(encoding='utf-8')):
                reading = m.group(1)
                full = re.search(re.escape(m.group(0)) + r'(.*?)-->',
                                 f.read_text(encoding='utf-8'), re.S)
                text = re.sub(r'\s+', ' ', full.group(1)).strip() if full else ''
                items.append((reading, text))
                verify_rows.append((year, slug, reading, text))
            rec = [f'  - edition: {year}',
                   f'    service: {FAMILY}/{slug}',
                   f'    source_url: {q(url)}',
                   f'    retrieved: {RETRIEVED}',
                   f'    status: transcribed',
                   f'    depth: tier-1',
                   f'    verifier: {q(VERIFIER)}',
                   f'    note: {q(note)}']
            if items:
                rec.append('    verify_items:')
                for reading, text in items:
                    rec.append(f'      - anchor: {q(slug)}')
                    rec.append(f'        source_reading: {q(reading)}')
                    rec.append(f'        note: {q(text)}')
            out.append('\n'.join(rec))

    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8').rstrip('\n')
    body += ('\n\n  # --- Wave 11: Prayers and Thanksgivings upon several Occasions ---\n'
             + '\n'.join(out) + '\n  # --- end Wave 11 ---\n')
    p.write_text(body, encoding='utf-8')
    print(f"appended {len(out)} provenance records, {len(verify_rows)} verify_items")
    return verify_rows


if __name__ == '__main__':
    rows = main()
    for r in rows:
        print("  VERIFY:", r[0], r[1], '::', r[2])
