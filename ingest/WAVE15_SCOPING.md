# Wave 15 — the 1928 lectionary & calendar tables: source survey and scoping options

Status: **survey complete, rulings PENDING.** Written 2026-09-11 before any build.
Read with `WAVE14_GUIDE.md` (row schema, rulings A-F), `WAVE14_SCOPING.md` and
`AUDIT_METHOD.md`.

---

## 0. Headline findings

1. **`Calendar&Tables_1928.pdf` prints no lessons and no psalms.** Its Calendar
   is day / Sunday letter / holy day only (golden numbers against 21 March -
   18 April). The 1928 book moved the daily lessons OUT of the Kalendar into a
   church-year table. SOURCES.md's premise, that this PDF is the source for the
   1928 Kalendar, Proper Lessons, Feasts and Fasts and Proper Psalms, is half
   wrong: it serves the Kalendar and the Feasts and Fasts only.
2. **The 1928 lectionary is a separate file, `1928/Lectionary_1928.pdf`** (9
   pages; same Corel/WordPerfect producer; the justus index links it from the
   "(1928 Version)" rows, and `Lectionary_1945.pdf` from the "(1945 Version)"
   rows). It carries the Proper Psalms, the Selections, the Sunday psalm table,
   the three lesson tables, and the two table-governing rubrics.
3. **A live false `absent:` at 1892, inherited by 1928.** Wave 14 put both
   "Order how..." rubrics in 1892's `absent:` on the grounds that 1892 and 1928
   "merged them into Concerning the Service of the Church". The evidence was the
   books' TABLE OF CONTENTS entry ("Concerning the Service of the Church, with
   the Order how the Psalter and the rest of the Holy Scripture is appointed to
   be read"). The pages print them as titled sections:
   - 1892 `Front_Matter_1892.htm`: `CONCERNING THE SERVICE OF THE CHURCH.`, then
     `THE ORDER HOW THE PSALTER IS APPOINTED TO BE READ.`, then (after the Proper
     Psalms table) `THE ORDER HOW THE REST OF THE HOLY SCRIPTURE IS APPOINTED TO
     BE READ.`
   - 1928 `Lectionary_1928.pdf` p.1 and p.3: `THE USE OF THE PSALTER.` (a renamed
     successor) and `THE ORDER HOW THE REST OF THE HOLY SCRIPTURE IS APPOINTED
     TO BE READ.` (same title), under the running head "Concerning the Service
     of the Church".
4. **Related, older:** 1892 and 1928 print "Concerning the Service of the
   Church" (the rules text 1979's `concerning-the-service.md` descends from),
   but `front-matter/concerning-the-service` is `absent:` from 1789 through
   1928. That file's history is the 1549 Preface (Wave 9), so this is a slot
   identity question, not only a presence fix.

## 1. Is it the 1945 revision?

Not on the evidence available, but not proven either.

- The Calendar & Tables PDF carries no lectionary, so it cannot be the 1945
  *Psalms and Lessons for the Christian Year*. justus names it `_1928` and
  offers only one Calendar/Tables file, linked from both sets of rows.
- `Lectionary_1928.pdf` self-identifies as the original: "A TABLE OF LESSONS FOR
  THE CHRISTIAN YEAR" with separate psalm tables, not the 1945 combined
  "Psalms and Lessons" title.
- What the text layers cannot show is which PRINTING Wohlers keyed the Calendar
  and Tables from. The decisive witness is justus `1928/BCP1929.pdf` ("The
  original 1928 printing as PDF graphics", HEAD: 42,365,481 bytes), book pages
  xlvi-lii. Not downloaded; needs the maintainer's go-ahead.

## 2. Inventory

### 2.1 `Calendar&Tables_1928.pdf` (6 landscape sheets, two book pages each)

| sheet | book content | rows | in scope under Wave 14 ruling B? |
|---|---|---|---|
| 1-2 | The Calendar, Jan-Dec, + a Thanksgiving Day note after December | 366 expected (Feb 29 printed with no letter); **360 extracted** | yes -> `tables/calendar.md` |
| 3 | Tables and Rules for the Movable and Immovable Feasts: Rules to know when the Movable Feasts begin; A Table of Feasts (2 columns); A Table of Fasts; Other Days of Fasting (I-III); Days of Solemn Supplication; **Tables of Precedence** (two tables + rules); A Table of occasions with a proper Collect not in the Calendar (3 columns) | ~75 entries | yes -> `tables/feasts-and-fasts.md` |
| 4 | To find the date of Easter Day (prose); Table to find the Dominical Letter; Table to find Easter Day 1786-2013 (part) | grids | prose per the 1892 precedent; grids OUT |
| 5 | Table to find Easter (cont.); Table of the Movable Feasts by Easter date | grids | OUT (arithmetic) |
| 6 | General Tables I and II (Dominical letter, golden numbers) + prose | grids | OUT (arithmetic) |

**Calendar text-layer defects (measured by the Sunday-letter cycle and day
completeness, not eyeballed):**

- **6 rows missing outright:** 15 April, 15 May, 15 June, 11 July, 11 August,
  11 September. In April the orphaned golden number of the lost row is glued to
  16 April (`9 16 A`).
- **3 wrong letters:** 11 February and 11 March print `d` (the cycle requires
  `g`); 1 October prints `d` (requires `A`).
- **All Saints is keyed against 1 October**, not 1 November, and November 1
  has no entry. It looks like a copied row.
- Case / spacing: 31 January and 9 May print `C`; `18g`, `18b`, `5 g5 c`.
- Independence Day (4 July) is in the Calendar but not in the Table of Feasts,
  so Wave 14's names gate needs a stated exemption.

### 2.2 `Lectionary_1928.pdf` (9 landscape sheets)

| sheet | book content | rows (approx.) | target path |
|---|---|---|---|
| 1 | Concerning the Service of the Church (prose) | 3 paras | see finding 4 |
| 1 | THE USE OF THE PSALTER (rubric) | 4 paras | `front-matter/order-how-psalter-appointed.md` (rename) |
| 1-2 | Proper Psalms for Seasons and Days + two NOTEs | 22 | `tables/proper-psalms.md` |
| 2 | Selections of Psalms I-XX (two columns, wrapped) | 20 | `psalter/selections.md` (closes a recorded gap) |
| 2-3 | A Table of Psalms for the Sundays of the Church Year | 57 | `tables/proper-psalms.md`, own `##` |
| 3 | Psalms for Special Occasions | 10 | `tables/proper-psalms.md`, own `##` |
| 3 | THE ORDER HOW THE REST OF THE HOLY SCRIPTURE IS APPOINTED TO BE READ | 6 paras | `front-matter/order-how-rest-of-scripture.md` |
| 3 | Hymns and Anthems (rubric) | 1 para | out |
| 3-8 | **A Table of Lessons for the Christian Year** (Sundays AND weekdays, Advent 1 -> Sunday next before Advent; Ember-day optional lessons; fixed dates 29 Dec - 5 Jan) | ~360-400 rows x 4 citations | `tables/proper-lessons.md` |
| 9 | A Table of Lessons for the Fixed Holy Days not in the above (Eve / Morning / Evening) | ~25 | `tables/proper-lessons.md` |
| 9 | A Table of Lessons for Special Occasions | ~10 | `tables/proper-lessons.md` |

**Hazards:** two book pages per sheet (plain mode keeps left-then-right; layout
mode reads across the gutter); day labels wrap (`FIRST SUNDAY` / `IN ADVENT`);
citations wrap mid-extent (`Isa. 60:1-11,` / `18-end`); ordinal suffixes of the
right-hand page leak onto left-hand citations (`Matt. 19:1-9th`, `James 3th`);
footnote markers `*` (optional Ember lessons) and `†` (Christmas Eve); and
**unproofread OCR throughout** (justus: "has not been proofread and undoubtedly
will contain errors"): `Lake 2:22-40`, `Joke 13:10-35`, `I Es.. 15`,
`Isa. 401-11`, `Ezek. 371-14`, `Wisdom 31-9`, `I Kgs. 18:1-Is`, `II Cur. 5`,
`v. l2`, `Mark 12. -v. 13`. Several are ambiguous without a page image.

## 3. What the diffs will and will not mean

- `calendar.md`: v1892 is the INHERITED 1789 table (1892's Kalendar is a
  recorded gap), so `git diff v1892 v1928` compares 1928 with 1789. The lesson
  columns vanishing is right in direction (1892's own TOC reads "The Calendar,
  with Tables of Lessons"), but holy-day changes between 1789 and 1892 would be
  attributed to 1928. `git diff v1928 v1979` is genuine and clean: same three
  fields per day.
- `feasts-and-fasts.md`, `proper-psalms.md`: v1892 is authored, so both diffs
  are genuine. proper-psalms is `absent:` at 1979 (true).
- `selections.md`: v1892 is the inherited 1789 list (recorded gap), so
  `v1892->v1928` compares 1928 with 1789.
- `proper-lessons.md`: v1892 is authored (Sundays, Holy-days, Lent days). The
  1928 Christian-Year table succeeds both the Sundays and the Lent-days tables.
  Genuine diff, but a noisy one: weekday rows interleave the Sunday rows.
  Absent at 1979 (Ruling C).
