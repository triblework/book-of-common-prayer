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
centres on the **Daily Office — Morning Prayer**, from the opening of the office
through the Venite rubric, which is where the tradition's most famous changes
live (e.g. the 1552 penitential introduction, the 1662 Lord's Prayer doxology).
The Scottish 1764/1929 commits instead carry the **Holy Communion** office
(exhortation + offertory), because the 1764 book was a Communion Office only.
Deeper service bodies, the remaining occasional offices, the catechism, the
ordinal, and the Psalter are **not yet transcribed** and are tracked as stretch
work (brief §13). Where an edition could not be sourced cleanly, that is stated
explicitly below rather than filled with invented text.

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
| 1979 | **not transcribed this pass** | The 1979 (public domain) is served by dynamic/JavaScript sites (bookofcommonprayer.net) or day-generated pages (missionstclare.com) that the static scraper cannot capture cleanly; transcribing from memory is disallowed. The commit documents the gap (notably Rite II's "Lord, open our lips / And our mouth shall proclaim your praise"). TODO: source a clean 1979 Rite I / Rite II transcription. |

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

## Uncertain passages (`<!-- VERIFY -->`)

Each is flagged inline in the text and should be checked against a page scan.

| File / edition | Reading in source | Note |
|----------------|-------------------|------|
| 1552 Morning Prayer | `Psalm ii.` | Verse is Psalm 51:3; likely a `li`→`ii` printer error. |
| 1552 Morning Prayer | `Jerem. ii.` | Verse is Jeremiah 10:24; 1559 carries the same reading. |
| 1559 Morning Prayer | `Lord, make haste to helpe us` | 1552 reads `O Lord`; the missing `O` may be a transcription slip. |
| 1637 (Scottish) Morning Prayer | `Ps. 28` | Sentence is Proverbs 28:13. |
| 1764 (Scottish) Communion | `Matth. vi. 9. 20` | Passage is Matthew 6:19-20; `9` likely for `19`. |
| 1929 (Scottish) Communion | `Acts 20. 85` | Verse is Acts 20:35; `85` likely a scan error. |
| 1789 (American) Morning Prayer | several roman-numeral citations | The justus 1789 page had OCR damage in citations (e.g. `Psalm ii 17` for Psalm 51:17); read against the parallel 1662 sentences. |
| 1662 Morning Prayer (Prayer for the King's Majesty) | `King CHARLES` | The CoE source serves the reigning monarch (Charles III); the 1662 book as first printed named the then-sovereign (Charles II). Reign-dependent; reconcile against a dated 1662 scan. |
| 1662 Morning Prayer (Prayer for the Royal Family) | `Queen Camilla, William Prince of Wales, the Princess of Wales` | The CoE source serves the current Royal Family; the 1662 book named the then-Royal Family. Reign-dependent; reconcile against a dated 1662 scan. |
