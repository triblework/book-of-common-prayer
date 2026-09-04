#!/usr/bin/env python3
"""Wave 14 — SOURCES.md rows, the scope paragraph, NOTICE.md and README.md.

`SOURCES.md`'s "Current transcription scope" is PUBLISHED PROSE THAT NO GATE
VALIDATES, and it had gone stale AGAIN: it still listed the four sections Wave
12 transcribed as "not yet transcribed". It is rewritten here, along with the
README's "Coming soon", which still promised the propers Wave 10 delivered.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
RR = WT / 'repo-root'
VERIFY_RE = re.compile(r"<!--\s*VERIFY:\s*'([^']*)'(.*?)-->", re.S)

LABEL = {'1549': '1549', '1552': '1552', '1559': '1559', '1789': '1789 (American)',
         '1892': '1892 (American)', '1928': '1928 (American)',
         '1979': '1979 (American)'}
NAME = {'calendar': 'Kalendar', 'proper-lessons': 'Proper Lessons',
        'feasts-and-fasts': 'Feasts and Fasts',
        'eucharistic-lectionary': 'Eucharistic Lectionary',
        'daily-office-lectionary': 'Daily Office Lectionary'}


def sources_rows():
    rows = []
    for ed_dir in sorted((WT / 'editions').iterdir()):
        for fam in ('tables', 'front-matter'):
            d = ed_dir / fam
            if not d.is_dir():
                continue
            for f in sorted(d.glob('*.md')):
                slug = f.stem
                if fam == 'front-matter' and not slug.startswith('order-how'):
                    continue
                for m in VERIFY_RE.finditer(f.read_text(encoding='utf-8')):
                    note = re.sub(r'\s+', ' ', m.group(2)).strip().lstrip(';').strip()
                    rows.append('| %s %s | `%s` | %s |'
                                % (LABEL.get(ed_dir.name, ed_dir.name),
                                   NAME.get(slug, slug), m.group(1), note))
    return rows


SCOPE = """## Current transcription scope (read this first)

This repository models the whole genealogy (all branches and tags) and
demonstrates the diff mechanism end-to-end. The **transcribed text** now covers
nine service families, across every edition that has them:

- **`daily-office/`** — Morning and Evening Prayer
- **`the-litany/`** — the Litany
- **`holy-communion/`** — the Communion office, across **all twelve** editions
- **`occasional-offices/`** — Baptism (public, private, riper years),
  Confirmation, Matrimony, Visitation of the Sick, Burial, Churching,
  Commination, the Catechism, the Forms of Prayer to be used at Sea, the
  American Penitential Office, Family Prayer, and the 1789 Prayer and
  Thanksgiving to Almighty God
- **`ordinal/`** — the Preface and the ordering of deacons, priests and bishops
- **`front-matter/`** — Preface, Concerning the Service, Of Ceremonies,
  Ratification, and the two rubrics that govern the tables (the Order how the
  Psalter, and how the rest of Holy Scripture, is appointed to be read)
- **`collects-epistles-gospels/`** — the propers for 106 occasions across the
  church year (collects in full; Epistle and Gospel as their appointed citation)
- **`prayers-and-thanksgivings/`** — the occasional prayers, state prayers and
  thanksgivings, 135 prayers
- **`tables/`** — the Kalendar, the Tables of Proper Lessons, the Tables and
  Rules for the Feasts and Fasts, and the 1979 three-year eucharistic and
  two-year Daily Office lectionaries, all as normalized long-form (one entry per
  line, stable column order) so a changed cell is a one-line diff

This is where the tradition's most famous changes live — the 1552 penitential
introduction; the Holy Communion 1549→1552 restructuring, the moving Gloria in
Excelsis, the changing words of administration, and the Black Rubric
appearing/vanishing/returning across 1552/1559/1662; the 1552 baptismal
simplification; the Reformation stripping of the Burial office in 1552; the 1604
Catechism sacraments section; the growth of the occasional prayers from nothing
in 1549 to eighty-one texts in 1979; and, in the tables, the disappearance of the
Kalendar's four lesson columns between 1789 and 1979 as the readings move into a
two-year cycle keyed to the church's own weeks rather than to the civil date.

Presence varies by edition and is itself the signal: most families run across the
ten full-book editions, while the Scottish 1764 "Wee Bookie" and 1929 are
Communion-only; the Commination is English/Scottish only (the American line drops
it); the propers and the Prayers and Thanksgivings are absent from 1764/1929.

**Not yet transcribed**, tracked as a later wave: the **Psalter**. Several tables
are also carried for some editions but not others; where an edition's own table
could not be sourced it INHERITS its parent's and is marked
`inherited-unreviewed` in `provenance.yaml`. **That is a transcription gap, not a
claim that the edition reprinted its parent unchanged.** The gaps are listed
below. Where an edition could not be sourced cleanly, that is always stated
explicitly rather than filled with invented text.

### Recorded gaps in the tables

| Edition | Table | Why |
|---|---|---|
| 1604 | Kalendar, both rubrics | No allow-listed 1604 source exists — the same gap recorded for the 1604 propers. |
| 1662 | Kalendar, Proper Lessons, both rubrics | The Church of England serves only the **post-1922 recension** of these (verse-level citations, "or" alternatives, and PDFs that are explicitly the Revised Tables of Lessons Measure 1922). Its *Tables and Rules* and *Vigils and Fasts* PDFs **do** print the 1662 text, and those are transcribed. |
| 1637 | Kalendar, both rubrics | The Scottish line is transcribed for the Communion; the 1637 book does print these. |
| 1892 | Kalendar | The source HTML has lost the table's row structure — several days are packed into one line-break slot, the packing differs column by column, and continuation lines interleave. No structural rule recovers per-day rows, and a wrong reconstruction would silently misdate a year of lessons. |
| 1928 | Kalendar, Proper Lessons, Feasts and Fasts | PDF-only. 1928 also revised its lectionary twice — the original (1928–1944) and the 1945 revision — and one edition node cannot carry both. |
| 1549–1662 | Proper Lessons | These books print their proper lessons as some thirty small per-occasion tables whose column heights vary with the occasion. No single row model fits them, and applying one only where it succeeds would publish a file reading as "these occasions only" — a false historical claim. |
"""

NOTICE_ENTRY = """- **2026-09-02** — Wave 14: the **lectionary and calendar tables**, under a new
  `tables/` family, represented as normalized long-form (one entry per line,
  stable column order) so a changed cell is a one-line diff. This wave pays a
  debt Wave 10 deliberately deferred: the 1979 **three-year (A/B/C) eucharistic
  lectionary** (280 entries) and the **two-year Daily Office Lectionary** (784
  entries across 108 weeks) had no representation in the repository at all,
  because three reading sets per day cannot fit the single-citation slot the
  historic propers use. Their source is the eleventh part of the public-domain
  1979 e-text, which no earlier wave had fetched. Also added: the **Kalendar**
  for 1549/1552/1559/1789/1979, the **Tables of Proper Lessons** for 1789/1892,
  the **Tables and Rules for the Feasts and Fasts** for 1662/1789/1892/1979, and
  the two rubrics that govern them under `front-matter/`. Flagship diff:
  `git diff v1789 v1979 -- texts/normalized/tables/calendar.md`, where the
  Kalendar's four lesson columns vanish — 1979 keeps the civil-date calendar but
  moves the readings into a lectionary keyed to the church's own weeks.
  Presence notes: 1892 and 1928 **merged** both rubrics into *Concerning the
  Service of the Church*, so those take an explicit absence; 1979 has no
  successor to the Psalter-order rubric (only two of its six provisions survive,
  inside the lectionary note) but does have one to the Scripture-order rubric,
  which it prints as *Concerning the Daily Office Lectionary*. Editions whose own
  table could not be sourced INHERIT their parent's and are marked
  `inherited-unreviewed`; those gaps are listed in `SOURCES.md` and are
  transcription gaps, not claims about the books. The 1979 e-text is missing
  pages 889, 899 and 909 with their content; those losses are flagged inline and
  nothing is reconstructed.
- **2026-09-02** — A correction ships with Wave 14. `tools/sentence_split.py`
  gained an additive abbreviation list for the forms these tables print, and it
  incidentally fixes two places where the splitter had been breaking a sentence
  mid-phrase after an abbreviated "S.": the 1552 collect for Saint Mark
  ("thy Evangelist S. Marke") and the 1637 collect for Saint Matthew ("didst
  call S. Matthew"). Additive entries can only prevent a split, and the change
  was measured against the previous tool: those two cells are the only
  pre-existing text affected.
"""


def main():
    # 1. SOURCES: uncertain-passage rows
    p = RR / 'SOURCES.md'
    s = p.read_text(encoding='utf-8')
    rows = sources_rows()
    anchor = '## Uncertain passages (`<!-- VERIFY -->`)'
    i = s.index(anchor)
    j = s.index('\n\n', s.index('|----------------|', i))
    s = s[:j] + '\n' + '\n'.join(rows) + s[j:]
    # 2. SOURCES: the scope section
    a = s.index('## Current transcription scope')
    b = s.index('\n---\n', a)
    s = s[:a] + SCOPE + s[b:]
    p.write_text(s, encoding='utf-8')
    print('SOURCES.md: +%d uncertain rows, scope section rewritten' % len(rows))

    # 3. NOTICE: rebuild-log entry
    p = RR / 'NOTICE.md'
    s = p.read_text(encoding='utf-8').rstrip('\n')
    s += '\n' + NOTICE_ENTRY
    p.write_text(s, encoding='utf-8')
    print('NOTICE.md: rebuild-log entry appended')

    # 4. README: refresh the stale "Coming soon" and add a flagship diff
    p = RR / 'README.md'
    s = p.read_text(encoding='utf-8')
    s = s.replace(
        "**Coming soon** (in progress): the Collects, Epistles & Gospels; the Psalter and\nlectionary tables will follow.",
        "The **lectionary and calendar tables** are transcribed under `tables/` as\nnormalized long-form — the Kalendar, the Tables of Proper Lessons, the Tables and\nRules for the Feasts and Fasts, and the 1979 three-year eucharistic and two-year\nDaily Office lectionaries. **Coming soon**: the Psalter.")
    s = s.replace(
        "# The Black Rubric (Declaration on Kneeling) appears in 1552, vanishes in 1559,",
        "# The Kalendar loses its lesson columns between 1789 and 1979: the American 1979\n"
        "# book keeps a civil-date calendar but moves the readings into a two-year cycle\n"
        "# keyed to the church's own weeks, so the four lesson columns simply vanish:\n"
        "git diff v1789 v1979 -- texts/normalized/tables/calendar.md\n\n"
        "# The Black Rubric (Declaration on Kneeling) appears in 1552, vanishes in 1559,")
    p.write_text(s, encoding='utf-8')
    print('README.md: status refreshed, flagship diff added')


if __name__ == '__main__':
    main()
