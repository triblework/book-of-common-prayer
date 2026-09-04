# SOURCES — per-edition provenance

For every edition this file records where the text came from, when it was
retrieved, and any omissions or uncertain passages. Copyright status is in
`NOTICE.md`.

**Primary source:** Charles Wohlers' collection at the *Society of Archbishop
Justus*, <http://justus.anglican.org/resources/bcp/>. Retrieval is performed by
`tools/scrape.py`, which caches responses under `scrape-cache/` (gitignored),
rate-limits requests (≥1s apart), honors `robots.txt`, and refuses any host not
on its allow-list. All retrievals below were made **2026-08-10**.

## Current transcription scope (read this first)

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

---

## English line (`main`)

| Edition | Source URL | Notes |
|---------|------------|-------|
| 1549 | <http://justus.anglican.org/resources/bcp/1549/Matins_1549.htm> | Matins opens directly with the Lord's Prayer. |
| 1552 | <http://justus.anglican.org/resources/bcp/1552/MP_1552.htm> | Adds the penitential introduction. |
| 1559 | <http://justus.anglican.org/resources/bcp/1559/MP_1559.htm> | Restores the Ornaments Rubric. The justus page also annotates the 1604 readings inline. |
| 1604 | derived from the 1559 justus apparatus | The Jacobean changes to the MP opening (rubric "saide"→"made", "or remission of sins", added "Priest." label, Gloria → "&c.") are documented inline on the 1559 page. |
| 1662 | <https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/order-morning-prayer> | See the 1662 sourcing note below. `BCP 1662`. |

### 1662 sourcing note
justus serves the 1662 only as the Baskerville 1762 **PDF** (`.../1662/mp.pdf`),
whose ligatures (`st`, `ct`) drop out of every text-layer extractor tried
(`pypdf`, `pdfminer.six`), corrupting words such as *most*, *against*,
*Minister*. The clean text was therefore taken from the **Church of England's
own website** (the authoritative publisher of the 1662; added to the scraper
allow-list for this purpose) and **cross-checked** against the Baskerville PDF.
The CoE web page interleaves a modern rubric ("If no priest be present…") that
is **not** part of the 1662 book; it was excluded. Reproduced with the required
Crown-copyright acknowledgment: **BCP 1662** (see `NOTICE.md`).

## Scottish line (`scottish`) — forks from `v1604`

| Edition | Source URL | Notes |
|---------|------------|-------|
| 1637 | <http://justus.anglican.org/resources/bcp/Scotland/MP_1637.htm> | "Laud's Liturgy"; Morning Prayer. |
| 1764 | <http://justus.anglican.org/resources/bcp/Scotland/Scot1764_Communion.htm> | Communion Office only ("Wee Bookie"); Morning Prayer is **absent** on this commit by design. Transcribed: exhortation + offertory. |
| 1929 | <http://justus.anglican.org/resources/bcp/Scotland/Scot_Scottish_Communion.htm> | Represented by the Scottish Liturgy (Holy Communion), updating the same `holy-communion.md`. The justus full-book PDF (`Scottish_BCP1929.pdf`) is an image/OCR scan and was **not** used for text. |

## American line (`american`) — forks from `v1662`

| Edition | Source URL | Notes |
|---------|------------|-------|
| 1789 | <http://justus.anglican.org/resources/bcp/1789/MP_1789.htm> | First American book; Daily Morning Prayer. |
| 1892 | <http://justus.anglican.org/resources/bcp/1892/MP_1892.htm> | Expanded opening sentences + liberalizing rubrics. |
| 1928 | <http://justus.anglican.org/resources/bcp/1928/MP.htm> | Full Daily Morning Prayer from the justus Satucket clean HTML (spec §4.1); gap closed. |
| 1979 | <http://justus.anglican.org/resources/bcp/bcpoffce.txt> | Public-domain ASCII e-text (spec §4.2); Rite I as the office body, Rite II as a separate `## Rite Two` section. Mechanically reflowed via `scrape.py --text`; gap closed. |

---

## Omissions

- The Psalter and full lectionary/calendar tables are **stretch scope** (brief
  §13); their files are absent rather than stubbed.
- The proposed English 1928 "Deposited Book" is omitted (no confirmed clean PD
  source; brief §1).
- Services absent from an edition are represented by the **absence** of the file
  at that commit (e.g. Morning Prayer at Scottish `v1764`), so the removal shows
  cleanly in the diff.
- American `v1928` and `v1979` Daily Office text: see the table above.

## Scope of the Litany files

The `the-litany/litany.md` file for each edition covers the **Litany proper** —
invocations, deprecations, obsecrations, intercessions, Agnus Dei/Kyrie, the
Lord's Prayer, the concluding suffrages and collects, the Prayer of St.
Chrysostom, and the Grace (where the edition prints them). The **occasional
prayers and thanksgivings** (For rain / fair weather / dearth / war / plague,
etc.) and the **appended state prayers** (King's/Queen's Majesty, Royal-Family
collect, Clergy, Ember) that some editions print after the Litany are handled in
a later "Prayers and Thanksgivings" pass, not here — matching the Church of
England 1662 Litany, which ends at the Grace. The Scottish 1929 book's Litany is
not yet transcribed (the Scottish line currently centres the Communion office at
1764/1929); `justus`'s `Scotland/Scot_Litany.htm` in fact serves the 1929 book,
while the 1637 Litany is at `Scotland/Litany_1637.htm`.

### Prayers and Thanksgivings upon several Occasions (Wave 11)

One file per prayer under `prayers-and-thanksgivings/`, for every edition that
carries the block. 1552–1637 print these prayers **inline after the Litany
suffrages**; 1662 and the American line print them as a separate section. The
repo gives them their own family throughout so each prayer has a single stable
path and its own per-edition diff; the earlier books' inline placement is a
book-order fact recorded in `NOTICE.md`, not a text difference.

Two relocations are recorded rather than shown as deletions: the **state
prayers** (sovereign, royal family, clergy) move from this block into Morning
and Evening Prayer at 1662, and **A Prayer for all Conditions of Men** and the
**General Thanksgiving** move into Morning and Evening Prayer in the American
line from 1789. Both texts continue in `daily-office/`.

Excluded from this wave, each its own section of the book: the 1662 *Forms of
Prayer to be used at Sea*, the 1892/1928 *Penitential Office*, *Family Prayer*,
and the 1789 *Prayer and Thanksgiving to Almighty God*.

The 1789 *Prayer to be used at the Meetings of Convention* is **not** carried at
1789: the source page's own apparatus records it as added in 1845.

### The four deferred sections (Wave 12)

Four smaller sections of the book, each excluded from Wave 11 as its own wave:
the *Forms of Prayer to be used at Sea* (1662, 1789, 1892), *A Penitential
Office for Ash-Wednesday* (1892, 1928), *Forms of Prayer to be used in Families*
(1789, inherited 1892, expanded 1928), and *A Form of Prayer and Thanksgiving to
Almighty God* (1789, 1892). Each is one file under `occasional-offices/` with
`##` anchors, like the other occasional offices.

**Psalms in the Sea forms are carried as a pointer, not transcribed.** Those
pages print whole psalms (97 verse blocks at 1662 alone); the Psalter is a
separate wave, so each run collapses to a line naming the psalm and its verse
count. The anchor is identical whether it later holds a pointer or the full
text, so deepening throws nothing away. **Psalm 51 in the Penitential Office is
carried in full**, because it is the structural core of that service and the
already-published Commination sets that precedent for the same psalm on the same
day.

**The Penitential Office is not the Commination.** The American line drops the
Commination at 1789 and prints a Penitential Office for the same day from 1892.
It keeps the occasion and Psalm 51 but carries none of the Commination's eight
denounced curses and drops the name. It therefore has its own file, and the
relationship between them is recorded in `NOTICE.md` rather than asserted as a
diff on one path.

Two justus pages print **1789 and 1892 side by side** in labelled parallel
columns. Each edition's cell is built from its own column; the texts genuinely
differ, so 1892 is not merely the 1789 page reprinted.

## Uncertain passages (`<!-- VERIFY -->`)

Each is flagged inline in the text and should be checked against a page scan.

| File / edition | Reading in source | Note |
|----------------|-------------------|------|
| 1552 Morning Prayer | `Psalm ii.` | Verse is Psalm 51:3; likely a `li`→`ii` printer error. |
| 1552 Morning Prayer | `Jerem. ii.` | Verse is Jeremiah 10:24; 1559 carries the same reading. |
| 1559 Morning Prayer | `Lord, make haste to helpe us` | 1552 reads `O Lord`; the missing `O` may be a transcription slip. |
| 1637 (Scottish) Morning Prayer | `Ps. 28` | Sentence is Proverbs 28:13. |
| 1637 (Scottish) Morning Prayer | `missing page` | justus notes a missing page from the Te Deum through the rubric before the Collects; that span is a reconstructed text with re-ordered canticle labels — confirm against a 1637 scan. |
| 1764 (Scottish) Communion | `Matth. vi. 9. 20` | Passage is Matthew 6:19-20; `9` likely for `19`. |
| 1929 (Scottish) Communion | `Acts 20. 85` | Verse is Acts 20:35; `85` likely a scan error. |
| 1789 (American) Morning Prayer | several roman-numeral citations | The justus 1789 page had OCR damage in citations (e.g. `Psalm ii 17` for Psalm 51:17); read against the parallel 1662 sentences. |
| 1662 Morning Prayer (Prayer for the King's Majesty) | `King CHARLES` | The CoE source serves the reigning monarch (Charles III); the 1662 book as first printed named the then-sovereign (Charles II). Reign-dependent; reconcile against a dated 1662 scan. |
| 1662 Morning Prayer (Prayer for the Royal Family) | `Queen Camilla, William Prince of Wales, the Princess of Wales` | The CoE source serves the current Royal Family; the 1662 book named the then-Royal Family. Reign-dependent; reconcile against a dated 1662 scan. |
| 1552 Evening Prayer | `Lord, make haste to helpe us` | 1552 Morning Prayer has `O Lord`; the missing `O` may be a transcription slip. |
| 1552 Evening Prayer | `all that them is ... they that dwel therm` | Cantate Domino; justus prints `them is`/`therm`, both probable OCR for `therein`; normalized to `therein`. |
| 1552 Evening Prayer | `Deus misereatur. Ps. lxvii.` | The justus 1552 EP page names this alternative to the Nunc Dimittis by title only; the psalm body is not printed on that page. |
| 1559 / 1604 Evening Prayer | `And my sprit ... the loweliries of his handmaiden` | Magnificat; justus prints OCR forms `sprit` (spirit) and `loweliries` (lowelines); rendered as the intended words. |
| 1637 (Scottish) Evening Prayer | `Lord make haste to help us` | 1637 Morning Prayer has `O Lord`; the missing `O` may be a transcription slip. |
| 1637 (Scottish) Evening Prayer | `Cantate domino. Ps. 98 / Nunc dimittis / Luke 2. 29. / Deus misereatur. Ps. 67.` | The justus 1637 EP canticle labels float to the wrong positions; the bodies run Magnificat, Cantate Domino, Nunc Dimittis, Deus Misereatur and the labels are re-ordered to match. |
| 1789 (American) Evening Prayer | `Psalm ii. 9` and other citations | Same OCR citation/word damage as 1789 MP (e.g. `Psalm ii. 9` for 51:9, `St. Luke vx. 18, 19` for xv, `walk m his laws`); read against the parallel 1789 MP / 1662. |
| 1789 (American) Evening Prayer | `O God, make speed to save us / O Lord, make haste to help us` | The justus 1789 EP page prints only `O Lord, open thou our lips` then the Gloria; this pair (present at 1789 MP) is absent, as on the 1892/1928 EP pages; omitted following the source. |
| 1892 / 1928 (American) Evening Prayer | `O God, make speed to save us / O Lord, make haste to help us` | The justus 1892 and 1928 EP pages likewise omit this pair (present at their Morning Prayer); omitted following the source; confirm against a scan. |
| 1928 (American) Evening Prayer | `St. Mark xiii. 35, 36.` | Source prints `St. Mark xiii, 35, 36.` with a comma after `xiii`; normalized to a period for citation consistency. |
| 1928 (American) Evening Prayer | `Thy will be done, On earth as it is in heaven.` | The 1928 EP page reads thus, diverging from the same-edition 1928 Morning Prayer (`Thy will be done on earth, As it is in heaven.`); transcribed as the EP source prints it. |
| 1604 Litany | `thy servaunt JAMES our most gracious king and governour` | Derived from the justus 1559 apparatus (which documents the JAMES name and the added Royal-Family petition); the her->his pronouns follow from the male sovereign. |
| 1662 Litany (King) | `CHARLES, our most gracious King and Governor` | The CoE source names the reigning monarch (Charles III); the 1662 book named the then-sovereign (Charles II). Reign-dependent; reconcile against a dated 1662 scan. |
| 1637 (Scottish) Litany | `The Litany` | The source page body prints no standalone heading (it opens at the rubric 'Here followeth the Letany...'); the title was taken from the page's HTML title/index label. Confirm the printed heading against a 1637 scan. |
| 1637 (Scottish) Litany | `honor` | The source prints `honor` (no `u`) in one petition though `honour` elsewhere; possible justus slip for 1637 `honour`. |
| 1637 (Scottish) Litany | `Favorably` | The source prints `Favorably` (no `u`); the 1549/1552 parallel reads `Favourably`; possible justus slip. |
| 1789 / 1892 (American) Litany | `in the day of judgment` | The justus 1789 page prints `in the day our judgment`; `our` is an OCR slip for `of` (cf. 1662 `in the day of judgement`). |
| 1789 / 1892 (American) Litany | `whensoever they oppress us; and graciously hear us` | The justus page prints `oppress us . and graciously` (damaged semicolon); read against the 1662 parallel. |
| 1789 / 1892 (American) Litany | `Fulfill` | The justus page prints `Fulfill`; the same-edition 1789 Evening Prayer prints `Fulfil`; internal commas restored from the parallel. |
| 1892 (American) Litany | `That it may please thee to send forth laborers into thy harvest` | The justus 1789 page marks this petition `added in the 1892 BCP`; the only indicated 1892 difference. |
| 1549 Communion | `The Epistle written in the Chapiter of to the` | 1549 prints a fill-in formula with blank slots for the proper Epistle's book/chapter/verse; the blanks did not survive the HTML capture. |
| 1552 Communion | `God of goddes` | Nicene Creed; several printings read `God of God`. |
| 1552 Communion | `Job iiii.` | The Tobit offertory sentences are cited `Job iiii.` (a printer error for Tobit 4). |
| 1559 Communion | `as sane as he conveniently may` | Opening admission rubric; `sane` likely a printer error for `soone`. |
| 1559 Communion | `Psal. lxi.` | Citation for `Blessed be the man…`; printed on the wrong line, likely a transposition of `Psal. xli.` (Psalm 41). |
| 1604 Communion | `JAMES our King and governoure` | Derived from the justus 1559 apparatus (Jacobean monarch change Elizabeth→JAMES); no separate 1604 Communion page survives. |
| 1662 Communion (Collect for the King) | `CHARLES our King` | The CoE source serves the reigning monarch (Charles III); the 1662 book named Charles II. Reign-dependent. |
| 1662 Communion (admission rubric) | `give an account to the Ordinary within seven days an opportunity for interview` | The CoE admission rubric adds administrative wording that reads like a modern statutory amendment; the 1662 book carried the `open and notorious evil liver` rubric. |
| 1637 (Scottish) Communion | `Matth. 11. 28` | The Comfortable Words marginal citations are set in a side column and were interleaved out of order by the HTML capture; realigned to their sentences. |
| 1764 (Scottish) Communion | `holy Father` | The words `(holy Father)` are omitted on Trinity Sunday per a source footnote; retained in brackets. |
| 1764 (Scottish) Communion | `1 John ii. 12` | Last Comfortable Word; `12` likely for `1` (1 John 2:1). |
| 1789 (American) Communion | `the face of the Lord not be turned away` | The justus 1789 e-text drops `shall`; the page carries scattered OCR omissions. |
| 1892 (American) Communion | `under the direction the Minister` | A dropped `of` (`under the direction of the Minister`). |
| 1892 (American) Communion | `the flesh of Thy dear Son us Christ` | `us` appears to be a corruption of `Jesus`. |
| 1892 (American) Communion | `after the manner dissemblers with God` | A dropped `of` (`after the manner of dissemblers`). |
| 1892 / 1928 (American) Communion | `Answer` | Floating Sursum Corda / salutation speaker labels were assigned to their responses; the spoken words are unchanged. |
| 1928 (American) Communion | `alms and` | The intercession prints `[alms and]` in brackets as optional text (said only when alms are collected); kept as BCP typography. |
| 1929 (Scottish) Communion | `Elizabeth our Queen` | The justus page follows a later reprint; a 1929 book named the reigning King (George V). Reign-dependent. |
| 1549 Confirmation (The Signing with the Cross) | `heades` | source prints 'heades' with a footnote '* head in several printings'; 'heades' kept as printed; confirm against a page scan |
| 1549 Private Baptism (The Private Baptism) | `he*` | source prints 'he*' with a footnote '* they in some printings'; 'he' kept as the primary reading; confirm against a page scan |
| 1552 Confirmation (The Confirmation) | `Lard` | source prints 'Lard'; likely an OCR/scan corruption of 'Lord'; kept as printed; confirm against a page scan |
| 1552 Confirmation (The Confirmation) | `let out crye` | source prints 'let out crye'; likely 'let our crye'; kept as printed; confirm against a page scan |
| 1552 Private Baptism (The Introduction) | `shot compel` | source prints 'shot compel'; likely 'shal compel'; kept as printed; confirm against a page scan |
| 1559 Confirmation (The Preface) | `should he doen` | source prints 'should he doen'; likely 'should be doen'; kept as printed; confirm against a page scan |
| 1559 Confirmation (The Preface) | `shoulde he ministred` | source prints 'shoulde he ministred'; likely 'shoulde be ministred'; kept as printed; confirm against a page scan |
| 1559 Confirmation (The Confirmation) | `questyone` | source prints 'questyone'; likely 'questions'; kept as printed; confirm against a page scan |
| 1559 Confirmation (The Confirmation) | `bothe` | source prints 'bothe' with footnote "'bothe' removed in 1604"; kept as printed; confirm against a page scan |
| 1559 Confirmation (The Confirmation) | `prayer` | source prints 'prayer' with footnote "'prayers' in 1604"; kept as printed; confirm against a page scan |
| 1559 Confirmation (The Rubrics) | `he ordred` | source prints 'he ordred'; likely 'be ordred'; and 'sheal'; likely 'shal'; kept as printed; confirm against a page scan |
| 1559 Private Baptism (The Vows) | `ponce Pilate` | source prints 'ponce Pilate'; likely 'Poncius'/'Pontius Pilate'; kept as printed; confirm against a page scan |
| 1559 Private Baptism (The Vows) | `wet doune` | source prints 'wet doune'; likely 'went doune'; kept as printed; confirm against a page scan |
| 1559 Public Baptism (The Flood Prayer) | `thy` | source prints 'thy' ('with thy holy gost'); a footnote records 'the' in 1604 printings; kept as printed; confirm against a page scan |
| 1604 Confirmation (The Preface) | `should he doen` | source prints 'should he doen'; likely 'should be doen'; kept as printed; confirm against a page scan |
| 1604 Confirmation (The Preface) | `shoulde he ministred` | source prints 'shoulde he ministred'; likely 'shoulde be ministred'; kept as printed; confirm against a page scan |
| 1604 Confirmation (The Confirmation) | `questyone` | source prints 'questyone'; likely 'questions'; kept as printed; confirm against a page scan |
| 1604 Confirmation (The Rubrics) | `he ordred` | source prints 'he ordred'; likely 'be ordred'; and 'sheal'; likely 'shal'; kept as printed; confirm against a page scan |
| 1604 Private Baptism (The Vows) | `ponce Pilate` | source prints 'ponce Pilate'; likely 'Poncius'/'Pontius Pilate'; kept as printed; confirm against a page scan |
| 1604 Private Baptism (The Vows) | `wet doune` | source prints 'wet doune'; likely 'went doune'; kept as printed; confirm against a page scan |
| 1637 Public Baptism (The Flood Prayer) | `Sanctifie this fountain of baptisme, thou which art the Sanctifier of all things.` | source prints 'Sanctifie this fountain of baptisme, thou which art the Sanctifier of all things.' as a bracketed clause marked with an asterisk keyed to the following font-water rubric; the enclosing brackets are source (not editorial) and were kept, the asterisk dropped; confirm against a page scan |
| 1549 Private Baptism (The Blessing of the Font) | `all those that shall he baptized` | the justus 1549 text reads 'shall he baptized'; an OCR/print slip for 'shall be baptized'; left as-sourced pending a 1549 scan |
| 1662 Public Baptism (The Final Exhortation) | `Foreasmuch` | source prints 'Foreasmuch'; the Private and Riper-Years 1662 forms print 'Forasmuch'; kept as printed; confirm against a page scan |
| 1789 Baptism of Riper Years (The Flood Prayer) | `his family m the ark` | source prints 'his family m the ark'; likely 'in the ark'; kept as printed; confirm against a page scan |
| 1789 Baptism of Riper Years (The Rubrics) | `he may he admitted` | source prints 'he may he admitted'; likely 'he may be admitted'; kept as printed; confirm against a page scan |
| 1789 Baptism of Riper Years (The Rubrics) | `shall he assembled` | source prints 'shall he assembled'; likely 'shall be assembled'; kept as printed; confirm against a page scan |
| 1789 Baptism of Riper Years (The Rubrics) | `shall he added` | source prints 'shall he added' and 'shall he used'; likely 'shall be added'/'shall be used'; kept as printed; confirm against a page scan |
| 1789 Baptism of Riper Years (The Rubrics) | `shall he brought` | source prints 'shall he brought'; likely 'shall be brought'; kept as printed; confirm against a page scan |
| 1789 Confirmation (The Renewal of Vows) | `under took` | source prints 'under took'; likely 'undertook'; kept as printed; confirm against a page scan |
| 1789 Private Baptism (The Vows) | `Wilt thou be baptized in this Faith?` | source prints 'Wilt thou be baptized in this Faith?' (with the answer 'That is my desire.') enclosed in square brackets with a footnote marking it an error later omitted in 1832; kept here as 1789 printed text, with the editorial brackets, asterisk, and footnote dropped; confirm against a page scan |
| 1789 Private Baptism (The Reception) | `let is give thanks` | source prints 'let is give thanks'; likely 'let us give thanks'; kept as printed; confirm against a page scan |
| 1892 Baptism of Riper Years (The Flood Prayer) | `his family m the ark` | source prints 'his family m the ark'; likely 'in the ark'; kept as printed; confirm against a page scan |
| 1892 Baptism of Riper Years (The Lord's Prayer) | `Thy will be done oil earth` | source prints 'Thy will be done oil earth'; likely 'on earth'; kept as printed; confirm against a page scan |
| 1892 Baptism of Riper Years (The Final Exhortation) | `Baptism repre-sent unto us` | source prints 'Baptism repre-sent unto us'; rejoined as 'represent'; 1789 parallel and CoE tradition read 'representeth'; confirm against a page scan |
| 1892 Baptism of Riper Years (The Rubrics) | `he may he admitted` | source prints 'he may he admitted'; likely 'he may be admitted'; kept as printed; confirm against a page scan |
| 1892 Baptism of Riper Years (The Rubrics) | `persons shalt be assembled` | source prints 'persons shalt be assembled'; likely 'shall be assembled'; kept as printed; confirm against a page scan |
| 1892 Baptism of Riper Years (The Rubrics) | `shall he added` | source prints 'shall he added' and 'shall he used'; likely 'shall be added'/'shall be used'; kept as printed; confirm against a page scan |
| 1892 Baptism of Riper Years (The Rubrics) | `shall he brought` | source prints 'shall he brought'; likely 'shall be brought'; kept as printed; confirm against a page scan |
| 1892 Confirmation (The Renewal of Vows) | `under took` | source prints 'under took'; likely 'undertook'; kept as printed; confirm against a page scan |
| 1892 Confirmation (The Lord's Prayer) | `Answer` | source prints the label 'Answer' before 'The Lord be with you' (label misplaced, likely OCR); assigned to the response 'And with thy spirit' per the parallel American rite; confirm against a page scan |
| 1892 Private Baptism (The Reception) | `let is give thanks` | source prints 'let is give thanks'; likely 'let us give thanks'; kept as printed; confirm against a page scan |
| 1892 Public Baptism (The Exhortation) | `graft` | source prints 'graft' ('he will graft to this Child'); likely 'grant'; kept as printed; confirm against a page scan |
| 1892 Public Baptism (The Exhortation upon the Gospel) | `sternal` | source prints 'sternal' ('the blessing of sternal life'); likely 'eternal'; kept as printed; confirm against a page scan |
| 1928 Confirmation (The Lord's Prayer) | `Answer` | source prints the label 'Answer' before 'The Lord be with you' (label misplaced, likely OCR); assigned to the response 'And with thy spirit' per the parallel American rite; confirm against a page scan |
| 1928 Public Baptism (The Second Prayer) | `arid` | source prints 'arid' ('Ask, arid ye shall have'); likely 'and'; kept as printed; confirm against a page scan |
| 1928 Public Baptism (The Gospel) | `putS` | source prints 'putS' ('putS his hands upon them'); likely 'put'; kept as printed; confirm against a page scan |
| — Wave 6: pastoral occasional offices — | | |
| 1559 Matrimony | `sale` | source prints 'sale'; likely 'saye'; kept as printed; confirm against a page scan |
| 1559 Matrimony | `thai` | source prints 'thai'; likely 'shal' (Then shal the Priest joyne); kept as printed; confirm against a page scan |
| 1559 Matrimony | `As it was in the be. &c.` | source prints 'As it was in the be. &c.'; reading unclear (likely 'in thee'); kept as printed; confirm against a page scan |
| 1559 Matrimony | `childers children` | source prints 'childers children'; likely 'childrens children'; kept as printed; confirm against a page scan |
| 1559 Matrimony | `Thaposthe` | source prints 'Thaposthe'; likely 'Thapostle' (the apostle); kept as printed; confirm against a page scan |
| 1892 Matrimony | `shalt come` | source prints 'shalt come' and "shalt be"; likely "shall come"/"shall be"; kept as printed; confirm against a page scan |
| 1892 Matrimony | `not by any to he entered into` | source prints 'not by any to he entered into'; likely "to be entered into"; kept as printed; confirm against a page scan |
| 1892 Matrimony | `to have andhold` | source prints 'to have andhold' (Man's vow reads "and to hold"); corrected joined word to "and hold"; a "to" may be dropped; confirm against a page scan |
| 1892 Matrimony | `who art m heaven` | source prints 'who art m heaven'; corrected obvious OCR to "in heaven"; confirm against a page scan |
| 1979 Matrimony | `Am the ordering of their common life` | 'Am the ordering of their common life' the 1979 PD e-text is garbled here — the rubric 'to which the People respond, saying, Amen.' and the first petition's opening ('Give them wisdom and devotion in the ordering…') are run together and words appear dropped; kept as printed in the e-text; confirm against a page scan |
| 1979 Matrimony | `you are bidden to declare it` | 'you are bidden to declare it' the 1979 PD e-text banns form reads 'between N. N. of — and N. N. of — in Holy Matrimony, you are bidden to declare it', apparently dropping the clause 'If any of you know reason why these two persons should not be joined together'; kept as printed in the e-text; confirm against a page scan |
| 1549 Visitation of the Sick | `yougth` | source prints 'yougth'; likely 'youth'; kept as printed; confirm against a page scan |
| 1549 Visitation of the Sick | `its` | source prints 'its'; likely 'in'; kept as printed; confirm against a page scan |
| 1549 Visitation of the Sick | `us` | source prints 'us'; likely 'in'; kept as printed; confirm against a page scan |
| 1549 Visitation of the Sick | `O Lorde,` | source prints 'O Lorde,' with a footnote 'Lorde omitted in some printings'; kept as printed; confirm against a page scan |
| 1552 Visitation of the Sick | `the articles a/the faith` | source prints 'the articles a/the faith'; 'a/the' is OCR for 'of the'; corrected; confirm against a page scan |
| 1552 Visitation of the Sick | `Psal. xxi.` | source prints 'Psal. xxi.'; the psalm is actually Psalm 71 (Vulgate Ps 70); kept as printed; confirm against a page scan |
| 1552 Visitation of the Sick | `cut of the forum of the visitacion` | source prints 'cut of the forum of the visitacion'; 'of the forum' is OCR for 'off the form'; corrected; confirm against a page scan |
| 1559 Visitation of the Sick | `in` | source prints 'in'; a footnote records "to" in early 1600's printings; footnote line dropped; confirm against a page scan |
| 1559 Visitation of the Sick | `rekerse` | source prints 'rekerse'; likely "reherse" (rehearse); kept as printed; confirm against a page scan |
| 1559 Visitation of the Sick | `lowarde` | source prints 'lowarde'; likely "towarde"; kept as printed; confirm against a page scan |
| 1559 Visitation of the Sick | `Chriest` | source prints 'Chriest'; likely "Christe"; kept as printed; confirm against a page scan |
| 1559 Visitation of the Sick | `Psaime` | source prints 'Psaime'; likely "Psalme"; kept as printed; confirm against a page scan |
| 1789 Visitation of the Sick | `chastenment` | source prints 'chastenment'; likely OCR / period variant of 'chastisement'; kept as printed; confirm against a page scan |
| 1789 Visitation of the Sick | `And of he hath not before disposed` | source prints 'And of he hath not before disposed'; 'of' likely OCR for 'if' ("And if he hath not"); kept as printed; confirm against a page scan |
| 1789 Visitation of the Sick | `his soul is full trouble` | source prints 'his soul is full trouble'; standard reading 'full of trouble'; kept as printed; confirm against a page scan |
| 1789 Visitation of the Sick | `depart of this life` | source prints 'depart of this life'; standard reading 'depart out of this life'; kept as printed; confirm against a page scan |
| 1892 Visitation of the Sick | `Maker heaven and earth` | 'Maker heaven and earth' the 1892 PDF prints 'Maker heaven and earth' (the word 'of' appears dropped; standard reading 'Maker of heaven and earth'); kept as printed; confirm against a page scan |
| 1892 Visitation of the Sick | `And of he hath not before disposed` | 'And of he hath not before disposed' the 1892 PDF prints 'And of he hath not'; 'of' is likely OCR for 'if' (both are real words), kept as printed; confirm against a page scan |
| 1892 Visitation of the Sick | `his soul is full trouble` | 'his soul is full trouble' the 1892 PDF prints 'his soul is full trouble' (the word 'of' appears dropped; standard reading 'full of trouble'); kept as printed; confirm against a page scan |
| 1892 Visitation of the Sick | `that so doing` | 'that so doing' the 1892 PDF prints 'to the often receiving of te Holy Communion' and 'that to doing, they may'; 'te'->'the' and 'to doing'->'so doing' read as OCR errors and are here corrected to the standard rite; confirm against a page scan |
| 1549 Burial | `m` | source prints 'm'; likely 'in' (Ps 116 'I was in misery'); kept as printed; confirm against a page scan |
| 1549 Burial | `avavntageth` | source prints 'avavntageth'; likely 'avauntageth'; kept as printed; confirm against a page scan |
| 1549 Burial | `eivill` | source prints 'eivill'; likely 'evill'; kept as printed; confirm against a page scan |
| 1549 Burial | `arid` | source prints 'arid'; likely 'and'; kept as printed; confirm against a page scan |
| 1549 Burial | `naturiall` | source prints 'naturiall'; likely 'naturall'; kept as printed; confirm against a page scan |
| 1549 Burial | `hyfe` | source prints 'hyfe'; likely 'lyfe' (cf. 1552 'depart thys lyfe'); kept as printed; confirm against a page scan |
| 1559 Burial | `unto` | source prints 'unto'; a footnote notes 'into' in 1604 printings; kept as printed; confirm against a page scan |
| 1559 Burial | `Job xi.` | source dumps marginal citation 'Job xi.' after this anthem; the anthem ("I heard a voice from heaven") is Revelation xiiii, not Job, so the citation appears misplaced or mis-scanned; kept as printed; confirm against a page scan |
| 1637 Burial | `the the resurrection` | source prints 'the the resurrection'; doubled word likely a transcription dittography for 'the resurrection'; kept as printed; confirm against a page scan |
| 1637 Burial | `hath taketh away` | source prints 'hath taketh away'; likely 'hath taken away'; kept as printed; confirm against a page scan |
| 1637 Burial | `an is full of trouble` | source prints 'an is full of trouble'; likely 'and is full of trouble'; kept as printed; confirm against a page scan |
| 1637 Burial | `shall he cast` | source prints 'shall he cast'; likely 'shall be cast'; kept as printed; confirm against a page scan |
| 1789 Burial | `Then the Minister shall say [the Lord` | source prints 'Then the Minister shall say [the Lord's Prayer]' with a bracket-and-asterisk footnote ("omitted in 1892 BCP"); brackets/asterisk dropped as editorial apparatus, words kept as printed; confirm against a page scan |
| 1789 Burial | `shalt say` | source prints 'shalt say'; likely "shall say"; kept as printed; confirm against a page scan |
| 1892 Burial | `Inasmuch it may sometimes` | source prints 'Inasmuch it may sometimes' with a doubled space; standard 1892 reads "Inasmuch as it may sometimes"; a word ("as") appears dropped in extraction; kept as printed; confirm against a page scan |
| 1928 Burial | `Grace` | source prints 'Grace'; likely 'Grave'; kept as printed; confirm against a page scan |
| 1928 Burial | `Minister.` | the spine prints detached 'Minister.'/"Answer." speaker labels for the following versicles (five stand-alone label lines, plus one "Answer." attached to "Blessed are the pure in heart"); the OCR separated the labels from their texts, so they are rendered here as plain versicle-and-response lines without reconstructed attribution; confirm against a page scan |
| 1604 Burial | `Job xi.` | source dumps marginal citation 'Job xi.' after this anthem; the anthem ("I heard a voice from heaven") is Revelation xiiii, not Job, so the citation appears misplaced or mis-scanned; kept as printed; confirm against a page scan |
| 1559 Churching | `as the case that require` | source prints 'as the case that require'; likely 'as the case shal require'; kept as printed; confirm against a page scan |
| 1559 Churching | `Priest` | source prints 'Priest'; footnote notes 'Minister' in 1604; confirm against a page scan |
| 1559 Churching | `gine her thanckes` | source prints 'gine her thanckes'; likely 'geve/give her thankes'; kept as printed; confirm against a page scan |
| 1637 Churching | `Psal. 121.` | spine prints a trailing 'Psal. 121.' after "if there be any at that time." on the Communion rubric; dropped here as a running caption / catchword rather than liturgical text; confirm against a page scan |
| 1789 Churching | `Minster` | source prints 'Minster'; likely 'Minister'; kept as printed; confirm against a page scan |
| 1892 Churching | `sf` | 'sf' source (1892 PDF) prints 'sf this be used'; obvious OCR for 'if'; corrected; confirm against a page scan |
| 1892 Churching | `he applied` | 'he applied' source (1892 PDF) prints 'which shall he applied by the Minister'; obvious OCR for 'be applied'; corrected; confirm against a page scan |
| 1979 Churching | `asbrant` | 'asbrant' the 1979 PD e-text is garbled/merged here — the rubric 'The Celebrant, holding or taking the child by the hand, gives the child to the mother or father, saying' is run into the preceding address and 'the Celebrant' appears corrupted to 'asbrant'; kept as printed in the e-text; confirm against a page scan |
| 1604 Churching | `as the case that require` | source prints 'as the case that require'; likely 'as the case shal require'; kept as printed; confirm against a page scan |
| 1604 Churching | `gine her thanckes` | source prints 'gine her thanckes'; likely 'geve/give her thankes'; kept as printed; confirm against a page scan |
| 1549 Commination | `Date` | source prints 'Date' (Firste Date of Lente); likely 'Daye' (the first day of Lent); kept as printed; confirm against a page scan |
| 1549 Commination | `cummen` | source prints 'cummen' (the lorde is cummen out of his place); a footnote notes 'come' in some printings; confirm against a page scan |
| 1549 Commination | `pietie` | source prints 'pietie' (of a great pietie); a footnote notes 'pity' in some printings; confirm against a page scan |
| 1552 Commination | `alter` | 'alter' source (justus 1552) prints 'alter thy great goodness'; Psalm 51 and the 1549 parallel read 'after'; likely an f/l OCR scanno; kept as printed; confirm against a page scan |
| 1552 Commination | `dense` | 'dense' source (justus 1552) prints 'dense me from my sinne'; the 1549 parallel reads 'clense'; likely a 'cl'->'d' OCR scanno; kept as printed; confirm against a page scan |
| 1559 Commination | `judgmet` | source prints 'judgmet'; likely 'judgment' (missing 'n'); kept as printed; confirm against a page scan |
| 1559 Commination | `Curseth` | source prints 'Curseth'; every parallel curse reads 'Cursed'; likely a 'd'->'th' OCR scanno; kept as printed; confirm against a page scan |
| 1559 Commination | `cornmaundernentes` | source prints 'cornmaundernentes'; likely 'commaundementes' (rn->m OCR scannos); kept as printed; confirm against a page scan |
| 1559 Commination | `soubdenly` | source prints 'soubdenly'; likely 'sodenly' (stray 'b'); kept as printed; confirm against a page scan |
| 1559 Commination | `tyrne of Justice` | source prints 'tyrne of Justice'; likely 'tyme' (rn->m OCR scanno); kept as printed; confirm against a page scan |
| 1559 Commination | `were` | source rubric prints 'were' (likely 'where') and 'shall say thy: Psalme' (likely 'this'); both look like OCR errors; kept as printed; confirm against a page scan |
| 1559 Commination | `multitud` | source prints 'multitud'; likely 'multitude' (missing 'e'); kept as printed; confirm against a page scan |
| 1559 Commination | `Minis/er.` | source prints the label 'Minis/er.'; clearly 'Minister.'; rendered as the printed speaker designation |
| 1559 Commination | `Psal. li.` | source prints 'Psal. li.' as a detached final line after the Turn Thou Us prayer (the psalm citation for the Miserere); kept in printed position; confirm against a page scan |
| 1637 Commination | `Matt. 31.2.` | source prints 'Matt. 31.2.'; there is no Matthew 31, the reference is to Matt. 3.12 ('His fanne is in his hand… burn the chaff'); kept as printed; confirm against a page scan |
| 1637 Commination | `thy god pleasure` | source prints 'thy god pleasure'; Psalm 51 and sense read 'thy good pleasure'; likely a dropped 'o'; kept as printed; confirm against a page scan |
| 1637 Commination | `be I favourable, O Lord, bee favourable` | source prints 'be I favourable, O Lord, bee favourable'; the intrusive 'I' appears to be a stray character/dittography (cf. 1552 'bee favourable (O Lord) bee fauourable'); kept as printed; confirm against a page scan |
| 1552 Catechism | `THAT IS TO SAVE` | source prints 'THAT IS TO SAVE'; obvious OCR scanno for 'saye' (cf. 1549 'that is to say'); rendered 'saye'; confirm against a page scan |
| 1552 Catechism | `the Lard` | source prints 'the Lard'; obvious OCR scanno for 'Lord' (cf. II 'the Lorde thy God'); rendered 'Lord'; confirm against a page scan |
| 1559 Catechism | `Commaundemetes` | source prints 'Commaundemetes'; OCR drop of a letter for 'Commaundementes'; rendered 'Commaundementes'; confirm against a page scan |
| 1559 Catechism | `in hyrn` | source prints 'in hyrn'; OCR 'rn' for 'm' → 'hym'; rendered 'hym'; confirm against a page scan |
| 1604 Catechism | `Commaundemetes` | source prints 'Commaundemetes'; OCR drop of a letter for 'Commaundementes'; rendered 'Commaundementes'; confirm against a page scan |
| 1604 Catechism | `in hyrn` | source prints 'in hyrn'; OCR 'rn' for 'm' → 'hym'; rendered 'hym'; confirm against a page scan |
| 1604 Catechism | `In the name the Name of the Father, and of Sonne` | source prints 'In the name the Name of the Father, and of Sonne'; apparent dittography of 'name/Name' and a dropped 'the' before 'Sonne'; kept as printed; confirm against a page scan |
| 1637 Catechism | `In the name the Name of the Father, and of Sonne` | source prints 'In the name the Name of the Father, and of Sonne'; apparent dittography of 'name/Name' and a dropped 'the' before 'Sonne'; kept as printed; confirm against a page scan |
| 1559 Ordering of Deacons | `Elizabeth` | 'Elizabeth'; the justus synoptic gives the 1559-added petition text with EDWARD retained and a note 'changed appropriately for Queen Elizabeth, King James & King Charles'; the sovereign name and her/she pronouns are the apparatus-directed Elizabethan substitution; confirm against a 1559 page scan |
| 1604 Ordering of Deacons | `James` | 'James'; there is no 1604 justus Ordinal page; the 1604 sovereign name and his/he pronouns are derived from the 1559 petition per the synoptic note 'changed appropriately for … King James'; confirm against a 1604 page scan |
| 1604 Ordering of Deacons | `Kings` | 'Kings'; the 1604 King's-Sovereignty oath is derived from the 1559 Queen's oath per the justus note 'Kings supremacie in 1604' and its bracketed [Kings]/[his] readings; confirm against a 1604 page scan |
| 1662 Ordering of Deacons | `CHARLES` | 'CHARLES'; the CoE source prints the reigning monarch (Charles III); the 1662 book as first printed named the then-sovereign (Charles II); reign-dependent; reconcile against a dated 1662 page scan |
| 1662 Ordering of Deacons | `Queen Camilla, William Prince of Wales, the Princess of Wales` | 'Queen Camilla, William Prince of Wales, the Princess of Wales'; the CoE source prints the current Royal Family; the 1662 book named the then-Royal Family; reign-dependent; reconcile against a dated 1662 page scan |
| 1549 Ordering of Priests | `where thou shalt be so appointed` | 'where thou shalt be so appointed'; the justus synoptic brackets this tail with a note "Replaced by 'al' in 1552"; the exact 1552/1559 tail is left as the 1550 reading pending a page scan |
| 1552 Ordering of Priests | `where thou shalt be so appointed` | 'where thou shalt be so appointed'; the justus synoptic brackets this tail with a note "Replaced by 'al' in 1552"; the exact 1552/1559 tail is left as the 1550 reading pending a page scan |
| 1789 Ordering of Priests | `for that and ability` | 'for that and ability'; the 1662 reads 'for that will and ability'; the 1789 justus HTML likely dropped 'will' in OCR; kept as printed; confirm against a 1789 page scan |
| 1789 Ordering of Priests | `as much as in lieth` | 'as much as in lieth'; likely 'as much as in you lieth' (word 'you' dropped in OCR); kept as printed; confirm against a 1789 page scan |
| 1789 Ordering of Priests | `That neither devil, world, nor` | 'That neither devil, world, nor'; the following metrical line likely began 'flesh,' (dropped in OCR — cf. 1662 'nor flesh, against us'); kept as printed; confirm against a 1789 page scan |
| 1892 Ordering of Priests | `for that and ability` | 'for that and ability'; the 1662 reads 'for that will and ability'; the 1789 justus HTML likely dropped 'will' in OCR; kept as printed; confirm against a 1789 page scan |
| 1892 Ordering of Priests | `as much as in lieth` | 'as much as in lieth'; likely 'as much as in you lieth' (word 'you' dropped in OCR); kept as printed; confirm against a 1789 page scan |
| 1892 Ordering of Priests | `That neither devil, world, nor` | 'That neither devil, world, nor'; the following metrical line likely began 'flesh,' (dropped in OCR — cf. 1662 'nor flesh, against us'); kept as printed; confirm against a 1789 page scan |
| 1604 Consecration of Bishops | `Kings` | 'Kings'; there is no 1604 justus Ordinal page; the King's Mandate/Sovereignty is derived from the 1559 Queen's readings per the synoptic 'Kings supremacie in 1604' note; confirm against a 1604 page scan |
| 1789 Consecration of Bishops | `That neither devil, world, nor` | 'That neither devil, world, nor'; the following metrical line likely began 'flesh,' (dropped in OCR — cf. 1662 'nor flesh, against us'); kept as printed; confirm against a 1789 page scan |
| 1892 Consecration of Bishops | `Or else the longer paraphrase of the same Hymn, as in the Ordering of Priests.` | 'Or else the longer paraphrase of the same Hymn, as in the Ordering of Priests.'; the justus 1789 apparatus notes only that in 1892 the printed hymn is replaced by this cross-reference; confirm the exact 1892 rubric wording against a 1892 page scan |
| 1789 The Preface | `member of our Church. and every sincere Christian` | 'member of our Church. and every sincere Christian' — the justus 1789 text prints a full stop before a lower-case "and"; likely a comma in the original; left as-sourced pending a 1789 scan |
| 1637 Concerning the Service of the Church | `to fall to thin ground` | 'to fall to thin ground' — probably an OCR rendering of "to fall to the ground"; left as-sourced from justus pending a 1637 scan |
| 1979 Concerning the Service of the Church | `fulfull` | 'fulfull' — the justus 1979 public-domain e-text reads "fulfull"; the printed 1979 Book reads "fulfil"; treated as an e-text typo and left as-sourced pending a page-scan check |
| 1637 Of Ceremonies | `OF such Ceremonies as be used in the Church, and have had their Beginning by the Institution of Man` | 'OF such Ceremonies as be used in the Church, and have had their Beginning by the Institution of Man' — justus notes two leaves are missing from its 1637 original around this section, so the Of Ceremonies text may be supplied from a parallel copy; confirm against a 1637 scan |
<!-- wave10-10a rows: begin -->
| 1549 advent-3 | `The thirde sonday [in` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 advent-4 | `The fourth sonday [in` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 ash-wednesday | `The fyrst day of Lent[, commonly called` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 easter-3 | `The iii Sondaye` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 easter-4 | `The iiii Sondaye[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 easter-5 | `The v. Sondaie` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 epiphany-3 | `The thirde Soondaye` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 epiphany-4 | `The iiii Sonday[after the` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 epiphany-5 | `The v. Sonday[after the` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 lent-2 | `The seconde Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 lent-3 | `The iii. Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 lent-4 | `The iiii Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 lent-5 | `The v. Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 st-bartholomew | `Sainct Bartholomewe[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 st-matthew | `Sayncte Matthewe[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 trinity-2 | `The second Sondaye` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 trinity-3 | `The third sonday[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 trinity-4 | `The fourth Sondaye[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 trinity-5 | `The v Sunday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 trinity-6 | `The vi Sondaie` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 trinity-7 | `The vii Sonday[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1549 trinity-8 | `The eight Sonday[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 advent-3 | `The thirde sonday [in` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 advent-4 | `The fourth sonday [in` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 ash-wednesday | `The fyrst day of Lent[, commonly called` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 easter-3 | `The iii Sondaye` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 easter-4 | `The iiii Sondaye[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 easter-5 | `The v. Sondaie` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 epiphany-3 | `The thirde Soondaye` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 epiphany-4 | `The iiii Sonday[after the` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 epiphany-5 | `The v. Sonday[after the` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 lent-2 | `The seconde Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 lent-3 | `The iii. Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 lent-4 | `The iiii Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 lent-5 | `The v. Sonday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 st-bartholomew | `Sainct Bartholomewe[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 st-matthew | `Sayncte Matthewe[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 trinity-2 | `The second Sondaye` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 trinity-3 | `The third sonday[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 trinity-4 | `The fourth Sondaye[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 trinity-5 | `The v Sunday` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 trinity-6 | `The vi Sondaie` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 trinity-7 | `The vii Sonday[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1552 trinity-8 | `The eight Sonday[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 advent-3 | `The thirde sonday [in` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 advent-4 | `The fourth sonday [in` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 ash-wednesday | `The fyrst day of Lent[, commonly called` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 easter-3 | `The iii Sondayeafter Easter` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 easter-4 | `The iiii Sondaye[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 easter-5 | `The v. Sondaieafter Easter` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 epiphany-3 | `The thirde Soondaye after the Epiphany` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 epiphany-4 | `The iiii Sonday[after the` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 epiphany-5 | `The v. Sonday[after the` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 lent-2 | `The seconde Sonday in Lent` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 lent-3 | `The iii. Sonday in Lent` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 lent-4 | `The iiii Sonday in Lent` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 lent-5 | `The v. Sonday in Lent` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 st-bartholomew | `Sainct Bartholomewe[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 st-matthew | `Sayncte Matthewe[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 trinity-2 | `The second Sondayeafter Trinity` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 trinity-3 | `The third sonday[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 trinity-4 | `The fourth Sondaye[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 trinity-5 | `The v Sundayafter Trinity` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 trinity-6 | `The vi Sondaieafter Trinity` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 trinity-7 | `The vii Sonday[` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1559 trinity-8 | `The eight Sonday[ after` | the source brackets this title expansion and footnotes it only as "added in late 1500's", without naming a book; represented here as entering at 1559. |
| 1892 advent-1 | `The First Sunday in Advent` | * "unto" in 1892 only — the source marks the variant with an asterisk in the rubric but does not give the surrounding wording, so the 1789 reading is kept here. |
| 1892 advent-2 | `The Second Sunday in Advent` | * Comma was before the word 'ever' until 1892. |
| 1892 christmas-day | `The Nativity of our Lord, or the Birthday of Christ, commonly called Christmas-day` | * Virgin until 1832 † Holy from 1892 |
| 1892 transfiguration | `The Transfiguration of Christ` | Readings for the Transfiguration added in 1892 — the source states only that the READINGS were added then, and does not say when the feast or its collect first appeared in the American books. |
| 1928 advent-1 | `The First Sunday in Advent` | * "unto" in 1892 only — the source marks the variant with an asterisk in the rubric but does not give the surrounding wording, so the 1789 reading is kept here. |
| 1928 advent-2 | `The Second Sunday in Advent` | * Comma was before the word 'ever' until 1892. |
| 1928 advent-3 | `The Third Sunday in Advent` | * against myself in 1928 |
| 1928 advent-4 | `The Fourth Sunday in Advent` | * through Jesus Christ our Lord in 1928 |
| 1928 christmas-2 | `The Second Sunday after Christmas Day` | Readings for the 2nd Sunday after Christmas added in 1928 — the source prints one set of readings for this day without distinguishing them, so they are carried at 1928 and omitted at 1789/1892. |
| 1928 christmas-day | `The Nativity of our Lord, or the Birthday of Christ, commonly called Christmas-day` | * Virgin until 1832 † Holy from 1892 |
| 1928 circumcision | `The Circumcision of Christ` | the apparatus labels the earlier Epistle "1786, 1786, 1892" -- 1786 twice and no 1789 -- evidently a typo for "1786, 1789, 1892"; read as including 1789, whose base text it is. |
| 1928 epiphany | `The Epiphany, or the Manifestation of` | This rubric dropped in 1928. |
| 1928 epiphany-4 | `The Fourth Sunday after the Epiphany` | * condemnation in 1928 — and the source does not say what becomes of the 1789 Gospel this shift displaces. |
| 1928 transfiguration | `The Transfiguration of Christ` | Readings for the Transfiguration added in 1892 — the source states only that the READINGS were added then, and does not say when the feast or its collect first appeared in the American books. |
| 1928 whitsunday | `Whitsunday` | WHITSUNTIDE. Pentecost, commonly called Whitsunday. in 1928 — and "Rubric and Readings for a second service added in 1928"; the second service's readings are not separately printed on the page, so they are not represented here. |
| 1979 advent-1 | `First Sunday of Advent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 advent-2 | `Second Sunday of Advent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 advent-3 | `Third Sunday of Advent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 advent-4 | `Fourth Sunday of Advent` | the traditional-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 advent-4 | `Fourth Sunday of Advent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 all-saints | `All Saint` | s Day' — 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 annunciation | `The Annunciation` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 annunciation | `The Annunciation` | the collect under `The Collect` breaks off mid-sentence in the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); carried as the source has it and NOT reconstructed. |
| 1979 annunciation | `The Annunciation` | the collect under `The Collect (Contemporary)` breaks off mid-sentence in the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); carried as the source has it and NOT reconstructed. |
| 1979 ascension-1 | `Seventh Sunday of Easter: The Sunday after Ascension Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 ascension-day | `Ascension Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 ash-wednesday | `Ash Wednesday` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 christmas-1 | `First Sunday after Christmas Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 christmas-2 | `Second Sunday after Christmas Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 christmas-day | `The Nativity of Our Lord: Christmas Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 circumcision | `The Holy Name` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 conversion-st-paul | `Conversion of Saint Paul` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-1 | `Second Sunday of Easter` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-2 | `Third Sunday of Easter` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-3 | `Fourth Sunday of Easter` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-4 | `Fifth Sunday of Easter` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-4 | `Fifth Sunday of Easter` | the collect under `The Collect (Contemporary)` breaks off mid-sentence in the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); carried as the source has it and NOT reconstructed. |
| 1979 easter-5 | `Sixth Sunday of Easter` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-day | `Easter Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-even | `Holy Saturday` | the contemporary-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 easter-even | `Holy Saturday` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-friday | `Friday in Easter Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-monday | `Monday in Easter Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-saturday | `Saturday in Easter Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-thursday | `Thursday in Easter Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-tuesday | `Tuesday in Easter Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 easter-wednesday | `Wednesday in Easter Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany | `The Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-1 | `First Sunday after the Epiphany: The Baptism of our Lord` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-2 | `Second Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-3 | `Third Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-4 | `Fourth Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-5 | `Fifth Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-6 | `Sixth Sunday after the Epiphany` | the contemporary-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 epiphany-6 | `Sixth Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-7 | `Seventh Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-8 | `Eighth Sunday after the Epiphany` | the traditional-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 epiphany-8 | `Eighth Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 epiphany-last | `Last Sunday after the Epiphany` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 good-friday | `Good Friday` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 holy-innocents | `The Holy Innocents` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 independence-day | `Independence Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 lent-1 | `First Sunday in Lent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 lent-2 | `Second Sunday in Lent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 lent-3 | `Third Sunday in Lent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 lent-4 | `Fourth Sunday in Lent` | the contemporary-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 lent-4 | `Fourth Sunday in Lent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 lent-5 | `Fifth Sunday in Lent` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 monday-before-easter | `Monday in Holy Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 palm-sunday | `Sunday of the Passion: Palm Sunday` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 purification | `The Presentation` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-andrew | `Saint Andrew` | the contemporary-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 st-andrew | `Saint Andrew` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-barnabas | `Saint Barnabas` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-bartholomew | `Saint Bartholomew` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-james | `Saint James` | the contemporary-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 st-james | `Saint James` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-james-of-jerusalem | `Saint James of Jerusalem` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-john-baptist | `The Nativity of Saint John the Baptist` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-john-evangelist | `Saint John` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-joseph | `Saint Joseph` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-luke | `Saint Luke` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-mark | `Saint Mark` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-mary-magdalene | `Saint Mary Magdalene` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-mary-the-virgin | `Saint Mary the Virgin` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-matthew | `Saint Matthew` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-matthias | `Saint Matthias` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-michael | `Saint Michael and All Angels` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-peter | `Saint Peter and Saint Paul` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-philip-st-james | `Saint Philip and Saint James` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-simon-st-jude | `Saint Simon and Saint Jude` | the contemporary-language collect for this day is absent from the public-domain e-text (a dropout in its 1993 keying, not a feature of the book); not reconstructed. |
| 1979 st-simon-st-jude | `Saint Simon and Saint Jude` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-stephen | `Saint Stephen` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 st-thomas | `Saint Thomas` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 thanksgiving-day | `Thanksgiving Day` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 the-visitation | `The Visitation` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 thursday-before-easter | `Maundy Thursday` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 transfiguration | `The Transfiguration` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-11 | `Proper 21` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-11 | `Proper 21` | placed at `trinity-11` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-12 | `Proper 22` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-12 | `Proper 22` | placed at `trinity-12` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-13 | `Proper 26` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-13 | `Proper 26` | placed at `trinity-13` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-17 | `Proper 23` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-17 | `Proper 23` | placed at `trinity-17` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-19 | `Proper 19` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-19 | `Proper 19` | placed at `trinity-19` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-20 | `Proper 2` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-20 | `Proper 2` | placed at `trinity-20` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-4 | `Proper 12` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-4 | `Proper 12` | placed at `trinity-4` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-7 | `Proper 17` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 trinity-7 | `Proper 17` | placed at `trinity-7` by COLLECT LINEAGE, not by day: 1979 replaces the Sundays after Trinity with calendar-dated Propers, so it does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this representation is flagged for revision. |
| 1979 trinity-sunday | `First Sunday after Pentecost: Trinity Sunday` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 tuesday-before-easter | `Tuesday in Holy Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 wednesday-before-easter | `Wednesday in Holy Week` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
| 1979 whitsunday | `The Day of Pentecost: Whitsunday` | 1979 appoints three reading sets for this day under the three-year lectionary, which the single Epistle/Gospel slot cannot represent; deferred to the lectionary-tables wave. |
<!-- wave10-10a rows: end -->
## Occasional offices — Baptism family & Confirmation (Wave 5)
| `prayers-and-thanksgivings/for-the-clergy-and-people.md` (1559, 1604) | `untitled` | The source prints this prayer with no title of its own — it follows the preceding prayer directly, opening with a drop capital. The bracketed heading is editorial; confirm against a page scan. |
| `prayers-and-thanksgivings/prayer-after-the-former.md` (1604, 1637) | `untitled` | Printed without a title in these editions (1662 heads it "A Prayer that may be said after any of the former"). The bracketed heading is editorial. The 1559 page's note "This prayer added in 1604" sits immediately after this text, but the spine has lost the page's visual association of note to referent — confirm the attribution. |
| `prayers-and-thanksgivings/for-the-sovereign.md` (1604) | `Quene Elizabeth` | RECORDED GAP, not a reading. The 1559 page's apparatus says this prayer was "Replaced by a prayer for the King in 1604" and gives the style "Sovereign Lord King James", but attests neither the pronouns nor the spellings the 1604 book printed. The attested 1559 wording is retained rather than reconstructing a text no allow-listed source supports; resolve from a 1604 facsimile. |
| `occasional-offices/prayers-at-sea.md` (1662) | `psalm-cento` | Two runs of psalm verses in the Sea forms (the composite "Hymn of Praise and Thanksgiving" after a tempest, and the one after victory) carry no single printed psalm label, so no citation is supplied for them. The verses are deferred to the Psalter wave along with the labelled psalms. Confirm against a page scan whether the book names a source for either hymn. |
| 1789 (American) Kalendar | `November Morning 1, Evening 1` | the source column(s) Morning 1, Evening 1 carry one entry fewer than this month has days, so they are omitted for November rather than aligned on a guess, which would misdate every following day of the month |
| 1892 (American) Proper Lessons | `Proper Lessons: Morning 2` | the source column(s) Morning 2 do not match the height of the others in this table, so they are omitted rather than aligned on a guess |
| 1979 (American) Daily Office Lectionary | `Proper 4 (=Week of 1-12; 2 Cor. 6:3-13(14-7:1); Luke 17:11-19)` | the e-text merges a reading line into this week heading; the heading is carried as printed and the displaced readings are not reconstructed |
| 1979 (American) Daily Office Lectionary | `Year One / Proper 10 (Week of the Sunday closest to July 13) / Friday` | the e-text yields 0 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `Mark 15:12-21` | the e-text yields 5 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `Luke 10:1-12,17-20` | the e-text yields 5 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `Matt. 22:15-22` | the e-text yields 5 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `John 2:1-12` | the e-text yields 2 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `2 Cor. 5:11-21 Mark 10:35-45` | the e-text yields 2 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `1 Cor. 10:14-17,- 42[*]` | the e-text yields 2 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `Rom. 11:1-12 Matt. 25:1-13` | the e-text yields 2 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `Year Two / Proper 19 (Week of the Sunday closest to September 14) / Friday` | the e-text yields 0 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Daily Office Lectionary | `Luke 14:18-30` | the e-text yields 6 readings where this office takes 3; carried exactly as the e-text prints it, not repaired |
| 1979 (American) Eucharistic Lectionary | `Year A: First and Second Sundays of Advent` | the public-domain e-text loses page 889 entirely, taking the '<Year A>' heading, the close of 'Concerning the Lectionary', and Year A's First and Second Sundays of Advent; the rows are absent rather than reconstructed |
| 1979 (American) Eucharistic Lectionary | `Hebrews 1:1-12, John 1:1-14` | the e-text yields 3 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 890) |
| 1979 (American) Eucharistic Lectionary | `John 1:29-41` | the e-text yields 3 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 890) |
| 1979 (American) Eucharistic Lectionary | `Matthew 21:1-11` | the e-text yields 2 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 892) |
| 1979 (American) Eucharistic Lectionary | `The Great Vigil: See pages 288-291.` | the e-text yields 1 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 893) |
| 1979 (American) Eucharistic Lectionary | `thew 21:33-43` | the e-text yields 1 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 898) |
| 1979 (American) Eucharistic Lectionary | `Mark 11:1-11a` | the e-text yields 2 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 903) |
| 1979 (American) Eucharistic Lectionary | `Matthew 28:1-10` | the e-text yields 6 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 904) |
| 1979 (American) Eucharistic Lectionary | `John 6:37-51` | the e-text yields 6 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 908) |
| 1979 (American) Eucharistic Lectionary | `Luke 21:25-31` | the e-text yields 3 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 911) |
| 1979 (American) Eucharistic Lectionary | `Luke 2:15-21` | the e-text yields 3 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 912) |
| 1979 (American) Eucharistic Lectionary | `Philippians 3:17--4:1 Luke 13:(22-30)31-35` | the e-text yields 3 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 913) |
| 1979 (American) Eucharistic Lectionary | `2 Corinthians 5:17-21 Luke 15:11-32` | the e-text yields 3 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 913) |
| 1979 (American) Eucharistic Lectionary | `Luke 19:29-40` | the e-text yields 2 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 914) |
| 1979 (American) Eucharistic Lectionary | `The Great Vigil: See pages 288-291` | the e-text yields 1 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 915) |
| 1979 (American) Eucharistic Lectionary | `Luke 12:13-21` | the e-text yields 6 citation fields where this occasion takes 4; carried exactly as the e-text prints it, not repaired (page 919) |

Four services under `occasional-offices/`, at Tier-1 across every edition that has
them. Public/Private Baptism and Confirmation run across the ten daily-office
editions (English 1549–1662, Scottish 1637, American 1789–1979); the Scottish
1764/1929 line is Communion-only, so all four are **absent** there. **Baptism of
Those of Riper Years** is a 1662 addition, present only at 1662, 1789 and 1892 —
the American line folds infant and adult baptism into a single Holy Baptism office
by 1928/1979, so the separate riper-years office is absent at 1928/1979.

Sources (justus per-edition pages; the 1662 texts from the Church of England
website; the 1979 texts from the public-domain ASCII e-text):

| Edition | Public / Private Baptism | Confirmation |
|---------|--------------------------|--------------|
| 1549 | `1549/Baptism_1549.htm` | `1549/Confirmation_1549.htm` (bundled with the Catechism; office only) |
| 1552 | `1552/Baptism_1552.htm` | `1552/Confirmation_1552.htm` |
| 1559 | `1559/Baptism_1559.htm` | `1559/Confirmation_1559.htm` (bundled with the Catechism; office only) |
| 1604 | derived from the justus 1559 apparatus | derived from the justus 1559 apparatus |
| 1662 | CoE `public-baptism-infants` / `private-baptism-infants` | CoE `order-confirmation` |
| 1637 | `Scotland/Baptism_1637.htm` | `Scotland/Confirmation_1637.htm` |
| 1789 | `1789/Baptism_1789.htm` | `1789/Confirmation_1789.htm` |
| 1892 | `1892/Baptism_1892.htm` | `1892/Confirmation_1892.htm` |
| 1928 | `1928/Baptism.htm` (single Holy Baptism office) | `1928/Confirnation.htm` (justus filename typo; bundled with the Offices of Instruction; office only) |
| 1979 | `bcpspecl.txt` (Holy Baptism / Emergency Baptism) | `bcpastrl.txt` (Pastoral Offices) |

Baptism of Riper Years: 1662 CoE `public-baptism-such-are-riper`; 1789
`1789/Baptism_1789.htm#Adult Baptism`; 1892 `1892/Baptism_1892.htm#Adult Baptism`.

Scope notes: the **1604 Public Baptism** office is unchanged from 1559 (baptism
carries no sovereign's name) and inherits the 1559 file; the flagged 1604 changes
fall in **Private Baptism** (the Hampton Court restriction to a lawful minister,
an expanded doubt-rubric and examination) and in **Confirmation** (`bothe`
removed; `prayer`→`prayers`). The 1549 "Blessing of the Font" prayers (printed
after the private-baptism office) are now transcribed — appended to the 1549
Private Baptism file under `## The Blessing of the Font`, present at 1549 only (a
clean deletion at v1552). The Catechism bodies once bundled on the 1549/1559/1928
Confirmation pages were transcribed in the Catechism wave.


## Occasional offices — pastoral offices (Wave 6)

Five services under `occasional-offices/`: **Matrimony**, the **Visitation of the
Sick** (with the Communion of the Sick), the **Burial of the Dead**, the
**Churching of Women**, and the **Commination**. Matrimony, Visitation, and Burial
run across the ten daily-office editions (English 1549–1662, Scottish 1637,
American 1789–1979); the Churching runs across them too (as the 1979 "Thanksgiving
for the Birth or Adoption of a Child"); the Commination is an English/Scottish
office (1549–1662 + 1637) that the American line drops (a clean deletion at 1789,
inherited by 1892/1928/1979). 1764/1929 remain Communion-only and carry none.

| Edition | Matrimony | Visitation of the Sick | Burial | Churching | Commination |
|---|---|---|---|---|---|
| 1549 | `1549/Marriage_1549.htm` | `1549/Visitation_Sick_1549.htm` | `1549/Burial_1549.htm` | `1549/Purification_Women_1549.htm` | `1549/Ashwednesday_1549.htm` |
| 1552 | `1552/Marriage_1552.htm` | `1552/Visitation_Sick_1552.htm` | `1552/Burial_1552.htm` | `1552/Churching_Women_1552.htm` | `1552/Commination_1552.htm` |
| 1559 | `1559/Marriage_1559.htm` | `1559/Visitation_Sick_1559.htm` | `1559/Burial_1559.htm` | `1559/Churching_of_Women_1559.htm` | `1559/Churching_of_Women_1559.htm` (bundled `#Commination`) |
| 1604 | inherits 1559 (no apparatus deltas) | inherits 1559 (no apparatus deltas) | derived from 1559 (`unto`→`into`) | derived from 1559 (`Priest`→`Minister`) | inherits 1559 (no apparatus deltas) |
| 1662 | CoE `form-solemnization-matrimony` | CoE `visitation-sick` + `communion-sick` | CoE `burial-dead` | CoE `churching-women` | CoE `commination` |
| 1637 | `Scotland/Marriage_1637.htm` | `Scotland/Visitation_Sick_1637.htm` | `Scotland/Burial_1637.htm` | `Scotland/Churching_of_Women_1637.htm` | `Scotland/Commination_1637.htm` |
| 1789 | `1789/Marriage_1789.htm` | `1789/Visitation_Sick_1789.htm` | `1789/Burial_1789.htm` | `1789/Churching_of_Women_1789.htm` | **absent** (dropped on the American line) |
| 1892 | `1892/Marriage_1892.pdf` | `1892/Visitation_Sick_1892.pdf` | `1892/Burial_1892.pdf` | `1892/Churching_of_Women_1892.pdf` | absent (inherited) |
| 1928 | `1928/Marriage.htm` | `1928/Visitation_Sick.htm` | `1928/Burial.htm` | `1928/Marriage.htm` (bundled `#Churching_Women`) | absent (inherited) |
| 1979 | `bcpastrl.txt` (Celebration and Blessing of a Marriage) | `bcpastrl.txt` (Ministration to the Sick) | `bcpastrl.txt` (Burial, Rite One + Rite Two) | `bcpastrl.txt` (Thanksgiving for the Birth or Adoption of a Child) | absent (no 1979 Commination) |

Scope notes: the 1549 Commination is printed as "The First Day of Lent, commonly
called Ash-Wednesday"; the 1549 Churching as "The Order of the Purification of
Women". The American 1892 offices exist on justus only as text-layer PDFs (the
1892 HTML index links back to the 1789 pages); they were extracted with pypdf
layout mode (or, for the two-column pages the extractor interleaves, read directly
from the PDF) and their obvious PDF-layout artifacts (drop-caps, split/joined
words, line-break hyphenation) corrected. The 1979 offices are reflowed
mechanically from the public-domain ASCII e-text (`bcpastrl.txt`); a few genuine
e-text defects (a dropped clause in the Marriage banns form, a garbled run in the
Marriage prayers rubric, a corrupted word in the Thanksgiving) are kept verbatim
and flagged. The 1979 book has no Commination and its nearest relative (the Ash
Wednesday liturgy) is deliberately not mapped.

## The Catechism (Wave 7)

One service, `occasional-offices/catechism.md`, at Tier-1 across the editions that
carry it. Historically the Catechism is printed with Confirmation (its title is "A
Catechism, that is to say, an Instruction to be learned of every person before he
be brought to be Confirmed by the Bishop"), so it lives beside `confirmation.md`
under `occasional-offices/`. **Scope:** `catechism.md` holds the Catechism title
and its Question-and-Answer body; the framing/catechizing rubrics that surround it
in the book (the Confirmation preface, "So soon as the children can say…", "The
Curate of every parish shall diligently … instruct and examine…") are
Confirmation-office rubrics and live in `confirmation.md`.

The Catechism runs across the ten daily-office editions (English 1549–1662,
Scottish 1637, American 1789–1979); 1764 is Communion-only (absent) and 1929
inherits that absence (the repo's Scottish line is Communion-only after 1637).

The flagship diff is that the Catechism **grows**: the pre-1604 text ends at the
Lord's-Prayer exposition, and the 1604 book **adds the whole Sacraments section**
("How many Sacraments hath Christ ordained…" → Baptism → the Lord's Supper) — the
famous `git diff v1559 v1604` insert. (An earlier growth is visible at
`git diff v1549 v1552`, where 1552 expands the Decalogue to its full scriptural
form and adds the Exodus preamble.)

| Edition | Catechism source | Form |
|---|---|---|
| 1549 | `1549/Confirmation_1549.htm` (bundled) | pre-1604 (no Sacraments) |
| 1552 | `1552/Confirmation_1552.htm` (bundled) | pre-1604; full Decalogue + Exodus preamble added |
| 1559 | `1559/Confirmation_1559.htm` (bundled) | pre-1604 (no Sacraments) |
| 1604 | derived from the justus `1559` page (which appends the captioned "added in 1604" block) | **Sacraments section added** |
| 1662 | CoE `catechism` | with Sacraments; `BCP 1662` |
| 1637 | `Scotland/Confirmation_1637.htm` (bundled) | with Sacraments; title adds "throughout the whole Church of Scotland" |
| 1789 | `1789/Catechism.htm` (standalone) | American form: "My Sponsors in Baptism", "the civil authority"; with Sacraments; keeps its own catechizing rubrics |
| 1892 | identical to 1789 (justus note; confirmed vs `1892/Catechism&Confirm_1892.pdf`) | inherits 1789 (reviewed-unchanged) |
| 1928 | `1928/Confirnation.htm` (bundled) | recast as the **Offices of Instruction** (two Offices) |
| 1979 | `bcpprayr.txt` | recast as **An Outline of the Faith** (contemporary Q&A) |

Scope notes: the American 1789 catechism is a standalone page (not bundled with
Confirmation) and diverges from the English 1662 text — "My Sponsors in Baptism"
for "Godfathers and Godmothers", "To honour and obey the civil authority" for "the
King, and all that are put in authority under him", and "our spiritual enemy" for
"ghostly enemy"; it also prints its own concluding catechizing rubrics (kept here
under `## The Rubrics`, since the separate 1789 confirmation file does not carry
them). The **1892** catechism is identical to 1789 (justus states so; confirmed
against the 1892 `Catechism&Confirm` PDF, a WordPerfect scan with minor OCR noise
but no substantive change), so it inherits 1789. The 1928 American book recasts the
Catechism as the "Offices of Instruction" — two Offices with prayers, hymn rubrics,
and Minister/People responses woven through the Q&A; it is represented under
`catechism.md` as the 1928 lineal form (the recasting is the meaningful `v1892→v1928`
diff), and its own headings are the anchors. The 1979 "Outline of the Faith" is
reflowed mechanically from the public-domain ASCII e-text (`bcpprayr.txt`) and, like
the other 1979 files, keeps its e-text typos verbatim pending a scan check.

Access note: justus.anglican.org serves its content over plain **HTTP**; its HTTPS
virtual host currently returns 404 for every path (an old Apache/OpenSSL cert setup),
so all justus fetches for this wave used `http://` URLs.

## Ordinal (Wave 8)

The Ordinal — the Preface, the Ordering of Deacons, the Ordering of Priests, and the
Consecration of Bishops — across the nine editions that carry it (English
1549/1552/1559/1604/1662, American 1789/1892/1928/1979). **Absent from the Scottish
line:** the 1637 book contained no Ordinal (Laud's Liturgy omitted it), and 1764/1929
are Communion-only, so all four services are `absent:` at 1637 and inherited-absent
thereafter. The 1549 node carries the separately-published **1550 Ordinal** (bound into
the book only from 1552) — see NOTICE.md for that placement decision.

| Edition | Source | Notes |
|---------|--------|-------|
| 1549 | justus `1549/{Deacons,Priests,Bishops}_1549.htm` (synoptic) | = the 1550 Ordinal; base readings |
| 1552 | same synoptic page, 1552 apparatus | delivery of instruments (porrection) removed; vesture stripped |
| 1559 | same synoptic page, 1559 apparatus | anti-papal Litany clause removed; King's Oath → Queen's Oath |
| 1604 | derived from 1559 (no justus page) | Deacons/Bishops only: Elizabeth→James, Queen→King in the oaths |
| 1662 | CoE website (`form-and-manner-making-ordaining` + three sub-pages) | forms gain the order-naming; preface gains the episcopal-succession clause |
| 1789 | justus `1789/{Deacon,Priests,Bishops}_1789.htm` | King's-Supremacy oath dropped → Promise of Conformity; dual priest form |
| 1892 | derived from 1789 (`1892/Ordinations_1892.pdf` cross-check) | Nicene-Creed rubric additions; printed hymn → cross-reference |
| 1928 | justus `1928/Ordinal.htm` | adds the Litany for Ordinations + a second metrical Veni Creator |
| 1979 | `bcpepscl.txt` via transform | contemporary-language rites (own section headings) |

## Front-matter (Wave 9)

The prefatory matter — **The Preface**, **Concerning the Service of the Church**,
**Of Ceremonies (why some be abolished and some retained)**, and the American
**Ratification** — under `front-matter/`. Presence differs sharply by line and is
the point of the wave:

- **Concerning the Service of the Church** is the 1549 original Preface ("There was
  never any thing by the wit of man..."), titled simply *The Preface* through 1604 and
  **renamed** *Concerning the Service of the Church* in 1662. English 1549-1662 and
  Scottish 1637 (a wholly distinct Scottish preface); the American line **drops** it at
  1789 and **re-adds** a new modern one at 1979.
- **The Preface** ("It hath been the wisdom of the Church of England...") is a **1662
  addition** (absent 1549-1604); the American line has its **own** Preface ("It is a
  most invaluable part of that blessed liberty...", 1789+), inherited 1892/1928/1979.
- **Of Ceremonies** runs from 1549 (printed at the *end* of the 1549 book, moved to the
  *front* in 1552 — a book-order change, see NOTICE) through 1662 and Scottish 1637;
  **absent from the American line**.
- **The Ratification** is **American only** (1789+).
- 1764/1929 (Communion-only Scottish line) carry no front-matter.

The title pages, Tables of Contents, Kalendars, the 1559 Act of Uniformity, and the
1637 royal Proclamation that share these source pages are book-structure / tables and
are out of Wave-9 scope; the 1979 "Historical Documents of the Church" (Articles of
Religion etc.) is back-matter, likewise out of scope.

| Edition | Source | Notes |
|---------|--------|-------|
| 1549 | justus `1549/front_matter_1549.htm`, `1549/Of_Ceremonies_1549.htm` | original Preface + Of Ceremonies (Of Ceremonies at the book's end) |
| 1552 | justus `1552/Front_matter_1552.htm` | Preface adds the Archbishop clause + three closing directives; Of Ceremonies now at the front (inherits 1549 text) |
| 1559 | justus `1559/front_matter_1559.htm` (reviewed) | Preface/Of Ceremonies unchanged from 1552 → inherited |
| 1604 | derived (reviewed-unchanged) | front-matter unchanged from 1559 → inherited |
| 1662 | CoE website (`preface`, `concerning-service-church`, `concerning-ceremonies-why-some-be`) | new Preface added; 1549 Preface renamed *Concerning the Service of the Church* |
| 1637 | justus `Scotland/front_matter_1637.htm` | distinct Scottish Preface (names James & Charles); Of Ceremonies (two source leaves missing — flagged) |
| 1789 | justus `1789/FrontMatter_1789.htm` | American Preface + Ratification; drops Concerning-the-Service and Of Ceremonies |
| 1892 | inherited from 1789 (`1892/BCP_1892.htm` cross-check) | Preface + Ratification unchanged |
| 1928 | inherited from 1789 (`1928/Front_Matter_1928.pdf` cross-check) | Preface + Ratification unchanged (1928 front-matter PDF has a garbled font layer; relied on cross-source stability) |
| 1979 | `bcpoffce.txt` via transform | re-adds a modern *Concerning the Service of the Church*; Preface + Ratification are the 1789 documents reprinted (inherited) |

