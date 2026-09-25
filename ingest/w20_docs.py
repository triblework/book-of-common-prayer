"""w20_docs.py -- Wave 20's edits to the published SOURCES.md and README.md.
Idempotent (each edit checks for its own marker). Run once after the cells."""
import os
WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def edit(rel, pairs):
    p = os.path.join(WT, rel)
    s = open(p, encoding='utf-8').read()
    for old, new, marker in pairs:
        if marker in s or (new == '' and old not in s):
            continue
        assert s.count(old) == 1, (rel, old[:60])
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)


GAP_1662 = ('| 1662 | Kalendar, Proper Lessons, both rubrics | The Church of England serves only the **post-1922 recension** of these (verse-level citations, "or" alternatives, and PDFs that are explicitly the Revised Tables of Lessons Measure 1922). Its *Tables and Rules* and *Vigils and Fasts* PDFs **do** print the 1662 text, and those are transcribed. |\n')
PL_OLD = ('| 1549–1662 | Proper Lessons | These books print their proper lessons as some thirty small per-occasion tables whose column heights vary with the occasion.')
PL_NEW = ('| 1549–1604 | Proper Lessons | These books print their proper lessons as some thirty small per-occasion tables whose column heights vary with the occasion (as recorded from their own sources in Wave 14; not re-checked since). The 1662 book does NOT: it prints one table that the row model fits, transcribed in Wave 20.')

SECTION = '''### The 1662 tables from the Annexed Book (Wave 20)

Until this wave `v1662` carried no Kalendar, Proper Lessons or reading rubrics
of its own: the Church of England serves only the post-1922 recension of
those, so 1662 inherited 1559's Kalendar and rubrics, and had no Proper
Lessons or Proper Psalms at all. Wave 18's witness — the **Annexed Book**, the
manuscript annexed to the Act of Uniformity 1662, in HMSO's 1892
type-reproduction (Wikimedia Commons, `File:The_Book_of_Common_Prayer.pdf`) —
prints all of them, and they are now transcribed from it: the Kalendar (twelve
month pages), the Proper Lessons (one table in two sections, Sundays and
Holy-days), the Proper Psalms on certain days, and the Order how the Psalter,
and how the rest of Holy Scripture, is appointed to be read.

**This witness is the only source for these files**, so they are in the
**manuscript's own spelling** — *Epiphanie of our Ld.*, *Hilarie B. &, Conf.*,
*Matth.*, *onely*, *vpon* — and not in the modernized spelling of the rest of
the 1662 node. The manuscript's own preface disclaims it as a standard of
orthography; these are its spellings, not those of the printed Sealed Books of
1662, which no allow-listed host has. `texts/normalized` smooths them as usual.
So a `v1559 → v1662` diff of these files shows two printings' spelling as well
as the real changes — for which the book's own lesson columns are the thing to
read.

How the tables are set: chapter numbers, which the book prints in roman, are
arabic (as in every other Kalendar here), with the printed extent kept
(`Luke 1. to 39`); the Golden Number, the Roman date (Kalends, Nones, Ides)
and the lunar line are left out as calendrical apparatus, as they were for
1549–1559; the book prints no Psalter-day column, so the rows have none; the
Sunday letters are capitals because the book's are; typeface (bold holy days,
italic commemorations) is not marked. The repository's standing decisions on
all of this are in `RULINGS.md` on the `authoring` branch (R12–R17).

How it was read: each page was rendered, deskewed and cut up by its printed
rules; every Kalendar cell was read twice by machine (on two independent
renderings of the file) and once by eye at high resolution, and every
disagreement was looked at again. The structure checks are clean — twelve
months, 366 rows (the book prints a 29th of February), the Sunday letters
unbroken through the year, every holy day's lessons blank, the second lessons
running on chapter by chapter. **The June page** is drawn blank by some PDF
viewers — its image uses a compression that not every decoder can read — and
was read from Wikimedia's own rendering of the same file.

Kept as the book prints them, though they look like slips: *S Thomos Apost.*
(21 December); the 29th of February's lessons *Matt. 7* and *Rom. 12*, which
break both second-lesson courses; *Tob. 4* then *Tob. 6* on 30 September. Three
readings are flagged below: a stop the June rendering cannot settle, a missing
stop between two chapters in June, and a broken entry for St Anne (26 July).

'''
VERIFY_ROWS = (
    '| 1662 Kalendar (June 11) | `S. Barnab, Apost. & M.` (normalized: `S. Barnab, Apost. and M.`) | The stop after *Barnab* looks like a comma in Wikimedia\'s 1920px rendering of the June page (the only legible one); a full stop cannot be ruled out. |\n'
    '| 1662 Kalendar (June 16) | `26 27` | Morning 1 prints two chapters of Job; no stop is visible between them at 1920px. |\n'
    '| 1662 Kalendar (July 26) | `S. Anne, mother to ye Bl. V. M.` | The letters after *Bl.* are broken in the print (both renderings): an upright stroke, a stop, part of an M, a stop. *V. M.* is what the fragments allow, not what they show. |\n')
ANCHOR_V = '| 1789 (American) Kalendar | `November Morning 1, Evening 1` |'

edit('repo-root/SOURCES.md', [
    (GAP_1662, '', 'Wave 20: GAP_1662_REMOVED'),
    (PL_OLD, PL_NEW, 'transcribed in Wave 20.'),
    ('---\n\n## English line (`main`)', SECTION + '---\n\n## English line (`main`)',
     '### The 1662 tables from the Annexed Book (Wave 20)'),
    (ANCHOR_V, VERIFY_ROWS + ANCHOR_V, '`S. Barnab, Apost. & M.`'),
])

README_OLD = ('> structure, tooling, and diff mechanism are complete; today the transcribed\n'
              '> text covers **Morning Prayer, Evening Prayer, the Litany, and Holy Communion**\n'
              '> in full across every edition that has them. No\n')
README_NEW = ('> structure, tooling, and diff mechanism are complete; today the transcribed\n'
              '> text covers **every service family the project set out to carry** — the\n'
              '> offices, the Litany, Holy Communion, the occasional offices, the Ordinal, the\n'
              '> propers, the Psalter and the tables — across every edition that has them;\n'
              '> what remains are recorded gaps and uncertain readings. No\n')
edit('repo-root/README.md', [(README_OLD, README_NEW, 'every service family the project set out to carry** — the')])
print('ok')
