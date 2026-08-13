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
covers the **Daily Office (Morning and Evening Prayer), the Litany, Holy
Communion, the Christian-initiation offices (Baptism and Confirmation), and the
pastoral occasional offices (Matrimony, the Visitation of the Sick, the Burial of
the Dead, the Churching of Women, and the Commination)** at full Tier-1 depth
across every edition that has them — where the tradition's most famous changes
live (e.g. the 1552 penitential introduction; the Holy Communion 1549→1552
restructuring, the moving Gloria in Excelsis, the changing words of
administration, and the Black Rubric appearing/vanishing/returning across
1552/1559/1662; the 1552 baptismal simplification; and the Reformation stripping
of the Burial office in 1552). Morning/Evening Prayer, the Litany, Baptism,
Confirmation, Matrimony, Visitation, Burial, and Churching run across the ten
daily-office editions; the Commination is English/Scottish only (the American line
drops it); **Holy Communion runs across all twelve** (the Scottish 1764 "Wee
Bookie" and 1929 are Communion-only, so they carry only that office). The
catechism, the ordinal, the front-matter, the seasonal Collects/Epistles/Gospels,
and the Psalter are **not yet transcribed** and are tracked as later waves. Where
an edition could not be sourced cleanly, that is stated explicitly below rather
than filled with invented text.

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

## Occasional offices — Baptism family & Confirmation (Wave 5)

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
after the private-baptism office) and the Catechism bodies bundled on the
1549/1559/1928 Confirmation pages are deferred to later waves.


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
