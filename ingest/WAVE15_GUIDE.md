# Wave 15 — the 1928 tables: guide

Companion to `WAVE15_SCOPING.md` (the survey). This file records the rulings,
the method, and how to re-run and check the wave.

## Rulings (maintainer, 2026-09-11: "Take all five recommendations; download BCP1929.pdf")

1. **Full scope, one publish.** `v1928`'s own cells for `tables/calendar`,
   `tables/feasts-and-fasts`, `tables/proper-psalms` (three tables),
   `psalter/selections` and `tables/proper-lessons` (three tables), in Wave 14's
   column order and row conventions, so `git diff v1892 v1928` and
   `git diff v1928 v1979` are genuine comparisons.
2. **Witness: `1928/BCP1929.pdf`**, the scan of the original 1928 printing.
3. **Fix the rubric `absent:` in this wave.** 1892 and 1928 print both "Order
   how…" rubrics; Wave 14's `absent:` came from the table of contents. Author
   both editions' cells, drop 1892's `absent:`, and log the correction in NOTICE.
4. **Concerning the Service (1892/1928) goes to the backlog**, not this wave:
   the file's history is the 1549 Preface, so it is a slot-identity question.
5. **The Christian-Year lessons go in `tables/proper-lessons.md`**, under their
   own `##`, beside the Fixed Holy Days and Special Occasions tables.

Standing ruling (Wave 14): `v1928` is the ORIGINAL lectionary (1928–1944). The
1945 revision is deliberately omitted and logged (HANDOFF §8, SOURCES, NOTICE).

## Sources

| Role | File | What |
|---|---|---|
| carrier | `1928/Calendar&Tables_1928.pdf` (6 sheets) | Calendar; Tables and Rules |
| carrier | `1928/Lectionary_1928.pdf` (9 sheets) | rubrics, psalm tables, Selections, Tables of Lessons |
| witness | `1928/BCP1929.pdf` (319 scan pages, 2 book pages each, JPEG2000) | the original 1928 printing |

Raw PDF bytes are cached in `scrape-cache/` with a `.pdf` suffix
(`scrape.fetch` returns decoded text). justus needs http://, not https.

**The carrier was keyed from a LATER printing.** Its index puts the Calendar
at p. xlvi; the original has p. xxix. Readings that differ include the heading
"COLLECT, EPISTLE, AND GOSPEL" (the original has no AND), Good Friday's psalm
22:1-19 (the original prints 1-9), and two reworded sentences in the Scripture
rubric. It is not the 1945 revision: the original prints "A Table of Lessons for
the Christian Year" with separate psalm tables, and the 1945 book combines them.
(The maintainer's own copy is a 1953 printing of the 1945 revision.)

## Method

- **Parsing from text runs** (`w15_src.runs`: y, x, text, size), never pypdf's
  layout mode for the lessons (1–2-space cell gaps scrambled rows). A run under
  5.5pt is small capitals and is lowercased, which recovers the typeset case.
- **De-kerning** removes spaces only: a probabilistic DP over a corpus (justus
  1928/1892 HTML and the editions) with a case-shape rule. It never adds or
  changes a letter.
- **`citation()`** does typographic normalization only (dashes, spacing,
  ordinals `1`→`I` before a book name, rejoining a split book name).
- **Witness pass.** Every row was compared with the scan crop
  (`w15_src.scan_crop`, via `sips`; export `W15_SCRATCH` for the crop dir).
  Disagreements are recorded in `w15_witness.py` / `w15_lessons_witness.json`
  as (text-layer reading, scan reading, book page), keyed by section, week, row,
  duplicate index and field, with a **stale-reading check**: a correction whose
  text-layer reading is no longer what the parser produces fails the build.
  Nothing is computed; the Calendar's letter cycle only *finds* the defects.
- **One inline VERIFY:** Palm Sunday's "Also: 24, 130, 132" (proper-psalms).
  The scan's last digit is damaged.

Totals: 229 corrections (calendar 13, feasts 10, psalms 14, rubrics 2, lessons
190).

## Row schema (as Wave 14)

- Calendar: `January 1 | Sunday Letter: A | Kalendar Note: Circumcision`;
  29 February carries `Sunday Letter: —`. 366 rows. Title `# The Kalendar`,
  matching 1979, so the heading does not diff.
- Proper Psalms: `Advent | Morning: 8, 50 | Evening: 96, 97`, following the
  book's NOTE (Morning and Evening split at the semicolon). Rows printed without
  that shape are `Psalms:`.
- Lessons, Christian Year: `<label> | Morning 1 | Morning 2 | Evening 1 | Evening 2`;
  stacked optional alternatives as ` / `; the printed directions for the 25th and
  26th Sundays after Trinity as `Lessons: …`. Fixed Holy Days: Eve 1/2, Morning 1/2,
  Evening 1/2. Special Occasions: First Lesson / Second Lesson.

## Rebuild and gates

```bash
python3 ingest/w15_build.py        # all Wave 15 cells + the two Wave 14 builders it touches
python3 ingest/w15_fidelity.py     # 0 unattested values; sensitivity 18/18
python3 ingest/w15_audit.py        # 0 anomalies; asserted row counts
python3 ingest/w14_fidelity.py; python3 ingest/w14_audit.py   # standing gates
python3 tools/verify_index.py --root . --check
```

`w15_fidelity` tests VALUES AS STRINGS (lectionary numbers are the content): an
exact substring of the source, or a LOCAL cover (pieces of 6+ characters within
200 of each other; a short last piece only where it begins a printed line or
completes a hyphen). Witness corrections are reversed per line before the test.
The sensitivity list holds readings the text layer prints nowhere; each must fail.

`w15_audit` checks counts, the letter cycle in every edition's calendar, 1928
holy days against the Table of Feasts, week structure (exemptions each carry a
reason), row shapes and the witness total.

## Other cells this wave touches

- `w14_build_1979_calendar.py`: a bare "29" is the next day (29 February), not a
  continuation. The 1979 calendar now has 366 rows.
- `w14_build_rubrics.py`: 1789 end markers fixed (stray "> Proper" and "¶ <a"
  removed); 1892 slices added; `SOURCE_NOISE` "EveningPrayer".
- `w14_editions.py`: 1892 and 1928 present for both rubrics; 1979 absent for the
  Psalter rubric.

## Scripts

`w15_src.py`, `w15_witness.py` (+ `w15_lessons_witness.json`),
`w15_calendar.py`, `w15_feasts.py`, `w15_psalms.py`, `w15_rubrics.py`,
`w15_lessons.py`, `w15_show.py` (print rows; `W15_RAW=1` skips the witness),
`w15_addw.py` (record witness entries), `w15_build.py`, `w15_fidelity.py`,
`w15_audit.py`, `gen_wave15_provenance.py`.
