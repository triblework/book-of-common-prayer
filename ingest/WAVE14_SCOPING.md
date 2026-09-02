# Wave 14 — Lectionary & calendar tables: source survey and scoping options

Status: **survey complete, rulings PENDING.** Written 2026-09-02 before any build.
Read with `AUDIT_METHOD.md` and the Wave-10 Decision-C block in `HANDOFF.md`.

---

## 0. Headline finding — the Wave-10 debt IS payable

The brief flagged a risk that the 1979 three-year lectionary might not exist in the
public-domain e-text at all. **It does.** The earlier scan looked at the wrong file
list: the `ASCII_1979.htm` index publishes **eleven** parts, and the eleventh is

    BCPLECTN.TXT -- Lectionary (p. 887 - 1001)

which no prior wave has ever fetched (9 of the 11 parts are in `scrape-cache`; this
was not one of them). Fetched 2026-09-02: 115,811 bytes, 4,367 lines, containing
BOTH 1979 lectionaries in full:

- **The Lectionary** (pp. 888-931) — the three-year eucharistic lectionary, with
  `<Year B>` / `<Year C>` section markers and ~171 occasion entries, plus Holy Days,
  the Common of Saints, and Various Occasions.
- **The Daily Office Lectionary** (pp. 934-1001) — the two-year cycle,
  `<Year One>` / `<Year Two>`, ~784 day entries across 49+ named weeks.

So Wave 10's Decision-C(4) deferral can be discharged in full, and the 1979 propers'
reading sets become representable for the first time.

### 0.1 …but the e-text has real page dropouts (record, do not reconstruct)

Page markers present run 888-936 then jump to 996. Three pages are missing **with
their content**, not merely their marker:

| lost page | consequence |
|---|---|
| 889 | the `<Year A>` heading, the tail of *Concerning the Lectionary*, and Year A's **First and Second Sundays of Advent** |
| 899 | the tail of Year A **Proper 19** (its citation line begins mid-word, `thew 21:33-43`) and **Propers 20, 21, 22** entirely |
| 909 | the Year B **Propers 11-14** band |

The Year C band around Propers 10-13 shows the same shape and needs the same check at
build time. `Year One` (Propers 11, 24) and `Year Two` (Proper 13) have gaps in the
Daily Office Lectionary too.

This is the Wave-10 precedent exactly ("1979 e-text dropouts — three collects
truncated in the 1993 keying... flagged inline, nothing reconstructed"). **Flag each
inline with `<!-- VERIFY -->`, reconstruct nothing.** The row-count gate below is what
turns these from silent loss into a loud stop.

---

## 1. Source survey — what each edition actually prints, and whether we can get it

Confirmed against each source's own index, 2026-09-02. `HTML` = clean HTML we can
parse; `PDF` = PDF with an extractable text layer; `--` = the book does not have it;
`GAP` = the book has it but no allow-listed source serves it.

| table | 1549 | 1552 | 1559 | 1604 | 1662 | 1637 | 1764 | 1929 | 1789 | 1892 | 1928 | 1979 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| The Kalendar (day / Sunday letter / holy day) + its daily lesson columns | HTML | HTML | HTML | GAP | **GAP** | -- | -- | HTML | HTML | HTML | PDF | -- |
| Proper Lessons for Sundays & Holy Days | HTML | HTML | HTML | GAP | **GAP** | -- | -- | HTML | HTML | HTML | PDF | -- |
| Order how the Psalter is appointed to be read | HTML | HTML | HTML | GAP | (post-1922) | HTML | -- | HTML | HTML | HTML | PDF | HTML |
| Order how the rest of Holy Scripture is appointed | HTML | HTML | HTML | GAP | (post-1922) | HTML | -- | HTML | HTML | HTML | PDF | HTML |
| Tables and Rules for the moveable feasts / Table of Feasts / Table of Fasts & Vigils | ? | ? | ? | GAP | PDF | -- | -- | HTML | HTML | HTML | PDF | txt |
| Golden number / Sunday letter / epact / Table to find Easter / Almanack | HTML | HTML | HTML | GAP | PDF | -- | -- | HTML | HTML | HTML | PDF | txt |
| Table of Kindred and Affinity | -- | -- | -- | -- | HTML | -- | -- | HTML | -- | -- | -- | -- |
| **Three-year eucharistic lectionary** | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | **txt** |
| **Two-year Daily Office Lectionary** | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | **txt** |

Source URLs, all verified to resolve:

- **1549** `1549/Kalendar_1549.htm` · **1552** `1552/Kalendar_1552.htm`
  (anchors `Psalms`, `Rest of Scripture`, `Proper Psalms&Lessons`, `Almanac`,
  `Kalendar`) · **1559** `1559/Kalendar_1559.htm` (same five anchors).
- **1789** `1789/FrontMatter_1789.htm` (`#TABLES of LESSONS`, `#Calendar`,
  `#How the Psalter`, `#How the rest of the Holy Scripture`) and
  `1789/Tables&Rules_1789.htm` (`#Holy Days`).
- **1892** `1892/Lectionary_1892.htm` — **its own page, not shared with 1789**
  (the Wave-12 paired-column trap does not apply here). Anchors `Lent`,
  `Calendar`, `Tables`, `Tables_HolyDays`. Carries three tables 1789 lacks:
  Lessons for the Forty Days of Lent, the Rogation Days, and the Ember Days.
- **1928** `1928/Calendar&Tables_1928.pdf` — 6 pages, **clean text layer** (unlike
  the Wave-9 Propers PDF: no garbled font layer, `pypdf` extracts readable rows).
- **1929 Scottish** `Scotland/Scot_Front_Matter.htm#Kalendar` and
  `Scotland/Scot_Tables_Rules.htm`.
- **1637 Scottish** `Scotland/front_matter_1637.htm` — carries the two "Order how…"
  rubric sections and the *Table and Kalendar* heading, but **the tables themselves
  are not on the page**.
- **1979** `bcplectn.txt` (both lectionaries) and `bcpprayr.txt` (Easter tables).
- **1662** Church of England, fifteen PDFs linked from the `tables` page.

### 1.1 The 1662 problem — the flagship line's biggest constraint

**The Church of England site does not serve the 1662 calendar or lectionary in its
1662 form.** It serves the currently authorized recension:

- `bcp-the-calendar.pdf` prints verse-level citations (`Genesis 1.1-19`,
  `Matthew 1.18 - 25`) — the revised tables, not 1662's whole-chapter lessons.
- `1-table-proper-lessons.pdf` prints `or` alternatives (`Isaiah 2 or Isaiah 4.2-6`)
  — likewise revised.
- Three PDFs are explicitly the **Revised Tables of Lessons Measure, 1922** and its
  tables. These are a 20th-century work, out of scope on spec §8 grounds
  independently of fidelity.
- Even the two "Order how…" HTML pages are the post-1922 text (the Scripture page
  refers to "a Sunday for which alternative Second Lessons are specially appointed
  in the Table"; `rules-order-service` speaks of Passion Sunday, "Easter 1", and
  Harvest Thanksgiving — none of which is 1662 language).

What **is** 1662-form on that site: `4-tables-and-rules.pdf` (Rules to know when the
Moveable Feasts begin, Table of Feasts) and `5-table-vigils-fasts.pdf`, both with
clean text layers and wording matching the received 1662 text.

en.wikisource.org (spec-preapproved for PD cross-checks) was checked: it carries a
**1892** BCP transcription but no 1662 one. So there is no easy second source.

**Consequence:** 1662 can author the feast/fast tables but must leave the calendar
and proper-lessons tables **unauthored**, inheriting 1559 by omission with provenance
`inherited-unreviewed` and a recorded gap. This is the Wave-10 precedent for the
1604 propers, applied again.

### 1.2 The 1928 lectionary forked mid-edition

The justus 1928 index offers the lectionary **twice**: the original (in use
1928-1944) and the 1945 revision (`Psalms and Lessons for the Christian Year`, used
1945-1978). One edition node cannot carry both. Recommendation: transcribe the
**original 1928 tables** — that is the book our `v1928` tag denotes — and record the
1945 revision as a known, deliberate omission in `NOTICE.md`.

---

## 2. The structural discriminator (per AUDIT_METHOD §"prefer a structural…")

The justus table pages **emit each table COLUMN as a single `<td>`**, with the
column's entries separated by `<br>`. A row is recovered by *zipping columns by
index*. Measured on `1789 FrontMatter` January:

    <tr> ... 7 <td>: day(32) letter(32) holyday(27) M1(32) M2(32) E1(32) E2(32)

The six numeric/lesson columns zip perfectly — `&nbsp;` is used as an explicit
alignment placeholder, so blank days keep their slot. **The holy-day column does
not** (27 vs 32): saint names wrap across `<br>` ("Circumci-" / "sion.") and blanks
collapse differently. That column must be reconstructed by a separate rule or
recorded as a gap; it must never be zipped by index.

**Therefore the mandatory gate for this wave** (the brief's "assert ROW COUNTS"):
the parser asserts that every zipped column of a table has an identical entry count
and **aborts** otherwise, and the audit gate asserts per-table row counts per
edition (a January table that yields 30 rows instead of 31 is a loud stop, not a
diff). This is the cheapest possible detector for the archetypal silent loss.

The 1979 e-text needs no zipping — it is line-oriented and regular:

    Sunday:  146, 147; 111, 112, 113
      Isa. 1:1-9; 2 Pet. 3:1-10; Matt. 25:1-13

---

## 3. Cache hygiene finding (independent of this wave)

`scrape-cache` still holds **71 files containing U+FFFD**, damage from the charset
bug fixed in Wave 11. The Wave-11 repair pass re-fetched only the entries whose lost
characters were known to matter (the 1549 æ ligatures); the rest were left. Verified
on `Scotland/front_matter_1637.htm`: the cached copy has 5 replacement characters,
`fetch(..., force=True)` returns 0. Published output was audited clean, so this is a
**source-cache hazard, not a live text defect** — but any new ingest reading one of
these pages inherits the damage silently. Recommend a bulk `force=True` re-fetch of
all 71 before this wave reads anything.
