# Wave 14 — build guide: lectionary & calendar tables

Rulings taken from the maintainer 2026-09-02 on the options in
`WAVE14_SCOPING.md`. **These are LOCKED. Do not re-litigate.** Read
`WAVE14_SCOPING.md` first for the survey those rulings rest on.

---

## 1. The locked rulings

- **RULING A — one file per table.** The 1979 three-year lectionary is ONE file
  with `## Year A` / `## Year B` / `## Year C` sections, not three files; the
  Daily Office Lectionary likewise carries `## Year One` / `## Year Two`. A table
  is one table in the book, and three files would imply three editions of one
  thing.
- **RULING B — five content tables plus two rubric sections; the arithmetic is
  out.** See §2 for the file list. The golden-number / Sunday-letter / epact /
  Almanack / Table-to-find-Easter / Tables-for-finding-Holy-Days grids are
  EXCLUDED: their long-form rows (`14 | March 21 | C`) carry no liturgical
  meaning, and their cross-edition diff is calendar arithmetic rather than
  revision (1789's runs to 1899, 1892's to a different terminal year). The
  *Rules* prose that governs them IS included, in `feasts-and-fasts.md`. The
  Table of Kindred and Affinity is also out — it is marriage law, and belongs
  with Wave 6 if anywhere.
- **RULING C — 1979 sits on its own paths.** 1979 abolished the civil-date
  Kalendar-with-lessons and the one-year Proper Lessons table; both go in
  `absent:` at 1979, which is TRUE and makes the deletion the headline
  `v1928 -> v1979` diff. Its two replacement lectionaries are keyed by liturgical
  week, are structurally incommensurable with a civil-date table, and therefore
  take their own paths. Per Wave-10 Decision C, nothing is forced onto a shared
  path to manufacture a diff.
- **RULING D — 1662 leaves the calendar and proper-lessons tables UNAUTHORED**,
  inheriting 1559 by omission. The Church of England serves only the post-1922
  recension of those tables (see `WAVE14_SCOPING.md` §1.1), so there is no
  allow-listed 1662-form source. **The absence must be legible to a reader**, not
  merely encoded: it is stated in `NOTICE.md`, in `SOURCES.md`, and — because a
  reader looking at the 1662 calendar will not go and read NOTICE — in a
  `<!-- VERIFY -->` note carried in provenance with `status:
  inherited-unreviewed`. A reader must never be able to mistake "inherited from
  1559" for "1662 printed the 1559 tables unchanged."
- **RULING E — the 1928 lectionary fork resolves to the ORIGINAL.** justus offers
  both the 1928 lectionary (in use 1928-1944) and the 1945 revision (*Psalms and
  Lessons for the Christian Year*, used 1945-1978). `v1928` denotes the book as
  published, so the original is transcribed. The 1945 revision is recorded as a
  known deliberate omission in `NOTICE.md` **and** in the durable backlog in
  `HANDOFF.md` §8, so it survives this wave.
- **RULING F — the Scottish line carries no tables.** The repo's Scottish branch
  is Communion-only by design (1764 is a Communion-only book; Waves 11 and 12
  both found the Scottish line carries none of their material). 1929 does print a
  Kalendar and Tables of Lessons, but authoring them at 1929 alone would create
  an orphan node with no 1637 or 1764 counterpart to diff against, and would
  leave the branch with table-governing rubrics referring to tables it does not
  have. `tables/` is therefore in `absent:` for the whole Scottish branch.

---

## 2. The file set

Family `tables/`, plus two additions to the existing `front-matter/` family.

| path | editions authored | absent | notes |
|---|---|---|---|
| `tables/calendar.md` | 1549 1552 1559 1789 1892 1928 | 1979, Scottish | 1604 & 1662 inherit (gaps) |
| `tables/proper-lessons.md` | 1549 1552 1559 1789 1892 1928 | 1979, Scottish | 1604 & 1662 inherit (gaps) |
| `tables/feasts-and-fasts.md` | 1662 1789 1892 1928 | Scottish | confirm 1549-1559 presence |
| `tables/eucharistic-lectionary.md` | 1979 | all others | **pays the Wave-10 debt** |
| `tables/daily-office-lectionary.md` | 1979 | all others | **pays the Wave-10 debt** |
| `front-matter/order-how-psalter-appointed.md` | 1549 1552 1559 1789 1892 1928 1979 | Scottish | 1662 inherits (post-1922 source) |
| `front-matter/order-how-rest-of-scripture.md` | 1549 1552 1559 1789 1892 1928 1979 | Scottish | 1662 inherits (post-1922 source) |

---

## 3. Row schema — normalized long-form (spec §10)

One entry per line, stable column order, ` | ` separated, liturgical-calendar
row order. Labels are part of the line so a column is self-identifying and a
changed cell is a one-line diff.

    ## January
    January 2 | b | Morning 1: Genesis 1 | Morning 2: Matthew 1 | Evening 1: Genesis 2 | Evening 2: Romans 1

    ## Proper Lessons for Sundays
    Advent 1 | Morning 1: Isaiah 1 | Morning 2: Luke 1 to v. 39 | Evening 1: Isaiah 2 | Evening 2: Romans 10

    ## Year A
    Advent 3 | Psalm 146 or 146:4-9 | Isaiah 35:1-10 | James 5:7-10 | Matthew 11:2-11

    ## Year One / Week of 1 Advent
    Sunday | Morning Psalms: 146, 147 | Evening Psalms: 111, 112, 113 | Isaiah 1:1-9 | 2 Peter 3:1-10 | Matthew 25:1-13

### 3.1 THE TRAILING-PERIOD TRAP (measured, not theoretical)

`sentence_split.py` splits on `[.?!]` + whitespace + any non-space. A cell ending
in a period therefore **breaks the row in half**:

    in : January 2 | b | Morning 1: Gen. 1. | Morning 2: Matt. 1 | ...
    out: January 2 | b | Morning 1: Gen. 1.
         | Morning 2: Matt. 1 | ...

So **every citation must be emitted without a trailing period**, which the
canonicalizer guarantees. Rows written this way are verified idempotent under
`sentence_split.py --stdin`.

### 3.2 Citations: `w14_cite.py`, extending `w10_cite.py`

`w10_cite.canonical()` handles `Book Chapter[:verse]` and **raises** on anything
else — the loud-stop property we want. But the calendar and lectionary print
partial-chapter extents Wave 10 never met (`Gen. 9 to v. 20`, `Eze. 20 v. 27`,
`Mal. 3 & 4`, `Luke 4 v.14 to 33`, `Jude.`). `w14_cite.py` imports
`w10_cite.BOOKS` and adds extent handling; it does **not** modify `w10_cite`, so
Wave 10 cannot regress.

Rules: canonicalize the book name and convert roman chapter numerals to arabic;
**preserve the printed extent verbatim** (normalized only for whitespace) rather
than expanding it — the extent is precisely where revision shows, so
`Gen. 9 to v. 20` becomes `Genesis 9 to v. 20`, never `Genesis 9:1-20`, which
would invent a verse the book does not print. Strip trailing periods. An
unrecognized book still raises.

Known OCR defect in the 1789 page: lowercase `l` for the digit `1`
(`l Kings 8`, `l5 to v.19`). Corrected with a `<!-- VERIFY -->` each.

---

## 4. The parser gate — assert row counts, always

The justus table pages **emit each table COLUMN as one `<td>`**, entries
separated by `<br>`; a row is recovered by zipping columns by index. Measured on
1789 January: seven cells of 32/32/27/32/32/32/32 entries.

1. **Every zipped column must have an identical entry count, or the parser
   ABORTS.** This is the wave's primary correctness gate and the cheapest
   detector for the archetypal silent loss (a table quietly losing three rows).
2. **Per-table row counts are asserted per edition in the audit gate**: January
   yields 31 rows, February 29, and so on. A short count is a finding, not a diff.
3. **The holy-day column is NOT index-zippable** and must never be treated as if
   it were. Its entries wrap across `<br>` (`Circumci-` / `sion.`) and trailing
   blanks are omitted, so it runs short. It IS positionally aligned — Epiphany
   lands on slot 6, Conversion of St. Paul on slot 25, both correct — so
   continuation fragments are rejoined and the result is then **gated against the
   edition's own Table of Feasts**: the set of holy-day NAMES recovered from the
   calendar must equal the set the Table of Feasts prints. Names come from one
   table, dates from the other, and agreement validates the join. Disagreement
   aborts.

Run BOTH gates (`w14_fidelity.py`, `w14_audit.py`) every pass, and re-run over
EVERYTHING after any parser fix — per `AUDIT_METHOD.md`, fidelity is structurally
blind to loss.

---

## 5. 1979 e-text dropouts — flag, never reconstruct

`bcplectn.txt` is missing pages 889, 899 and 909 with their content. Confirmed
losses: the `<Year A>` heading, *Concerning the Lectionary*'s tail, Year A Advent
1-2; Year A Proper 19's citation line (truncated mid-word, `thew 21:33-43`) and
Propers 20-22; a Year B Propers 11-14 band; and gaps at Year One Propers 11 & 24
and Year Two Proper 13. Each is carried as a `<!-- VERIFY -->` on its own line
with the doubtful reading first in single quotes. **Nothing is reconstructed** —
the Wave-10 precedent for the truncated 1979 collects.
