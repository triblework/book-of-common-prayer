# Wave 20 — the 1662 Kalendar and its tables, from the Annexed Book: guide

Closes the gap `SOURCES.md` had recorded since Wave 14 as "1662 | Kalendar,
Proper Lessons, both rubrics". Five cells at `v1662`, all from the Annexed
Book (Wave 18's witness, `File:The_Book_of_Common_Prayer.pdf` on Commons):

| cell | PDF pp. | what |
|---|---|---|
| `tables/calendar` | 44–55 | twelve months, 366 rows (Feb prints a 29th) |
| `tables/proper-lessons` | 36–38 | ONE table, Sundays (56 rows) + Holy-days (33) |
| `tables/proper-psalms` | 38 | six occasions — `v1662` had none, and no gap said so |
| `front-matter/order-how-psalter-appointed` | 34 | the Psalter rubric |
| `front-matter/order-how-rest-of-scripture` | 35 | the Scripture rubric |

Before this wave `v1662` inherited 1559's Kalendar and rubrics and had no
Proper Lessons at all. `texts/` changes at `v1662` only; 1789 authors all five
itself, so nothing leaks down the American line (the full build proves it).

## The rulings (all in `RULINGS.md`, made or recorded this wave)

- **R12** (maintainer) — the witness is the ONLY source here, so the files are
  in the manuscript's own spelling. R7 forbids using the MS to overrule another
  text's spelling; it does not forbid transcribing it where nothing else exists.
- **R13** (maintainer, confirming Wave 14's Ruling B) — chapter numerals to
  arabic with the extent verbatim; Golden Number, Roman date, lunar line out as
  apparatus; no Psalter Day (1662 prints none); footnotes as `Footnote |` rows;
  occasion ordinals (`ii`, `xiv`) stay roman — they are labels.
- **R14** — a second rendering of one file is not a second witness (June).
- **R15** (maintainer) — 1662's Proper Lessons fit the row model; the gap row
  narrows to 1549–1604; Proper Psalms come in with them.
- **R16** — typeface not encoded; superscripts inline; letters by glyph (J/I);
  a sign standing for missing letters is set (`Gregoriꝰ`, `Añunciation`,
  `Jm̄oveable`), a mark that only flags an abbreviation is not (`Ecclus`);
  spacing/hyphen conventions for the rubrics; *sic* readings kept and noted.
- **R17** — a table row is one unit for `sentence_split.py`. Measured first:
  one pre-existing row (1789 Proper Psalms) relied on the build splitting it;
  its source was pre-split, and `w20_gates` proves the old and new splitter
  agree on every pre-existing file.

## The page problem nobody had noticed: June

Every page of this PDF is MRC-compressed — a JPX colour layer painted through a
JBIG2 text mask. On p. 49 (June) Apple's decoder fails ("Too many symbols in
JBIG2 symbol dictionary") and every local render is blank but for ghosting;
Wave 18's whole-book OCR had recorded 0 lines there without comment. The text
is in the file (Google's text layer even has it). Wikimedia renders PDF pages
server-side with a different decoder, and its 1920px thumbnail of p. 49 is
legible, so June is read from that (`ingest/w20_fetch.py`: the scraper's
allow-list, robots and rate limit, for binary files). **Anyone reading this
PDF again: check p. 49 is not blank in your renderer.** Commons thumbnails come
only in standard widths (1920 is the largest allowed here; 2560/3598 → HTTP 400).

## The pipeline

```
w18_render.py --size=4400 N          # pypdf split -> Quick Look (as Wave 18)
bin/w20_grid page.png out.png        # deskew (±1.5°, best by rule length) + find rules
w20_kal_read.py                      # A = local, B = Commons; rows from the Roman-date
                                     #   strip's y; every cell cut out and OCR'd
                                     #   (bin/w20_cells: padded, 3x, one rect at a time)
w20_kal_eye.txt                      # the EYE READ, as printed, off 4400px crops
w20_kal.py [--write]                 # structure checks + A/B/eye comparison -> cell
w20_pl_eye.txt, w20_pl.py [--write]  # Proper Lessons/Psalms, with the cover test
w20_cellcrop.py / bin/w20_strip      # crop cells / stack crops for a re-look
gen_wave20_provenance.py, w20_docs.py, w20_gates.py
```

Build the binaries: `swiftc -O ingest/w20_{grid,cells,strip,ocrword}.swift -o
ingest/bin/…` plus Wave 17's `w17_ocr` / `w17_ocrbox`. `w20_kal_strips.py`
(whole-column strips) and `w20_ocrword.swift` (word boxes) were first attempts,
superseded by per-cell reading; kept for the record.

## What the machine could and could not do

- **Rows** came out perfectly: the Roman-date column prints exactly one entry
  per day, so its strip OCR gives every row's y. February (skewed −1.3°) and
  April (−0.9°) needed the deskew. November's strip picked up the footnote;
  the ladder was rebuilt from the pitch.
- **Cells** did not: on this italic type Vision agrees with itself (A = B) on
  roughly a third of the lesson cells. It drops a lone `v` or `x`, reads `xv`
  as "AX", loses an `i`. So the **eye read carries the weight**, and the
  machine reads find the cells to look at twice: 39 cells where A and B agreed
  against the eye read were all re-read — the eye read stood in all 39.
- **Structure is the strong check.** Sunday letters unbroken A–G over 365
  days; every all-blank lesson row is a holy day; M2 and E2 run on chapter by
  chapter with no gap all year (so every second-lesson cell is corroborated);
  the Old Testament course has 23 skips, every landing cell re-read at pixel
  level and every skip the book's own (genealogies, the tabernacle chapters,
  census lists, selective Ezekiel). For the Proper Lessons the Sunday first
  lessons run on in book order with no backward step in 56 rows; the Holy-day
  rows have no structure, and their cover test (column-strip OCR, 15% window,
  sensitivity proved by injected readings) finds 457 of 693 tokens — the rest
  mostly the italic `vr` and `to`.

## Readings worth knowing

- 29 February prints no letter but lessons `xiii | Matt. 7. | xiiii | Rom. 12.`
  — breaking both second-lesson courses. Clear on the page; kept, noted.
- `S Thomos Apost. & M.` (21 Dec), `Jnnocents day.`, `CH. II. Nat. et Ret.`
  (29 May), `K. Charles Mart.` (30 Jan), `Papists Conspiracy` (5 Nov).
- 30 Sept: Tob. 4 then Tob. 6 (the `i` of `vi` filled with ink but there).
- Proper Psalms, Ascension evening: **cviii (108)**. HANDOFF §8 carries
  1789's "24, 47, 103" as a suspected misreading (1892 reads 108). This is
  context for that lead, NOT a source for 1789 (R2): only a 1789 scan settles it.
- The mark over `Ecclus` varies — a tilde (p. 26), a cross-like flourish
  (p. 27), a struck `l` (Kalendar). Read as one abbreviation flag, not carried.

## Three flags

June 11 `S. Barnab, Apost. & M.` (comma or stop, at 1920px); June 16 M1
`26 27` (no stop visible between the chapters); July 26 St Anne, `Bl. V. M.`
broken in the print. The normalizer turns `&` into `and` inside the flag, so
the `SOURCES.md` row carries both forms (the published-context
`verify_index` failed until it did).

## Gates and build

`w20_gates` 0 (regeneration, structure, R13 schema, rubric attestation,
cover sensitivity, R17 splitter equivalence, containment, flags);
`w13_fidelity`/`w13_audit`/`w14_fidelity`/`w15_fidelity`/`w16_gates`/
`w19_gates` 0 unchanged; `w14_audit`, `w15_audit`, `w18_gates` needed
reasoned amendments (1662's per-occasion lesson counts as KNOWN_GOOD; 1662's
capital Sunday letters; Wave 18's flag count restricted to the cells it read).
`verify_index --check` 331 inline / 427 provenance. Full `build_history.py`:
`texts/` differs from the live tags ONLY at `v1662` (10 files); every tag
passes `sentence_split --check`, `normalize --check` and published-context
`verify_index`; no U+FFFD.

## Lessons

- **Look at every page you think you have.** Wave 18's page record showed 0
  lines for p. 49 and nobody asked why; it was a decoder failure, not a blank.
- **Rows from geometry, cells from eyes, structure as the judge.** On this
  type the machine is good at *where* and poor at *what*.
- **A tool change is a corpus change.** The splitter fix was measured on every
  file before and after, not assumed additive.
- **Record the call when you make it.** Every convention here went into
  `RULINGS.md` as it was decided (maintainer's instruction, 2026-09-25).
