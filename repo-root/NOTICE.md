# NOTICE — Provenance and copyright of the texts

The software/tooling in this repository is under the MIT `LICENSE`. **The
prayer-book texts under `texts/` are not.** This file records their provenance
and copyright status. See `SOURCES.md` for per-file source URLs and retrieval
dates.

## Summary of copyright status by edition

| Edition | Line | Status | Notes |
|--------:|------|--------|-------|
| 1549 | English | Public domain | First Edwardian book. |
| 1552 | English | Public domain | Second Edwardian book. |
| 1559 | English | Public domain | Elizabethan Settlement. |
| 1604 | English | Public domain | Jacobean / Hampton Court. |
| 1662 | English | Public domain **outside the UK**; **Crown copyright within the UK** | See the 1662 note below. |
| 1637 | Scottish | Public domain | "Laud's Liturgy". |
| 1764 | Scottish | Public domain | Scottish Communion Office. |
| 1929 | Scottish | Public domain | Scottish Book of Common Prayer. |
| 1789 | American | Public domain | First American book; US editions were PD on publication. |
| 1892 | American | Public domain | |
| 1928 | American | Public domain | |
| 1979 | American | Public domain | The 1979 text is explicitly public domain. |

## The 1662 Book of Common Prayer — Crown rights acknowledgment

The 1662 Book of Common Prayer is in the public domain in most of the world.
**In the United Kingdom, rights in the 1662 text are held by the Crown** in
perpetuity by royal prerogative, and are administered by Cambridge University
Press (and, for Bible content, the King's/Queen's Printer). Reproduction within
the UK is by permission of the Crown's patentee.

In acknowledgment of that convention, files transcribing the 1662 edition carry
the acknowledgment string:

```
BCP 1662
```

in their header, and the string is recorded here as required:

**BCP 1662**

## Texts deliberately EXCLUDED (still under active copyright)

The following are **not** included anywhere in this repository, on any branch:

- Church of England *Common Worship* (2000).
- Church of Ireland Book of Common Prayer (2004).
- Modern Canadian, Australian, and other 20th–21st-century non-US revisions.
- The proposed English 1928 "Deposited Book" (included only if a clear
  public-domain source is confirmed; otherwise omitted and noted in
  `SOURCES.md`).

If you believe any text here is included in error, please open an issue.

## Genealogical influence note

The American 1789 Communion Office borrowed substantially from the Scottish
1764 Communion Office (the "Wee Bookie"). Whether or not the git graph models
this as an explicit merge (see the brief §6D), the influence is real and is
recorded here for the historical record.

## History rebuilds

The published branches and tags are build artifacts, regenerated from the
`authoring` source whenever a service is added or deepened. Rebuild log:

- **2026-08-11** — Wave 1: Morning Prayer brought to full Tier-1 across all ten
  daily-office editions.
- **2026-08-12** — Wave 2: Evening Prayer added at full Tier-1 across the same
  ten editions (1764/1929 remain Communion-only).
- **2026-08-12** — Wave 3: The Litany added at full Tier-1 across the same ten
  editions (1764/1929 remain Communion-only). Litany scope is the Litany proper
  through the Grace; appended occasional/state prayers are deferred.
- **2026-08-12** — Wave 4: Holy Communion added at full Tier-1 across **all twelve**
  editions (English 1549–1662, Scottish 1637/1764/1929, American 1789–1979). The
  Scottish 1764 and 1929 opening slices were deepened to the full office. Flagship
  diffs: the 1549→1552 restructuring, the Gloria in Excelsis moving to the end, the
  words of administration, and the Black Rubric (Declaration on Kneeling) appearing
  in 1552, vanishing in 1559, and returning in 1662; the American 1789 rite carries
  the Scottish 1764 eucharistic prayer (`git diff v1764 v1789`).
- **2026-08-12** — Wave 5: the Christian-initiation offices added at full Tier-1.
  Four services under `occasional-offices/` — Public Baptism of Infants, Private
  Baptism, Baptism of Those of Riper Years, and Confirmation. Public/Private
  Baptism and Confirmation run across the same ten daily-office editions (English
  1549–1662, Scottish 1637, American 1789–1979); 1764/1929 remain Communion-only,
  so they carry none of them. Baptism of Riper Years is a 1662 addition, carried
  into the American line (1789/1892) and folded into a single Holy Baptism office
  by 1928/1979 (so it exists as a separate office only at 1662/1789/1892). Flagship
  diffs: the 1552 baptismal simplification (`git diff v1549 v1552 --
  texts/normalized/occasional-offices/public-baptism.md` — exorcism, chrisom, and
  anointing removed, signing with the cross moved after baptism); the 1604 Hampton
  Court restriction of private baptism to a lawful minister; the 1549→1552
  Confirmation change (the signing with the cross gives way to the "Defend, O Lord"
  imposition of hands). The 1979 offices were reflowed mechanically from the
  public-domain ASCII e-text (source → script → file). (The 1549 "Blessing of the
  Font" prayers — the monthly font-hallowing printed after private baptism — were
  since transcribed, appended to the 1549 Private Baptism file under `## The
  Blessing of the Font`; present at 1549 only, dropped in 1552. See the Wave-9
  rebuild entry below.)
- **2026-08-13** — Wave 6: the pastoral occasional offices added at full Tier-1.
  Five services under `occasional-offices/` — Matrimony, the Visitation of the Sick
  (with the Communion of the Sick), the Burial of the Dead, the Churching of Women,
  and the Commination. Matrimony, Visitation, and Burial run across the ten
  daily-office editions (English 1549–1662, Scottish 1637, American 1789–1979);
  1764/1929 remain Communion-only, so they carry none of them. Churching runs across
  them too — the 1979 book replaces it with "A Thanksgiving for the Birth or Adoption
  of a Child", represented under the same file. The **Commination is an
  English/Scottish office (1549–1662 + 1637) that the American line drops**: it is
  modelled as a clean deletion at 1789 (`git diff v1662 v1789 --
  texts/normalized/occasional-offices/commination.md`), which 1892/1928/1979 inherit;
  the 1979 book has no Commination and its nearest relative (the Ash Wednesday
  liturgy) is deliberately not mapped. Flagship diffs: the Reformation stripping of
  the Burial office in 1552 (`git diff v1549 v1552 --
  texts/normalized/occasional-offices/burial.md` — the 1549 requiem's commendation of
  the soul, prayers for the dead, office of psalms, and Communion of the dead removed,
  leaving the graveside form, with the committal and prayer rewritten to remove prayer
  for the dead); the 1549→1552 Matrimony changes (the "gold and silver" dropped from
  the giving of the ring, the blessing reworded, the apocryphal Tobias/Raphael
  reference removed); and the 1549 Commination's title as "The First Day of Lent,
  commonly called Ash-Wednesday". 1604 changes were derived from the justus 1559
  apparatus (Burial "unto"→"into"; Churching "Priest"→"Minister"; Matrimony,
  Visitation, and Commination unchanged and inherited). 1979 offices were reflowed
  mechanically from the public-domain ASCII e-text `bcpastrl.txt` (source → script →
  file), including the Burial's Rite One (office body) and Rite Two (separate section);
  the American 1892 offices, which justus serves only as text-layer PDFs, were
  extracted with pypdf layout mode. A handful of genuine e-text/print defects are kept
  verbatim and flagged inline (`<!-- VERIFY -->`) — see `SOURCES.md`.
- **2026-08-13** — Wave 7: the Catechism added at Tier-1, as
  `occasional-offices/catechism.md` (a sibling of Confirmation, with which it is
  printed). It runs across the editions that carry it — English 1549–1662, Scottish
  1637, American 1789–1979; 1764 is Communion-only and 1929 inherits that absence.
  The catechism file holds the title and the Question-and-Answer body; the framing
  and catechizing rubrics remain with the Confirmation office. The flagship feature
  is that the Catechism **grows**: the 1604 book adds the whole Sacraments section
  ("How many Sacraments hath Christ ordained…" → Baptism → the Lord's Supper),
  authorized at the Hampton Court Conference — a clean insert at `git diff v1559
  v1604 -- texts/normalized/occasional-offices/catechism.md`; an earlier growth
  appears at 1552, which expands the Decalogue to its full scriptural form and adds
  the Exodus preamble. The 1604 text was derived from the justus 1559 Confirmation
  page, which appends the "added in 1604" material under a caption. The American line
  recasts the Catechism twice: the 1928 book as the **Offices of Instruction** (two
  Offices with prayers and Minister/People responses woven through the Q&A), and the
  1979 book as **An Outline of the Faith** (a contemporary commentary on the creeds),
  reflowed mechanically from the public-domain ASCII e-text `bcpprayr.txt` (source →
  script → file). A few OCR/e-text readings are kept verbatim and flagged inline
  (`<!-- VERIFY -->`) — see `SOURCES.md`.
- **2026-08-14** — Wave 8: the Ordinal added at Tier-1, under `ordinal/` as four
  services — `preface`, `ordering-deacons`, `ordering-priests`, and
  `consecration-bishops`. (Published 2026-08-14; tips main `8675fb8` · scottish
  `f004784` · american `36b8e6e`.) It runs across the nine editions that carry it (English
  1549/1552/1559/1604/1662, American 1789/1892/1928/1979). **Placement decision (the
  1549 nuance):** the Ordinal was published *separately* as the **1550 Ordinal** and
  was bound into the Prayer Book only from 1552; the 1549 book proper contained no
  Ordinal. It is represented here at the **v1549 node**, sourced from the standalone
  1550 Ordinal (justus files it under `/1549/` as the synoptic "Ordinal from the
  1549, 1552 and 1559 Books of Common Prayer", title-page 1550). This preserves the
  1550→1552 revision as a `git diff v1549 v1552` and keeps the 1550 witness; the
  alternative (first representing it at 1552) would discard it. **Scottish line:** the
  Ordinal is **absent** from the whole Scottish line — the 1637 book (Laud's Liturgy)
  contained no Ordinal, and 1764/1929 are Communion-only; all four services are
  `absent:` at 1637 and inherited-absent thereafter. The English 1549/1552/1559 texts
  were hand-authored from the justus synoptic pages (a three-way apparatus: 1550 base
  + "added 1552/1559" inserts + labelled 1552/1559 branches); 1604 was derived from
  1559 (sovereign name and oath only); 1662 came from the Church of England website;
  the American 1789/1928 from justus and 1892 by derivation from 1789; and 1979 by
  transform script from the public-domain ASCII e-text `bcpepscl.txt` (source →
  script → file). Flagships: the **delivery of instruments (porrection) removed in
  1552** (`git diff v1549 v1552 -- texts/normalized/ordinal/ordering-priests.md`), the
  **anti-papal clause and King's-Supremacy oath dropped in 1559**, the **explicit
  order-naming added to the forms in 1662** (`git diff v1604 v1662`), and the
  **American Promise of Conformity replacing the oath in 1789** (`git diff v1662
  v1789 -- texts/normalized/ordinal/consecration-bishops.md`). A handful of OCR/print
  readings are kept verbatim and flagged inline (`<!-- VERIFY -->`) — see `SOURCES.md`.

- **2026-08-14** — Wave 9: the front-matter added at Tier-1, under `front-matter/`
  as four pieces — `preface`, `concerning-the-service`, `of-ceremonies`, and
  `ratification`. Presence differs by piece and by line, and that divergence is the
  point of the wave.
  **Slot / identity decisions:** (1) `concerning-the-service` is the 1549 original
  **Preface** ("There was never any thing by the wit of man…"); it is *titled* "The
  Preface" through 1604 and **renamed** "Concerning the Service of the Church" in
  1662. It is kept under one filename across editions so the 1662 rename reads as a
  heading change rather than a delete-plus-add (`git diff v1604 v1662 --
  texts/normalized/front-matter/concerning-the-service.md`). (2) `preface` is the
  **1662 addition** ("It hath been the wisdom of the Church of England…"), absent
  1549–1604, so `git diff v1604 v1662 -- .../front-matter/preface.md` is a clean
  insertion; the American line carries its **own** distinct Preface ("It is a most
  invaluable part of that blessed liberty…", 1789), which replaces the English one at
  the fork (`git diff v1662 v1789`). (3) The **American line drops** both
  `concerning-the-service` and `of-ceremonies` at 1789 (clean deletions); the 1979
  book **re-adds** a modern `concerning-the-service`. (4) `ratification` is **American
  only** (1789+). (5) The **Scottish 1637** book opens with its **own distinct
  Preface** ("The Church of Christ hath in all ages had a prescript forme of Common
  prayer…", naming King James and Charles), which occupies the same opening-preface
  slot — so `git diff v1604 v1637 -- .../front-matter/concerning-the-service.md`
  shows the English preface wholly replaced by the Scottish one.
  **Placement note (Of Ceremonies):** in the **1549** book "Of Ceremonies" was printed
  at the **end** of the volume; from **1552** it was moved to the **front**. This
  build models it as one `of-ceremonies` file whose text is essentially unchanged
  1549→1552 (the move is a book-order change, not a textual one), so the placement
  shift is recorded here rather than as a diff. 1764/1929 (Communion-only) carry no
  front-matter.
  **Out of scope this wave** (recorded, not transcribed): the title pages, Tables of
  Contents, and Kalendars that share these source pages; the **1559 Act of
  Uniformity** and the **1637 royal Proclamation** printed before their prefaces; and
  the 1979 **"Historical Documents of the Church"** (Articles of Religion, etc.),
  which is back-matter. These are book-structure or tables and belong to later waves.
  **Sourcing:** English 1549/1552 from the justus front-matter pages; 1559/1604
  reviewed as unchanged and inherited; 1662 from the Church of England website; the
  Scottish 1637 from justus (`Scotland/front_matter_1637.htm`); American 1789 from
  justus (`1789/FrontMatter_1789.htm`), 1892/1928 inherited as the reprinted 1789
  documents (the 1928 front-matter PDF has a garbled font layer — cross-source
  stability was relied on), and the 1979 `concerning-the-service` by transform script
  from the public-domain ASCII e-text `bcpoffce.txt` (source → script → file). A few
  OCR/print readings are kept verbatim and flagged inline (`<!-- VERIFY -->`).
  (Published 2026-08-14; tips main `da4fa1d` · scottish `2474e65` · american
  `4a722f6`.) This publish also carries a completed Wave-5 deferral — the **1549
  Blessing of the Font** (the monthly font-hallowing printed after Private Baptism),
  appended to the 1549 Private Baptism file (present at 1549 only). **Still deferred:**
  the Litany-appended **Prayers and Thanksgivings** — the occasional prayers (rain,
  fair weather, dearth, war, plague), the appended state prayers (royal progeny,
  clergy), and the thanksgivings — which the sources print as a growing,
  edition-variable block after the Litany (1552 onward) and which the 1662 and
  American books gather into a separate "Prayers and Thanksgivings upon several
  Occasions" section; these are their own future wave, not part of the Litany file.
- **2026-08-31** — Wave 10a: the **Collects, Epistles and Gospels** (the "propers")
  for Advent through the Sundays after the Epiphany, across the ten editions that
  carry them (absent from the Communion-only Scottish 1764/1929). Wave 10 is split
  into seasonal sub-waves, each published separately: 10a Advent–Epiphany, 10b
  pre-Lent–Easter Even, 10c Easter–Trinity, 10d the Holy Days.
  **Reading depth is a deliberate scoping choice:** each occasion carries its
  Collect(s) in full, and the Epistle and Gospel as their appointed **citation
  only**. The reading bodies are the Bible translation (Great Bible → King James →
  later versions), a separate work from the Prayer Book; the Prayer-Book signal is
  the collect wording and the appointed pericope, which the citation captures. The
  citation is written to the precision the book itself prints — chapter only for
  1549–1559, chapter and initial verse from 1662 and in the American line — so a
  closing verse supplied only by a modern editor never manufactures a diff.
  **1979 is mapped by an explicit crosswalk**, not by calendar number: 1979
  renumbers the year, and most historic collects that survive in it land on days
  outside this season (Advent 2's at Proper 28, Epiphany 1's at Proper 10). Its
  traditional-language collect carries the lineage diff and the contemporary one
  sits alongside; because 1979 appoints three reading sets per day under the
  three-year lectionary, it carries no single Epistle and Gospel, and those tables
  are deferred to the lectionary wave.
  **Two gaps are recorded rather than filled:** no allow-listed source prints the
  1604 propers, so the initial verse numbers that entered the citations in 1604 are
  not represented; and the public-domain 1979 e-text lost three collects in its
  1993 keying, which are flagged inline and not reconstructed.

- **2026-08-31** — Wave 10b: the propers for **pre-Lent through Easter Even**
  (Septuagesima, Sexagesima and Quinquagesima; Ash Wednesday; the five Sundays in
  Lent; Holy Week; Easter Even), 16 occasions across the same ten editions.
  Notable features of the books, represented rather than smoothed away: several
  days in Holy Week carry **no proper Collect** (the Sunday next before Easter's
  serves the week), so those cells hold only their appointed readings, and the
  Epistle on those days is an Old Testament lesson, which the books label "For the
  Epistle". Good Friday carries three Collects. The American line prints no Collect
  for the Tuesday and Wednesday before Easter until **1928**, which adds them.
  The **1979 book abolishes the pre-Lent "Gesima" Sundays** altogether; that is a
  genuine deletion, recorded as an explicit absence rather than mapped onto some
  other day's collect. 1979 also renames the days it keeps (Monday in Holy Week,
  Maundy Thursday, Holy Saturday), which shows as a heading change on the same
  file.
- **2026-08-31** — Wave 10c: the propers for **Easter Day through the Twenty-Fifth
  Sunday after Trinity**, 39 occasions across the editions that carry them.
  **A representational caveat, recorded because it shapes what the 1979 files
  assert.** The 1979 book does not merely rename the Sundays after Trinity; it
  replaces the reckoning, keying the season to calendar-dated Propers, so no day
  in that season corresponds between the older books and 1979. Where a Sunday
  after Trinity's collect demonstrably survives in 1979 at a Proper, this repo
  places the 1979 collect at the historic day's file, so that the modernization of
  the collect can be read as a diff. The cost is that such a file attaches a 1979
  collect to a day the 1979 book does not observe, and that the 1979 Propers are
  represented only through the historic days they map onto. Every file affected
  says so inline. **This representation is provisional and expected to be
  revised.** Where the evidence for descent is weak — collects share stock
  openings, so a shared opening alone proves nothing — no mapping was made at all,
  and the day is recorded as absent from 1979 rather than guessed at.
## A note on transcription

These transcriptions follow public-domain source transcriptions (principally
Charles Wohlers' collection at the Society of Archbishop Justus) cross-checked,
where practical, against public-domain page scans. Transcription involves
editorial judgment; passages whose reading is uncertain are marked inline with
`<!-- VERIFY: ... -->` comments and listed in `SOURCES.md`.
