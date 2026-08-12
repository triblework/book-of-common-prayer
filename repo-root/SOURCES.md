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
demonstrates the diff mechanism end-to-end. The **transcribed text** presently
covers the **Daily Office — Morning Prayer and Evening Prayer — the Litany, and
Holy Communion** at full Tier-1 depth across every edition that has them, which
is where the tradition's most famous changes live (e.g. the 1552 penitential
introduction, the 1662 Lord's Prayer doxology, the 1789 American recasting of the
evening canticles, and — in Holy Communion — the 1549→1552 restructuring, the
moving Gloria in Excelsis, the changing words of administration, and the Black
Rubric appearing/vanishing/returning across 1552/1559/1662). Morning/Evening
Prayer and the Litany run across the ten daily-office editions; **Holy Communion
runs across all twelve** (the Scottish 1764 "Wee Bookie" and 1929 are
Communion-only, so they carry only that office). The remaining occasional
offices, the catechism, the ordinal, and the Psalter are **not yet transcribed**
and are tracked as stretch work (brief §13). Where an edition could not be
sourced cleanly, that is stated explicitly below rather than filled with invented
text.

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
