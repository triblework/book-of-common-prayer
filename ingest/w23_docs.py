"""w23_docs.py -- Wave 23's edits to the published SOURCES.md, NOTICE.md and
README.md. Idempotent (each edit checks for its own marker); the verify rows
are regenerated from the 1979 cells' inline flags for the files this wave
touched, so the published index cannot drift. Run after gen_wave23_provenance."""
import os, re, sys
WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY_RE = re.compile(r'<!--\s*VERIFY:?\s*(.*?)-->', re.S)


def edit(rel, pairs):
    p = os.path.join(WT, rel)
    s = open(p, encoding='utf-8').read()
    for old, new, marker in pairs:
        if marker in s or (new == '' and old not in s):
            continue
        assert s.count(old) == 1, (rel, old[:70], s.count(old))
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)


SECTION = '''### The rest of the 1979 text against the publisher's own file (Wave 23)

Wave 19 collated the 1979 Psalter against Church Publishing's PDF of the book
and repaired seven named dropouts elsewhere. Wave 23 read **everything else**:
every paragraph of every 1979 cell outside the Psalter was located in the book
word for word, the Daily Office Lectionary was compared row by row, and the
1993 keying's own markup and hard wrap were dealt with. Rulings R22 and the
R11 addendum in `RULINGS.md`.

**The witness is a composite.** Two runs of the PDF's pages were replaced
after 1979 and carry the producer's slug: pp. 19–30 are a 2008 Calendar (with
commemorations added since 1979) and pp. 889–932 are the 2007 Revised Common
Lectionary. So `tables/calendar` and `tables/eucharistic-lectionary` have no
witness in this file and were not touched, and 100 of the 1979 flags (the 84
three-year-reading notes on the collects, and 16 in the eucharistic table)
cannot be closed from it; they need a scan of a printing from before 2006.
The text layer also confuses the digit 1 with capital I, and in the Daily
Office Lectionary prints citations no printing could have, so a citation
there is settled by the file only when a second check agrees (the other
year's same week, the same citation elsewhere, continuity with the rows
either side); otherwise both readings are flagged.

**What changed, in three reviewable steps.**

1. **Corrections and restorations** — 865 keyed items, each keyed to the
   paragraph it sits in, re-read in its page context, and applied file to
   file with the page recorded (`ingest/w23_evidence.json`): 297 word
   readings (typos, *thee*/*you* mix-ups, wrong, dropped, extra and reordered
   words, citation numerals), 12 spellings, 193 stops before a canticle's
   mediant that the repository's render had dropped, 28 rubric-final stops
   and 90 other stops set as the book sets them, two misspelt headings fixed
   (their slugs kept), and **104 restored passages** — swallowed and spliced
   stretches, two traditional collects the e-text had keyed from the
   contemporary text, and the eight collects the keying had lost outright
   (their flags are closed). Nothing was taken where the book's reading is a
   text-layer glyph or touches case or pointing. The **Daily Office
   Lectionary** gained 33 rows the e-text had lost or merged (820 rows
   against the e-text's 784), 58 corrected cells, 13 marks, the Year Two
   Christmas block (which printed Year One's Epistle and Gospel), and 3
   disputes the second check settled for the book; 15 it could not settle
   are flagged with both readings. The Lectionary's **Holy Days and Special
   Occasions** tables (pp. 996–1001), which the e-text carries but no wave
   had transcribed, are now `tables/daily-office-lectionary-holy-days` (45
   rows, 8 from the witness where the e-text had lost or damaged an entry).
2. **Markup** — 479 places where the 1993 e-text's own markup had been
   published as text (`=x=`, `&V.`, `&N.`, `&mdash.`, `[[ ]]`, broken speaker
   labels) are normalized to the book and the repository's conventions.
3. **Re-flow** — the 81 prayers files kept the e-text's hard wrap as
   paragraph breaks, 497 of them mid-sentence; they are re-flowed to the
   book's paragraphs (92 of 93 now verbatim).

Three Burial psalm verses the keying fused are flagged rather than restored,
because the repair would take a mediant from the file (R11). In all, 1979
flags 127 → 131 (19 closed, 23 opened). After the wave, 11 of 2,176 prose
paragraphs still differ from the book, every one accounted for (editorial
notes, refused glyph readings, the flagged verses, a running head).

**Not taken.** Letter case (the PDF's font runs name the small capitals, so
the small-capital LORD is recoverable; a pass of its own is queued), and 26
lines that open an e-text italic mark never closed (not one of the ruled
patterns).

---

'''

NOTICE = '''- **2026-10-16** — Wave 23: the **rest of the 1979 text, read against
  Church Publishing's own PDF** (Wave 19 did the Psalter). Every paragraph
  outside the Psalter was located in the book word for word and every
  difference keyed, re-read on its page and applied file to file.
  - **865 corrections and restorations**: word readings, spellings, the stops
    before a canticle's mediant the render had dropped, rubric stops, and 104
    passages the 1993 keying had swallowed or spliced — including the eight
    collects it lost outright and two it keyed from the wrong language set.
  - **The Daily Office Lectionary** repaired row by row (33 rows the e-text
    had lost or merged, a Christmas block that printed the wrong year's
    readings), and its Holy Days and Special Occasions tables added as a new
    file, which no earlier wave had carried.
  - **479 e-text markup marks** published as text are normalized, and the
    81 prayers files' hard wrap is re-flowed to the book's paragraphs.
  - **The witness is a composite**: its Calendar and Sunday lectionary pages
    are 2007–2008 replacements, so those two files were not touched and 100
    flags need a pre-2006 scan. Flags 19 closed, 23 opened.
  - This changes `texts/original` and `texts/normalized` only at `v1979`.

'''

CLOSED_COLLECTS = ['advent-4', 'easter-even', 'epiphany-6', 'epiphany-8', 'lent-4',
                   'st-andrew', 'st-james', 'st-simon-st-jude']
CLOSED_DOL = ["Proper 4 (=Week of 1-12; 2 Cor. 6:3-13(14-7:1); Luke 17:11-19)",
              "Year One / Proper 10 (Week of the Sunday closest to July 13) / Friday",
              "Mark 15:12-21", "Luke 10:1-12,17-20", "Matt. 22:15-22", "John 2:1-12",
              "2 Cor. 5:11-21 Mark 10:35-45", "1 Cor. 10:14-17,- 42[*]",
              "Rom. 11:1-12 Matt. 25:1-13",
              "Year Two / Proper 19 (Week of the Sunday closest to September 14) / Friday",
              "Luke 14:18-30"]
NAMES = {'occasional-offices/burial': '1979 (American) Burial of the Dead',
         'tables/daily-office-lectionary': '1979 (American) Daily Office Lectionary',
         'tables/daily-office-lectionary-holy-days': '1979 (American) Daily Office Lectionary (Holy Days)'}


def rows_from_cells():
    out = []
    for svc, name in NAMES.items():
        txt = open(os.path.join(WT, 'editions/1979', svc + '.md'), encoding='utf-8').read()
        for m in VERIFY_RE.finditer(txt):
            body = re.sub(r'\s+', ' ', m.group(1)).strip()
            q_ = re.search(r"'([^']+)'", body)
            key = q_.group(1) if q_ else body[:40]
            note = re.sub(r"^'%s';?\s*" % re.escape(key), '', body)
            out.append((svc, key, '| %s | `%s` | %s |\n' % (name, key.replace('|', '\\|'), note.replace('|', '\\|'))))
    return out


def main():
    edit('repo-root/SOURCES.md', [
        ("---\n\n## English line (`main`)", SECTION + "## English line (`main`)",
         "### The rest of the 1979 text against the publisher's own file (Wave 23)"),
    ])
    edit('repo-root/NOTICE.md', [
        ("## A note on transcription", NOTICE + "## A note on transcription",
         "Wave 23: the **rest of the 1979 text"),
    ])
    edit('repo-root/README.md', [
        ("The 1979 text has been read against Church Publishing's own PDF of the book: the Psalter was collated verse by verse (24 verses and 20 Latin headings corrected) and seven dropouts and typos elsewhere were repaired, including two collects and two passages the 1993 keying had swallowed.",
         "The 1979 text has been read against Church Publishing's own PDF of the book, all of it: the Psalter verse by verse (24 verses and 20 Latin headings corrected), and then every other paragraph — 865 corrections and restorations, 104 passages the 1993 keying had swallowed or spliced (the eight collects it lost among them), the Daily Office Lectionary repaired row by row and its Holy Days tables added, the keying's markup and hard wrap cleaned up. Two tables the file prints only in their 2007–2008 form were left alone.",
         "865 corrections and restorations"),
    ])
    p = os.path.join(WT, 'repo-root/SOURCES.md')
    s = open(p, encoding='utf-8').read()
    if 'Daily Office Lectionary (Holy Days)' not in s:
        # closed rows out
        for slug in CLOSED_COLLECTS:
            s, n = re.subn(r'^\| 1979 %s \| `[^`]*` \| the (?:traditional|contemporary)-language collect for this day is absent from the public-domain e-text.*\n' % re.escape(slug), '', s, flags=re.M)
            assert n == 1, (slug, n)
        for key in CLOSED_DOL:
            s, n = re.subn(r'^\| 1979 \(American\) Daily Office Lectionary \| `%s` \|.*\n' % re.escape(key), '', s, flags=re.M)
            assert n == 1, (key, n)
        # existing burial rows (if any) and the new rows: regenerate this wave's three files' rows
        for svc, name in NAMES.items():
            s = re.sub(r'^\| %s \| .*\n' % re.escape(name), '', s, flags=re.M)
        rows = ''.join(r for _s, _k, r in rows_from_cells())
        anchor = "| 1979 (American) Eucharistic Lectionary | `Luke 12:13-21` |"
        i = s.index(anchor); j = s.index('\n', i) + 1
        s = s[:j] + rows + s[j:]
        open(p, 'w', encoding='utf-8').write(s)
    print('w23 docs: ok (%d verify rows for this wave\'s files)' % len(rows_from_cells()))


if __name__ == '__main__':
    main()
