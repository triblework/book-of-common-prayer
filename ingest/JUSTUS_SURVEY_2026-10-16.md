# Workstream D — justus.anglican.org /resources/bcp/ survey (2026-10-16)

Assembled by the coordinator from the sub-agent's drafts (d0, d2, d3, d4, rulings, d1_tables). Its summary was delivered as a message and is reproduced in the coordinator's session; the inventory table is the last section.


---

# D_REPORT — Workstream D: survey of justus.anglican.org /resources/bcp/ (2026-10-16)

READ-ONLY survey. No transcription, no cell changes, no file written inside any
repo checkout. Everything below is structure, sizes and counts; no liturgical
text is quoted beyond a few words of a flag's own reading.

## 1. What I did

- Read COMMON_RULES.md, RULINGS.md (all, with R2, R3, R6, R7, R11, R12, R14,
  R15 in mind), HANDOFF.md §8, repo-root/SOURCES.md (all, including "Recorded
  gaps in the tables"), `tools/scrape.py` (ALLOWED_HOSTS: justus,
  commons/upload.wikimedia, loc.gov, churchofengland.org) and
  `ingest/w20_fetch.py`; listed `scrape-cache/` (395 files before this survey,
  ~190 of them justus).
- Walked the index pages, every request through `tools/scrape.py`'s own
  functions (allow-list `_check_host`, `_robots_ok`, its user agent, ≥1.1 s
  between requests, single process): the bcp root, `bcp.htm` (US),
  `england.htm`, `Scotland.htm`; the edition indexes 1549, 1552, 1559, 1662,
  1789, 1892, 1928, `Scotland/BCP_1637.htm`, `Scotland/Scotland.htm` (1929),
  `Scotland/wee_bookies.html` (1764 and siblings), `ASCII_1979.htm`,
  `formatted_1979.htm`, `Other_1979.htm`, `Standard1979.htm`; and the
  sub-indexes `1549/PDF_Notes.htm`, `1559/PDF1623.htm`, `1662/baskerville.htm`,
  `Sturt/index.html`, `1662/1775.html`, `1662/statutory.htm`,
  `1662/Orig_manuscript/index.html`, `1789/1790/index.htm`,
  `1789/1790/folio.html`, `1789/1795 folio/index.html`,
  `1789/1845Standard/index.html`, `1789/1871Standard/index.htm`,
  `1892Standard/index.htm`, `1928Standard/Standard.htm`, `Whats_new.htm`
  (32 index pages; GET, cached under `https://` keys).
- HEADed every justus URL those pages link (manual redirect following, each hop
  re-checked against the allow-list and robots), plus the page photographs
  linked from the cached edition pages. Downloaded only files under 5 MB that
  were needed to classify or locate something (listed in §4).
- Compared every pre-existing cached copy with today's HEAD (byte length after
  re-encoding the cached text to the page's own charset with line endings
  preserved), and today's index pages with their cached copies (diff).
- Helpers (scratchpad only, not in any repo):
  `scratchpad/d_survey/dsurvey.py` (page/head/headfile), `cachecheck.py`,
  `cmpcache.py`, `classify_rules.py`, `gen_d1.py`, `pdfclass.py`
  (pages / image XObjects / fonts / text density, run with `python3 -I`),
  `render.py` (qlmanage renders of CACHED scans into `scratchpad/d_render/`),
  `fetch_small.py` (size-checked downloads through `ingest/w20_fetch.py`).
  Raw HEAD records: `scratchpad/d_survey/heads.jsonl`; link lists:
  `scratchpad/d_survey/idx/*.links`.

---

## D2. Mapping: what each page scan (or different-class file) could settle

Open inline flags this session (`grep -rn VERIFY editions/<year>` in the
checkout): 1549 37 · 1552 40 · 1559 64 · 1604 25 · 1637 21 · 1662 9 · 1764 3
· 1789 28 · 1892 43 · 1928 25 · 1929 2 · 1979 127. In 1549, 1552 and 1559, 25
of those flags each are the same propers title-expansion note ("added in late
1500's", represented as entering at 1559) on the same 25 occasions.

### D2.1 Already cached — no fetch needed

| Find | Class | Covers | Could settle |
|---|---|---|---|
| `1892Standard/1892standard.pdf` 70,097,195 B (cached 2026-09-11, byte-identical today) | PAGE SCAN, 596 pp, JBIG2/DCT, no text layer | the whole 1892 Standard Book; **"A Table of Lessons for <month>", one month a page, January = scan p. 12 … December = scan p. 23** (checked this session by rendering pp. 11, 12, 20, 23, 24) | the **1892 Kalendar recorded gap** (row structure lost in the HTML); up to **42 of v1892's 43 flags** (not Psalm 1:3 "water-side", which this scan breaks across a line). The keyed `1892Standard/bcp.pdf` (576 pp, cached) has NO Calendar — its p. 9 Selections is followed by p. 10 Morning Prayer — so the scan is the only structured 1892 Kalendar source |
| `1928/BCP1929.pdf` 42,365,481 B (cached, byte-identical) | PAGE SCAN, 319 two-up JPX spreads + hidden OCR | the original 1928 printing, whole book incl. Psalter | **22 of v1928's 25 flags** (EP 3, HC 3, baptism 2, burial 2, confirmation 1, propers 11); the 3 Psalter mediants are better done from the 1952 facsimile (Q4) |
| `1928/BCP1936.pdf` 36,578,675 B (cached) | PAGE SCAN | 1936 printing | corroboration only (a later printing) |

### D2.2 The 1789 book (American line) — first page scans of v1789 itself

| Find | Class / printing | Contains | Could settle |
|---|---|---|---|
| `1789/1795%20folio/services.pdf` 39,140,350 B | PAGE SCAN + uncorrected OCR; Hugh Gaine, NY, 1795 (Griffiths 1795/11), complete but for the title page; MP/EP pages damaged and repaired | "All Services (i.e. everything else)" — so the front matter (Psalter rubric with the **Proper Psalms on certain days**, the **Calendar/Tables of Lessons**), offices, Ordinal | the **two Proper Psalms leads** (Ascension evening `103` vs 108; Good Friday evening `64` vs 69 — 2 cells, unflagged); the **November Kalendar columns** (Morning 1 + Evening 1 × 30 days = 60 blank cells, flag `editions/1789/tables/calendar.md:331`); the other **27 v1789 flags** (Litany 3, Ordinal 4, baptism of riper years 5, visitation 4, private baptism 2, burial 2, EP 2, MP 1, confirmation 1, churching 1, HC 1, preface 1) |
| `1789/1795%20folio/psalms.pdf` 40,018,577 B | PAGE SCAN, same book | the Psalter + the Selections of Psalms | **the 1789 Psalter recorded gap** (R2: "reopened by nothing short of a source for that edition itself" — this is one; see RULINGS NEEDED 2); the 1789 Selections (no flags) |
| `1789/1795%20folio/readings.pdf` 37,967,621 B | PAGE SCAN, same book | Collects, Epistles & Gospels | no open v1789 propers flags; corroboration of `collects_epistles_gospels_1789&1892.htm` only |
| `1789/1790/1790folio.pdf` 71,982,918 B | PAGE SCAN + uncorrected OCR; the 1790 partial folio (Griffiths 1793/12, dated 1790 by a MS note) — the only pre-1793-Standard scan | per its typeset twin `folio_bcp.pdf` (60 pp, downloaded and listed this session): MP, EP, Litany, Prayers, Communion, the Thanksgiving for the fruits of the earth, the ten Selections, and "Portions of Psalms ... on certain Holy-days" (Christmas, Ascension, Whitsunday); the scan adds the **Tables of Lessons** (Gibson, `std_eds1.htm`: "the Calendar of the Lessons") and a page of hymns. **No Psalter rubric and no Proper Psalms table** | MP 1 + EP 2 + Litany 3 + HC 1 = **7 v1789 flags**; the **November lesson columns** (60 cells, 1 flag); NOT the Proper Psalms leads. Gibson notes the 1790 editio princeps misprinted the 29 November second morning lesson, corrected in 1793 — so "which printing" decides the November cells (RULINGS NEEDED 1). Wave 13 rejected only its TEXT LAYER; the images have never been read |
| `1789/EP_1790Folio.jpg` 39,704 B (325×578) | PAGE IMAGE, one page of that 1790 folio (linked from `1789/EP_1789.htm`) | EP: end of a psalm, the Creed rubric, both Creeds | no open flag on the page; useful as a free legibility preview of the 70 MB scan (clean roman type, legible even at this size) |
| `1789/1845Standard/{services,psalms,readings,hymns,1845std}.pdf` 75.8 / 63.7 / 55.6 / 39.7 / 275.0 MB | PAGE SCAN + unproofread OCR; 1845 Standard (Griffiths 1845/36) | the whole book, in parts | corroboration of everything above from a later Standard; not the first choice for v1789 (R7) |
| `1789/1790/front_matter.pdf` 315,522 B (typeset; downloaded) | KEYING (InDesign, Caslon) of the 1790 FIRST EDITION (Griffiths 1790/13) — a different printing from the carrier, which composites eight printings of 1810–1876 | 11 pp; its p. 10 is the Psalter rubric with the Proper Psalms table | it prints Good Friday evening **64**, 88 and Ascension evening 24, 47, **103** — the SAME as the carrier. As a keying it settles nothing (R6), and both keyings are Wohlers'; but it weakens the "4-for-9 / 3-for-8 OCR slip" explanation in HANDOFF §8, since the readings recur in a page-for-page re-creation of the 1790 first printing. The 1795 scan decides |
| `1789/1790/bcp.pdf` 1,332,701 B (typeset; downloaded) | KEYING, same | 207 pp, ends with the Selections | confirms the typeset 1790 has **no Calendar, no Tables of Lessons and no Psalter** (TOC items 5–8 and 29 are not set) |
| `1789/1871Standard/*`, `1789/*_1789.pdf`, `ReadingsA/B.pdf` | KEYING (1871 Standard in DeVinne; a 1865/19 24mo in Century) | — | nothing (same class as the carrier) |

### D2.3 The 1604 text (and 1549–1604 gaps)

| Find | Class / printing | Could settle |
|---|---|---|
| `1559/BCP1623.pdf` 27,779,226 B | PAGE SCAN + uncorrected OCR; 1623 "Bible version" (Griffiths 1623/1) — **James I's reign**; title page, "first few leaves" and Psalter missing; "all of the services are complete"; Bible versions "omit some of the rubrics" | **all 25 v1604 flags**, incl. the 6 reign-dependent ones (Litany `JAMES` `editions/1604/the-litany/litany.md:92`; sovereign's prayer `prayers-and-thanksgivings/for-the-sovereign.md:3`; Ordinal `James`/`Kings` `ordinal/ordering-deacons.md:78,252`, `ordinal/consecration-bishops.md:28`; HC `editions/1604/holy-communion/holy-communion.md:54`); the **1604 propers gap** (1604 inherits 1559; the initial-verse-number change is unrepresented); the 1604 Catechism addition; the **1604 Kalendar + both rubrics** and the 1604 share of **1549–1604 Proper Lessons** only if the missing front leaves spare them (open the PDF's bookmarks first) |
| `1559/BCP1634.pdf` 130,490,854 B | PAGE SCAN; 1634 Barker (index: imperfect, some pages torn/missing) — Charles I's reign | the **1604 Kalendar + both rubrics**, the **1604 share of 1549–1604 Proper Lessons** (R15's reopener), every non-reign-dependent 1604 flag; never the reign-dependent readings |
| `1559/Psalter1634.pdf` 54,704,435 B | PAGE SCAN, the same book's Psalter | the **1604 share of the 1549–1604 Psalter gap** only (R2 bars using it for 1549–1559) |
| `1662/Orig_manuscript/convocation.pdf` 30,359,715 B | PAGE SCAN; the Convocation Book = a printed 1636 BCP marked up by Sancroft in 1661; 1871 reprint (Griffiths 1871/1) of the 1870 photographic facsimile | print layer: the 1604 text as printed 1636 (overlaps BCP1634); pen layer: the 1661 revision — a different-KIND witness for the **three Wave-20 1662 Kalendar flags** (`editions/1662/tables/calendar.md:184,190,234`) and the June page that only Wikimedia's renderer decodes (R14). The deviations report (below) says the 1662 Calendar's lessons "were left as appointed in the 1604 book" — so the print layer bears on 1662's lesson columns too |
| `1559/*.pdf` (typeset; `BCP1559.pdf` 9,969,289 B; per-section 0.1–2 MB) | KEYING of the HTML "adjusted to agree with" a 1634 copy (Griffiths 1634/1) | the carrier for a 1604 pass (as `Calendar&Tables_1928.pdf` was for 1928), not a witness |
| `1559/Catechism_1604.jpg` 34,396 B (340×569) | PAGE IMAGE (printing unstated) | shows the end of the Lord's-Prayer answer and the opening of the 1604 sacraments section; the 1604 flag at `occasional-offices/catechism.md:104` falls on the NEXT page — no flag on this one |

### D2.4 1549, 1552, 1559 — single-page photographs only (no book scan on justus)

No scan of a 1549, 1552 or 1559 book is served (the indexes link archive.org
and Google Books copies, off the allow-list). The 1549/1552 pages link small
photographs. Viewed this session at native size:

| Image | Size / px | On the page | Open flag it bears on |
|---|---|---|---|
| `1549/Priests_1550.jpg` | 101,188 B, 575×998 | 1550 Ordinal, delivery of the Bible and the "Take thou authority" sentence | **`editions/1549/ordinal/ordering-priests.md:196`** (`'where thou shalt be so appointed'`): at native size the 1550 sentence appears to END at "Congregacion." with no such tail |
| `1549/Priests_1552.jpg` | 103,455 B, 580×1049 | the 1552 form of the same page | **`editions/1552/ordinal/ordering-priests.md:190`**: the 1552 page prints the tail. Read together, the two images suggest the tail ENTERS at 1552, i.e. the 1549 cell may carry a 1552 reading — a correction, not just a closed flag (eye-read needed; RULINGS NEEDED 5) |
| `1552/MP_1552.jpg` | 51,391 B, 410×669 | first page of 1552 Morning Prayer: rubrics and the opening sentences with margin citations | **`editions/1552/daily-office/morning-prayer.md:19`** (`'Psalm ii'`) — the sentence and its margin citation are on the page and legible; the `'Jerem ii'` sentence (line 30) is not on this page |
| `1552/Confirmation_1552.jpg` | 34,713 B, 356×630 | the versicles and the first prayer of 1552 Confirmation | **`editions/1552/occasional-offices/confirmation.md:25`** (`'Lard'`) and **`:36`** (`'let out crye'`) — both versicles are on the page and legible |
| `1549/Confirmation2_1549.jpg` | 36,117 B, 342×576 | 1549 Confirmation: the signing, the rubric before the laying on of hands | **`editions/1549/occasional-offices/confirmation.md:48`** (`'heades'`) — the rubric is on the page and legible |
| `1549/Confirmation1_1549.jpg`, `Communion_Sick1_1549.jpg`, `Communion_Sick2_1549.jpg`, `Communion1_1549.jpg`; `1552/Communion_1552.jpg`; `1559/HC_1559_lg.jpg`, `MP_1559_lg.jpg`; `1549/BCP1559page.jpg` (a 1559 propers page, First Sunday in Advent) | 20–123 kB | checked by eye | no open flag falls on these pages (the 1549 Communion-of-the-Sick rubric with `'us'` is on the page BEFORE `Communion_Sick1`) |
| not viewed: `1549/` Matins1549, Preface1549, LastPage_1549, Communion2/3_1549, Easter1549, Easter1552, BCP1549Contents, Bishops_1550/1552, Ordinal_Preface_1550, Ordinal_title_1550/1634, Baptism.jpg, Unction.jpg, Communion_MS, Marriage_MS, GreatBible_Ephesians; `1552/` Black_Rubric1–3, Title_Page_1552; `1559/` Title_Page_1559 | 6–126 kB | sizes/dates in D1 | none mapped (no open flag in 1549 Matins, Preface, Easter; Black Rubric has no flag) |

**Caveat for every photograph:** 300–600 px wide JPEGs, printing/copy not
stated on the page (the 1549 notes say only "photographs of original pages"),
far below the 4400 px eye-crop rule in COMMON_RULES. Whether they may be used
at all is RULINGS NEEDED 5.

### D2.5 1637 (Scottish)

No 1637 book scan on justus (the index links two archive.org copies, off the
allow-list). Photographs: `Scotland/MP_1637.jpg` (57,462 B, 350×614) shows the
LAST response of the suffrages, the rubric before the Collects and the second
and third collects — the tail end of the **missing-page span** flagged at
`editions/1637/daily-office/morning-prayer.md:130` (Te Deum → the rubric
before the Collects); it does not show the canticles. It does not carry the
`'Ps. 28'` sentence (line 28). `Scotland/Communion{1..6}lg_1637.jpg` (87–100 kB
each) are six pages of the 1637 Communion — candidates for the 1637 HC flag
(`holy-communion.md:176`, the Comfortable Words citations; not viewed).
**The "1637 | Kalendar, both rubrics" gap is a scope gap, not a source gap:**
`Scotland/Kalendar_1637.htm` and `Scotland/Lectionary_1637.htm` serve (HTML,
same class as every other 1637 carrier), and both rubrics are in the cached
`Scotland/front_matter_1637.htm` (#Order_Psalter, #Order of Scripture).

### D2.6 1662 — printed books (R8/R12 reopeners) and apparatus

None of justus's printed-1662 items is a Sealed Book or a 1660s printing, so
**none reopens R8 or R12**: Sturt's engraved book of 1717 (`Sturt/*.pdf`, 11
files, 10.4–18.7 MB each, 400 dpi, Griffiths 1717/2); Baskerville 1762 (only
as Wohlers' re-setting, KEYING); `1662/BCP1775.pdf` 22,087,182 B (1775 Oxford
quarto, PAGE SCAN, "said to be the printing on which the first US BCP was
based" — context for 1789, never evidence under R2); `1662/BCP-Plaintune.pdf`
40,293,453 B (1843); `1662/Statutory.pdf` 51,168,830 B (1901). The 1666 (Field,
Cambridge) and 1669 (HM Printers) printings that `1662/1662.html` lists are on
Google Books / archive.org — off the allow-list.
Two keyed apparatus pages bear on open questions without being witnesses:
`Variations.htm` (Wohlers' table of state-prayer variants) gives the 1662
Royal-Family names as "Queen Catherine, Mary the Queen Mother, James Duke of
York" — an editor's table compiled from Howell, Blunt and the York report,
exactly the kind of apparatus R2 and R8 refuse to fill a blank from;
`1662/deviations.html` (the 1892 York Convocation committee's report on
modern editions vs the Sealed Books) is an independently compiled change log
(R6's "different kind"), useful for the communion-admission-rubric question
and for the Kalendar's placement and lessons.

### D2.7 1929 (Scottish), 1764, 1979, 1945

- **1929:** `Scotland/BCP1929.pdf` 77,609,792 B is the full book ("a printing
  from ~1950", PDF graphics) — it could settle both v1929 flags
  (`holy-communion.md:152` `Acts 20. 85`; `:257` `Elizabeth our Queen`, where a
  c.1950 printing is itself reign-dependent). **`Scotland/Scottish_BCP1929.pdf`
  (3,499,237 B, 39 pp, downloaded) is NOT the book**: it is A. C. Don's short
  illustrated history of the same name. SOURCES.md calls it "the justus
  full-book PDF" (RULINGS NEEDED 4).
- **1764:** only HTML (`Scot1764_Communion.htm`) and a title image
  (`Scotland/Scottish1764.jpg`, 11,817 B); the 3 v1764 flags have no scan.
- **1979:** nothing new — Wohlers' formatted re-setting (KEYING: 30 PDFs, 37 RTF, 35 DOC, 5 zips), the 1993 ASCII e-text (the carrier, 11 files, all cached and
  byte-identical), and `1979Prospectus.pdf` (10.9 MB) on `Standard1979.htm`.
  Church Publishing's file (Wave 19) remains the witness.
- **1945 lectionary (open fork, not wanted now):** present as
  `1928/Lectionary_1945.pdf` (KEYING) and `1928/BCP1945.pdf` 64,922,800 B
  (PAGE SCAN, the 1945 printing).

---

## D3. Queued next steps (HANDOFF §8 form), in priority order

Priority rests on three things, in this order: (a) a page scan of the edition's
OWN text that no previous wave has had (R2 is satisfied only by a source for
that edition itself); (b) the number of open flags and recorded gaps one fetch
can close; (c) cost — already-cached scans and small files first. Sizes are
the HEAD `Content-Length` of 2026-10-16. Every scan below is over the 5 MB
limit and was NOT downloaded; the coordinator decides.

**Q0 (zero-fetch, do first). The two scans already in `scrape-cache/` cover
more open flags than anything new.**
- *What:* `1892Standard/1892standard.pdf` (70,097,195 B, cached 2026-09-11,
  byte-identical to today's HEAD) and `1928/BCP1929.pdf` (42,365,481 B, cached,
  byte-identical).
- *What it settles:* (i) the **1892 Kalendar recorded gap** — confirmed this
  session that the scan carries "A Table of Lessons for <month>" one month a
  page, January at scan p. 12 through December at scan p. 23 (September seen at
  p. 20); the keyed `1892Standard/bcp.pdf` omits the Calendar entirely (its p. 9
  Selections is followed by p. 10 Morning Prayer), so the scan is the only
  structured source. (ii) **up to 42 of v1892's 43 flags** (offices, ordinal,
  Litany, propers; not Psalm 1:3 "water-side", which the scan cannot settle by
  construction). (iii) **22 of v1928's 25 flags** from the original 1928
  printing (the 3 Psalter mediant flags are the queued 1952-facsimile job).
- *Method:* Kalendar — the w20 table pipeline (`w20_grid` deskew + rules,
  `w20_cells` per-rect OCR, `w20_strip`, eye reads at 4400 px) on scan
  pp. 12–23 with the w14/w15 row model (the 1789 cell's shape); flags — the
  w17/w18 render+OCR (`w17_render.py`-style qlmanage renders, `w17_ocrbox`
  crops). 1928 — the w15_src JPEG2000 two-up split.
- *R7:* the 1892 scan is the subscribers' edition (Griffiths 1893/7) of the
  Standard Book — the 1892 standard itself; the 1928 scan is the original
  printing (Wave 15 established that the keyed text follows a later printing).

**Q1. The 1789 book in its own early printings — the first allow-listed page
scans of v1789.**
- *What, in order:* (a) `1789/1795%20folio/services.pdf` 39,140,350 B — Hugh
  Gaine's 1795 "first folio" altar book (Griffiths 1795/11), PDF graphics +
  uncorrected OCR, complete but for the title page; (b)
  `1789/1790/1790folio.pdf` 71,982,918 B — the 1790 partial folio (Griffiths
  1793/12, dated 1790 by a MS note), the only pre-1793-Standard scan; (c)
  `1789/1795%20folio/psalms.pdf` 40,018,577 B, only if the maintainer opens
  the Psalter (RULINGS NEEDED 2). (`readings.pdf` 37,967,621 B: optional, no
  open propers flags.)
- *What it settles:* from (a): the two Proper Psalms leads (Ascension evening
  103 vs 108; Good Friday evening 64 vs 69 — 2 cells), the November Kalendar
  columns (60 blank cells, 1 flag at `editions/1789/tables/calendar.md:331`),
  and the other 27 v1789 flags. From (b): the November lesson columns as
  printed before the 1793 Standard, and 7 of the 27 (MP 1, EP 2, Litany 3,
  HC 1) — the folio has NO Psalter rubric and NO Proper Psalms table (checked
  against its typeset twin, D2.2), so it cannot settle the two leads. From
  (c): a page scan of the 1789 Psalter — the gap R2 left open.
- *Method:* w17/w18 render+OCR (`w17_ocrbox` positions; eye at 4400 px for
  the two psalm numbers — 3/8 and 4/9 are exactly the digits OCR confuses);
  the w20 table pipeline (`w20_grid`, `w20_cells`, `w20_strip`) for the
  November lesson table, with the 1789 calendar cell's row model; the w18
  Psalter pipeline (`w18_psalter.py`, `w18_mediant.py`) for (c).
- *R7 (read first):* `std_eds1.htm` / `std_eds2.htm` (Gibson, *The Standard
  Editions of the American BCP*, on justus, fetched this session) and the 1790
  index. The first Standard (1793) made "a few minor, mostly typographical,
  changes"; Gibson records specific 1790→1793 corrections, among them **the
  29 November second morning lesson** and a Preface clause, and notes the 1793
  Standard followed the 1791 rather than the 1790 printing. So the 1795 folio
  is post-Standard and the 1790 folio is pre-Standard — they can legitimately
  differ in exactly the November cells. Decide which printing v1789
  represents before collating (RULINGS NEEDED 1). The 1790 scan's text layer
  is the OCR Wave 13 rejected; read the IMAGES (`1789/EP_1790Folio.jpg`, a page
  of the same folio, shows clean, legible roman type even at 325 px).
- *Already known from a keying (not evidence, R6):* the typeset re-creation of
  the 1790 first edition prints 64 and 103 too (D2.2), so do not expect the
  scan to "correct" them; it may confirm them.

**Q2. The 1604 text in printings of its own reign and after.**
- *What:* `1559/BCP1623.pdf` 27,779,226 B — a 1623 "Bible version" printing
  (Griffiths 1623/1), James I's reign, PDF graphics + uncorrected OCR; title
  page, "first few leaves" and Psalter missing, "all of the services are
  complete". Then `1559/BCP1634.pdf` 130,490,854 B (1634 Barker, imperfect)
  for what the 1623 copy lacks, and `1559/Psalter1634.pdf` 54,704,435 B.
- *What it settles:* **all 25 v1604 flags**, including the six reign-dependent
  ones (Litany `JAMES`, the sovereign's prayer, Ordinal `James`/`Kings` ×3,
  Communion `JAMES our King`), which only a James-I printing can answer; the
  **1604 propers gap** ("no allow-listed 1604 propers source", so 1604 inherits
  1559 and the initial-verse-number change is unrepresented); the 1604
  Catechism addition; and — if the 1623 copy's missing front leaves spare them,
  else from the 1634 copy — the **1604 Kalendar + both rubrics** gap and the
  **1604 share of the "1549–1604 Proper Lessons" gap** (R15's reopener: a
  1549–1604 scan showing whether the table fits the row model). From
  `Psalter1634.pdf`: the **1604 share of the "1549–1604 Psalter" gap** only.
- *Method:* w17/w18 render+OCR (prose), w20 table pipeline (Kalendar, Proper
  Lessons). The justus typeset `1559/*.pdf` (a keying adjusted to a 1634 copy)
  and `1559/*.htm` (which carries the 1604 apparatus) are the carriers.
- *R7:* a "Bible version" "omits some of the rubrics"; 1623 and 1634 spell as
  their printers did, not as 1604 did; the 1634 copy names King Charles, so
  never take reign-dependent readings from it. Which printing stands for v1604
  is a ruling (below).

**Q3. The Convocation Book — a 1636 printed book with the 1661 revision
written into it.**
- *What:* `1662/Orig_manuscript/convocation.pdf` 30,359,715 B — the 1871
  reprint (Griffiths 1871/1) of the 1870 photographic facsimile of the 1636 BCP
  that Sancroft marked up for Convocation in 1661.
- *What it could settle:* as a 1636 printing of the 1604 text it overlaps Q2
  (Kalendar, rubrics, Proper Lessons, propers); as the document the Annexed
  Book was fair-copied from, it is a second, different-KIND witness for the
  three Wave-20 Kalendar flags (June 11 stop, June 16 stop, July 26 St Anne)
  and for the June page that only Wikimedia's renderer can decode (R14).
- *R7:* two layers on one page (print of 1636, pen of 1661); a reading must
  say which layer it is from. Not a printed-1662 book (does not reopen R8/R12).

**Q4. The 1928 Psalter (already HANDOFF §8 item 3) — confirmed served.**
- `1928Standard/1952std.pdf` 68,953,844 B, Last-Modified 2014-09-22 (the 1952
  facsimile, Griffiths 1952/4, PDF graphics). **Already in `scrape-cache/`**:
  another session fetched it today at 14:24 under its `https://` key
  (`justus.anglican.org_resources_bcp_1928Standard_1952std.pdf.7929510c29ad3b30.pdf`,
  same byte count as today's HEAD) — not fetched by D. Settles the 3 v1928 mediant
  flags; method w18 Psalter pipeline; R7: a reduced 1952 facsimile of the 1928
  Standard Book, not the 1929 original printing (which is also cached and also
  contains the Psalter, at lower resolution).

**Q5. Single-page photographs already on justus (tiny; gated on RULINGS
NEEDED 5).** Five images carry six open flags (D2.4): `1549/Priests_1550.jpg`
101,188 B + `1549/Priests_1552.jpg` 103,455 B → the 1549 and 1552
ordering-priests flags (and possibly a 1549 correction); `1552/MP_1552.jpg`
51,391 B → 1552 MP `'Psalm ii'`; `1552/Confirmation_1552.jpg` 34,713 B → 1552
`'Lard'` and `'let out crye'`; `1549/Confirmation2_1549.jpg` 36,117 B → 1549
`'heades'`. All five are now in `scrape-cache/` (fetched this session). Method:
eye read at native size (no OCR pipeline is worth it at 350–580 px); R7: the
page does not say which printing or copy it is.

**Q6. The 1637 Kalendar and both rubrics — a scope gap with a source.**
`Scotland/Kalendar_1637.htm` and `Scotland/Lectionary_1637.htm` (HTML, sizes
in D1) plus the cached `Scotland/front_matter_1637.htm` (#Order_Psalter,
#Order of Scripture). Same class as every 1637 carrier (a keying); method the
w14 HTML table parser; R7: justus's 1637 notes (two leaves missing from its
copy near the front matter — check whether the Kalendar is affected).

**Not queued (recorded so they are not re-surveyed):** printed 1662 books on
justus are all late (Sturt's engraved 1717, Baskerville 1762 as a re-setting,
a 1775 Oxford quarto, the 1843 Plain-Tune book, the 1901 *Statutory Common
Prayer*) — none is a Sealed Book or a 1662 printing, so none can fill the R8
blanks; the 1666 and 1669 printings justus lists are on Google Books /
archive.org, off the allow-list. No 1549, 1552, 1559 or 1637 book scan exists
on justus (archive.org links only). The 1945 lectionary is present
(`1928/Lectionary_1945.pdf`, `1928/BCP1945.pdf` 64,922,800 B) — an open fork,
not wanted now.

---

## D4. Surprises

1. **The tree that came back is an OLDER snapshot than the one the repo was
   built from.** The newest `Last-Modified` on any `bcp/` index page is
   `Whats_new.htm`, 2024-05-31 (its last entry: "30 May 2024"). The copies of
   the same index pages that earlier waves cached in Aug–Sep 2026 carry
   material the live pages now lack:
   - `1789/BCP_1789.htm` (cached 2026-08-11) linked a **1822 Standard**
     (`1789/1822Standard/index.html`); the live page does not, and that URL now
     answers **404**. Its note "don't appear in a Standard Edition until 1822"
     is gone too.
   - `1928/BCP_1928.htm` (cached 2026-09-11) linked the 1976 "Final official
     printing" and an Internet Archive copy of Chorley; both lines are absent.
   - `1559/BCP_1559.htm` (cached 2026-08-11) had a paragraph of four
     plague/war "supplements" (1563, 1625, 1626, 1640) marked New!; absent now,
     while the live page flags as "new" the 1564–1638 Google Books entries that
     the August copy no longer flagged.
   - `1662/1662.html` (cached 2026-09-02) listed *The English Liturgy*
     (Griffiths 1903/5) and an 1883 *Annotated BCP* as new!; absent now.
   - `1892/BCP_1892.htm` differs in markup only (font tags); `england.htm`,
     `Scotland.htm`, `Scotland/BCP_1637.htm`, `Scotland/Scotland.htm`,
     `1549/BCP_1549.htm`, `1552/BCP_1552.htm`, `1892Standard/index.htm`,
     `1928Standard/Standard.htm` are identical to their cached copies (after
     http→https).
   So the restore after the 2026-09-18 outage / 2026-09-25 403 appears to be
   from a backup of about mid-2024. **The content pages the repo uses are
   unaffected**: all **135** pre-existing cache entries that could be compared
   (content pages, the 11 ASCII e-text files, the cached PDFs) are
   byte-identical to today's `Content-Length`; the only 4 that differ are the
   index pages named above (cache re-encoded
   to the page's charset, line endings preserved), and the three cached scans
   (`1892standard.pdf`, `BCP1929.pdf`, `BCP1936.pdf`) match to the byte. But
   any file justus added between mid-2024 and Aug 2026 may be gone (the 1822
   Standard is one), and a page fetched today could be older than the copy in
   the cache. **Recommendation:** never `--force` re-fetch a cached justus page
   without diffing it against the cache first; record the snapshot date in
   SOURCES' retrieval note.
2. **Scheme.** `http://justus.anglican.org/...` 302s to `https://` for every
   path tried (bcp root, robots.txt); HTTPS now presents a valid certificate.
   Every new cache entry from this survey is keyed by its `https://` URL, so it
   sits beside, not over, the `http://` copies earlier waves cached (the
   scraper's cache key hashes the full URL). Waves that cite `http://` URLs
   will still read their own cached copies.
3. **robots.txt** (Last-Modified 1999-10-16) disallows only `/access_stats`,
   `/status`, `/gwords`, `/stsams/*`, `/308`; nothing under `/resources/bcp/`
   is refused. No 403 anywhere in this survey.
4. **Dead links on live pages (404):** `1789/1822Standard/index.html` (see 1);
   `1892/Visitation_Sick_1789.htm` (the 1892 index's "Communion of the Sick"
   link; the page lives at `1789/Visitation_Sick_1789.htm`);
   `/resources/bcp.htm#1662` (from `Scotland/Scotland.htm`);
   `/1928/Articles.htm` (from the 1871 Standard index; the real page is
   `/resources/bcp/1928/Articles.htm`); `/Italian/index.html` and
   `/Swedish/index.html` (from the 1789 index); a relative
   `bcp/archive.org/details/comy00chur` "1666" link on `1662/1662.html`
   (a mangled archive.org URL); `file:///C|/websites/bcp/Scotland.htm` on
   `1662/Orig_manuscript/index.html`; four more mangled relative links on
   `1662/1662.html` that put Google Books URLs under `bcp/`
   (`bcp/books.google.com/books?id=…` for the 1675, 1706, 1745 and 1799
   printings) — all 404. Ten 404s in all among 670 URLs; none is a file the
   repo uses.
4b. **Redirect off the allow-list (recorded, not followed):** the Project
   Canterbury links on the 1892 and 1662 indexes (`/resources/pc/bcp/`, `magyar.html`,
   `swedish.html`, `tigara.html`) answer **301 → http://anglicanhistory.org/…**.
   The scraper's allow-list refuses that host; the hop was not made. (The
   first of these ended my main HEAD sweep with the scraper's own SystemExit;
   the helper was then changed to record the refusal and continue.)
5. **Moved/renamed/misnamed:** the Sturt engraved book is at `bcp/Sturt/`, not under
   `1662/` (a guess at `1662/Sturt/index.html` 404s; the 1662 index links the
   right path). The 1929 Scottish book is linked under two names:
   `Scotland/Scottish_BCP1929.pdf` (from `Scotland.htm`, the file SOURCES
   cites) and `Scotland/BCP1929.pdf` (from `Scotland/Scotland.htm`).
6. **Things the index describes that are not served as files:** the 1790 first
   edition's table of contents lists the Tables of Lessons, the Calendar and
   the two holy-day tables (items 5–8), but no per-section PDF is linked for
   them (only `front_matter.pdf` for items 1–4, and the single `bcp.pdf`).
   The 1789 index says "HTML only for the Psalter" and still points its Psalter
   link at `1928/Psalms.htm` (as SOURCES records).
7. **Not new, but newly important:** `Scotland/Kalendar_1637.htm` and
   `Scotland/Lectionary_1637.htm` (HTML) were already linked in the August
   cache. The "1637 | Kalendar, both rubrics" gap row reads as a scope choice
   ("the Scottish line is transcribed for the Communion"), and the HTML that
   would close it serves (D1); the two rubrics are in the cached
   `Scotland/front_matter_1637.htm` (#Order_Psalter, #Order of Scripture).
8. **Survey artefacts, not site faults:** five title-image URLs I built from
   cached pages in sub-directories with the wrong base
   (`1662/convocation_title.jpg`, `1662/manuscript_title.jpg`,
   `1789/title_page.jpg`, `1789/title.jpg`, `1789/certificate.jpg`) 404'd and
   are excluded from D1; likewise a guessed `1662/Sturt/index.html`. The real
   images sit under `1662/Orig_manuscript/`, `1789/1790/`, `1789/1845Standard/`.
9. **Another session is fetching justus in parallel:** `1928Standard/Standard.htm`
   (14:23:44) and `1928Standard/1952std.pdf` (14:24) entered the cache today
   before my first request (14:24:38). Two processes each honouring a 1 s
   interval can together exceed one request a second against justus; the
   coordinator may want to serialize justus work.

---

## 3. RULINGS NEEDED (none blocks this survey; each blocks a queued step)

1. **Which printing stands for v1789?** The finds are a 1790 partial folio
   (pre-Standard, only the sections that differ from 1662, plus the Tables of
   Lessons), a 1795 complete folio (after the 1793 Standard's "few minor,
   mostly typographical" changes), and the 1845 Standard (fifth Standard).
   Options: (a) the earliest scan that prints the passage (1790 folio where it
   has it, else 1795) — closest to 1789, mixed printings; (b) the 1795 folio
   throughout — one printing, consistent, post-1793; (c) treat any of them as
   corroboration only and leave v1789 on its composite HTML carrier.
   **Recommend (a)**, with every reading recording its printing, and the 1845
   Standard used only to corroborate. Depends on it: Q1 (Proper Psalms leads,
   November columns, 27 flags).
2. **Does a 1795 scan reopen the 1789 Psalter gap?** R2 says the gap is
   "reopened by nothing short of a source for that edition itself". A 1795
   printing of the 1789 book is such a source, with the R7 caveat above.
   Options: open it (transcribe the 1789 Psalter from `1795 folio/psalms.pdf`,
   ~2,500 verses through the w18 Psalter pipeline, 1662 as alignment reference
   for whitespace only, as Wave 13 did for 1892); keep the gap and use the scan
   only to check the Selections; or wait for a 1790 Psalter scan (none on an
   allow-listed host — the 1790 first edition is on justus only as a typeset
   re-creation, and its Psalter is not among the linked files).
   **Recommend opening it** — it is the first source for the edition itself.
   Depends on it: the largest single recorded gap in the American line.
3. **Which printing stands for v1604?** 1623 (James I, "Bible version",
   omits some rubrics, front leaves and Psalter missing) vs 1634 (Charles I,
   imperfect, complete otherwise, plus a separately scanned Psalter) vs the
   1636 Convocation Book's print layer. Options: (a) 1623 for everything it
   prints, 1634 for what it lacks (Kalendar/rubrics if missing, Psalter),
   reign-dependent readings ONLY from 1623; (b) 1634 throughout except
   reign-dependent readings. **Recommend (a).** Depends on it: Q2 (25 flags,
   the propers gap, the Kalendar/rubrics gap, the 1604 share of two more gaps).
4. **SOURCES.md misnames the 1929 Scottish book** (a correction, but a
   published-prose change, so the coordinator's call): it says "The justus
   full-book PDF (`Scottish_BCP1929.pdf`) is an image/OCR scan and was **not**
   used for text". `Scottish_BCP1929.pdf` (3.3 MB) is, per `Scotland.htm`,
   Alan Campbell Don's short illustrated *history*; the full book is
   `Scotland/BCP1929.pdf` (77,609,792 B), "a printing from ~1950" as PDF
   graphics. Proposed diff to `repo-root/SOURCES.md` (Scottish line table, 1929
   row): replace "The justus full-book PDF (`Scottish_BCP1929.pdf`) is an
   image/OCR scan and was **not** used for text." with "The justus full-book
   PDF (`Scotland/BCP1929.pdf`, PDF graphics of a c.1950 printing) was **not**
   used for text; `Scottish_BCP1929.pdf` is a history of the book, not the
   book." Depends on it: the two v1929 flags (`Acts 20. 85`; `Elizabeth our
   Queen`, where a c.1950 printing is itself reign-dependent — R7).
5. **May justus's single-page photographs serve as witnesses?** Five of them
   carry six open flags (D2.4) and two suggest a correction to a published
   1549 cell. They are page images (a different class from the HTML keying, so
   R6 is satisfied), but 300–600 px wide, of an unstated copy/printing, and
   far below COMMON_RULES' 4400 px eye-crop rule; there is no second
   rendering to agree with (R14 would not count one anyway). Options:
   (a) admit them for WORD-level readings by eye at native size, with the
   printing recorded as "unidentified copy photographed by justus", never for
   pointing or case; (b) admit them only to corroborate, never to change a
   cell; (c) exclude them. **Recommend (a)** for the five named images, each
   reading keyed to its image file and pixel size in evidence; a correction
   (the 1549 "where thou shalt be so appointed" tail) to be shown to the
   maintainer before it is applied. Depends on it: Q5.
6. **Scope: close the 1637 Kalendar + rubrics gap from justus's HTML?** The
   gap row says the 1637 book prints these and that the Scottish line was
   transcribed "for the Communion". `Scotland/Kalendar_1637.htm` (127,429 B)
   and `Scotland/Lectionary_1637.htm` (54,155 B) serve, and the rubrics are in
   the cached front-matter page. Options: transcribe (a keying, same class as
   every 1637 cell; R3 does not apply because nothing is claimed absent);
   leave the gap as a scope choice. **Recommend transcribing**, flagged as
   unverified against a 1637 scan like the rest of v1637. Depends on it: Q6.

---


#### 1549 (57 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1549/Ashwednesday_1549.htm | 200 | text/html | 25.5 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-01 | firste daye of Lent |
| 1549/BCP1549.pdf | 200 | application/pdf | 3.0 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | as a single file |
| 1549/BCP1549Contents.jpg | 200 | image/jpeg | 42.6 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/BCP_1549.htm |
| 1549/BCP1559page.jpg | 200 | image/jpeg | 19.8 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | linked from 1549/Readings_Advent_1549.htm |
| 1549/BCP_1549&52_Intro.htm | 200 | text/html | 28.4 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | Introduction |
| 1549/BCP_1549.htm | 200 | text/html | 19.9 kB | 2021-10-03 | INDEX | index page (walked; GET cached under its https key) | cached 2026-09-02 | 1549 Book of Common Prayer |
| 1549/Baptism_1549.htm | 200 | text/html | 48.5 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Baptisme |
| 1549/Bishops_1549.htm | 200 | text/html | 33.2 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Archebishoppes, Bishoppes |
| 1549/Bishops_1550.jpg | 200 | image/jpeg | 103.5 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Bishops_1549.htm |
| 1549/Bishops_1552.jpg | 200 | image/jpeg | 110.5 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Bishops_1549.htm |
| 1549/Burial_1549.htm | 200 | text/html | 36.1 kB | 2014-06-23 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Buriall |
| 1549/Communion1_1549.jpg | 200 | image/jpeg | 84.8 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | First page of Holy Communion |
| 1549/Communion2_1549.jpg | 200 | image/jpeg | 119.4 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | First page of the prayer of consecration |
| 1549/Communion3_1549.jpg | 200 | image/jpeg | 103.5 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | Second page of the prayer of consecration |
| 1549/Communion_1549.htm | 200 | text/html | 80.8 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | holy Communion |
| 1549/Communion_MS.jpg | 200 | image/jpeg | 6.4 kB | 2004-05-13 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Communion_1549.htm |
| 1549/Communion_Sick1_1549.jpg | 200 | image/jpeg | 30.9 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | linked from 1549/Visitation_Sick_1549.htm |
| 1549/Communion_Sick2_1549.jpg | 200 | image/jpeg | 30.2 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | linked from 1549/Visitation_Sick_1549.htm |
| 1549/Confirmation1_1549.jpg | 200 | image/jpeg | 34.9 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | linked from 1549/Confirmation_1549.htm |
| 1549/Confirmation2_1549.jpg | 200 | image/jpeg | 35.3 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | linked from 1549/Confirmation_1549.htm |
| 1549/Confirmation_1549.htm | 200 | text/html | 24.6 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Confirmacion |
| 1549/Deacons_1549.htm | 200 | text/html | 56.1 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Deacons |
| 1549/Easter1549.jpg | 200 | image/jpeg | 29.3 kB | 1999-03-08 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Reading_EasterWeek_1549.htm |
| 1549/Easter1552.jpg | 200 | image/jpeg | 32.5 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Reading_EasterWeek_1549.htm |
| 1549/Evensong_1549.htm | 200 | text/html | 18.3 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Evensong |
| 1549/GreatBible_Ephesians.jpg | 200 | image/jpeg | 26.2 kB | 1999-03-08 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/collects_epistles_gospels_1549.htm |
| 1549/HC.pdf | 200 | application/pdf | 817.3 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/Kalendar_1549.htm | 200 | text/html | 109.1 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-08-14 | Table and Kalendar |
| 1549/LastPage_1549.jpg | 200 | image/jpeg | 32.7 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Of_Ceremonies_1549.htm |
| 1549/Litany_1549.htm | 200 | text/html | 24.8 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-08-11 | the Litany |
| 1549/MP&EP.pdf | 200 | application/pdf | 514.0 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/Marriage_1549.htm | 200 | text/html | 30.8 kB | 2006-05-08 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Matrimony |
| 1549/Marriage_MS.jpg | 200 | image/jpeg | 11.6 kB | 2004-05-13 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Marriage_1549.htm |
| 1549/Matins1549.jpg | 200 | image/jpeg | 37.1 kB | 1999-03-08 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | First page of Matins |
| 1549/Matins_1549.htm | 200 | text/html | 26.9 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Matins |
| 1549/Of_Ceremonies_1549.htm | 200 | text/html | 16.5 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Of Ceremonies |
| 1549/Ordinal_Preface_1550.jpg | 200 | image/jpeg | 121.4 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Deacons_1549.htm |
| 1549/Ordinal_title_1550.jpg | 200 | image/jpeg | 24.2 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Deacons_1549.htm |
| 1549/Ordinal_title_1634.jpg | 200 | image/jpeg | 24.7 kB | 2001-08-16 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Deacons_1549.htm |
| 1549/PDF_Notes.htm | 200 | text/html | 9.0 kB | 2007-04-11 | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | technical notes |
| 1549/Preface1549.jpg | 200 | image/jpeg | 123.0 kB | 1999-03-08 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | Last page of Preface |
| 1549/Priests_1549.htm | 200 | text/html | 42.8 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Priestes |
| 1549/Priests_1550.jpg | 200 | image/jpeg | 98.8 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | linked from 1549/Priests_1549.htm |
| 1549/Priests_1552.jpg | 200 | image/jpeg | 101.0 kB | 1999-03-20 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) | fetched today (D) | linked from 1549/Priests_1549.htm |
| 1549/Purification_Women_1549.htm | 200 | text/html | 8.3 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | purificacion of women. |
| 1549/Unction.jpg | 200 | image/jpeg | 6.4 kB | 2004-05-13 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/Visitation_Sick_1549.htm |
| 1549/Visitation_Sick_1549.htm | 200 | text/html | 41.7 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | visitacion of the sicke |
| 1549/baptism.pdf | 200 | application/pdf | 494.0 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/bcp_1549.jpg | 200 | image/jpeg | 21.5 kB | 2002-01-17 | PAGE IMAGE | single-page photograph linked from a 1549 page (printing per filename) |  | linked from 1549/BCP_1549.htm |
| 1549/burial.pdf | 200 | application/pdf | 385.0 kB | 2014-06-23 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/collects_epistles_gospels_1549.htm | 200 | text/html | 16.4 kB | 2010-02-08 | HTML | keyed web page (Wohlers) | cached 2026-09-01 | Introites, Collectes, Epistles and Gospelles |
| 1549/confirmation.pdf | 200 | application/pdf | 209.2 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/end_matter.pdf | 200 | application/pdf | 407.4 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/front_matter.pdf | 200 | application/pdf | 935.9 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/front_matter_1549.htm | 200 | text/html | 16.9 kB | 2006-12-17 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | A PREFACE |
| 1549/matrimony.pdf | 200 | application/pdf | 300.2 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |
| 1549/visitation_sick.pdf | 200 | application/pdf | 303.7 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Caslon) from the 1896 facsimile (Griffiths 1896/5) of the first printing, Griffiths 1549/1 — per 1549/PDF_Notes.htm |  | [area] |

#### 1552 (21 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1552/BCP_1552.htm | 200 | text/html | 20.6 kB | 2019-06-06 | INDEX | index page (walked; GET cached under its https key) | cached 2026-08-11 | the 1552 Book |
| 1552/Baptism_1552.htm | 200 | text/html | 38.2 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Baptisme |
| 1552/Black_Rubric1.jpg | 200 | image/jpeg | 109.3 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1552 page |  | linked from 1552/Communion_1552.htm |
| 1552/Black_Rubric2.jpg | 200 | image/jpeg | 90.4 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1552 page |  | linked from 1552/Communion_1552.htm |
| 1552/Black_Rubric3.jpg | 200 | image/jpeg | 101.3 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1552 page |  | linked from 1552/Communion_1552.htm |
| 1552/Burial_1552.htm | 200 | text/html | 16.2 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Burial |
| 1552/Churching_Women_1552.htm | 200 | text/html | 7.9 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | thanksgiving of women after childe-birth |
| 1552/Commination_1552.htm | 200 | text/html | 23.3 kB | 2006-12-18 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Comminacion against sinners |
| 1552/Communion_1552.htm | 200 | text/html | 65.7 kB | 2006-12-18 | HTML | keyed web page (Wohlers) | cached 2026-09-01 | holy Communion |
| 1552/Communion_1552.jpg | 200 | image/jpeg | 40.0 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1552 page | fetched today (D) | linked from 1552/Communion_1552.htm |
| 1552/Confirmation_1552.htm | 200 | text/html | 25.0 kB | 2006-12-18 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Confirmacion |
| 1552/Confirmation_1552.jpg | 200 | image/jpeg | 33.9 kB | 1999-03-21 | PAGE IMAGE | single-page photograph linked from a 1552 page | fetched today (D) | linked from 1552/Confirmation_1552.htm |
| 1552/EP_1552.htm | 200 | text/html | 20.0 kB | 2006-12-18 | HTML | keyed web page (Wohlers) | cached 2026-08-11 | Eveninge Praier |
| 1552/Front_matter_1552.htm | 200 | text/html | 28.6 kB | 2007-08-10 | HTML | keyed web page (Wohlers) | cached 2026-08-14 | A PREFACE |
| 1552/Kalendar_1552.htm | 200 | text/html | 131.6 kB | 2006-12-18 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | howe the Psalter is appointed to be read |
| 1552/Litany_1552.htm | 200 | text/html | 29.0 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | The Letanie |
| 1552/MP_1552.htm | 200 | text/html | 33.9 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Mornyng Prayer |
| 1552/MP_1552.jpg | 200 | image/jpeg | 50.2 kB | 1999-03-21 | PAGE IMAGE | single-page photograph linked from a 1552 page | fetched today (D) | linked from 1552/MP_1552.htm |
| 1552/Marriage_1552.htm | 200 | text/html | 29.4 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Matrimonie |
| 1552/Title_Page_1552.jpg | 200 | image/jpeg | 44.1 kB | 2003-01-21 | PAGE IMAGE | single-page photograph linked from a 1552 page |  | linked from 1552/BCP_1552.htm |
| 1552/Visitation_Sick_1552.htm | 200 | text/html | 28.2 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Visitacion of the sicke |

#### 1559 (and the 1604 text) (36 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1559/BCP1559.pdf | 200 | application/pdf | 9.5 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | as a single file |
| 1559/BCP1623.pdf | 200 | application/pdf | 26.5 MB | 2011-05-13 | PAGE SCAN | "Bible version" printing 1623 (Griffiths 1623/1), PDF graphics + uncorrected OCR text; title page, first few leaves and the Psalter missing; "all of the services are complete" |  | Download or read the 1623 BCP (27MB) |
| 1559/BCP1634.pdf | 200 | application/pdf | 124.4 MB | 2021-10-03 | PAGE SCAN | scan of a 1634 Barker printing of the 1604 text (index: 127MB, "imperfect copy with a few pages torn and a few others missing"); the copy the PDF re-setting follows |  | scanned PDF version |
| 1559/BCP_1559.htm | 200 | text/html | 28.1 kB | 2023-10-31 | INDEX | index page (walked; GET cached under its https key) | cached 2026-08-11 | 1559 Book of Common Prayer |
| 1559/Baptism_1559.htm | 200 | text/html | 42.2 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/Baptism_1559.pdf | 200 | application/pdf | 1.6 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/Burial_1559.htm | 200 | text/html | 18.0 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/Burial_1559.pdf | 200 | application/pdf | 919.9 kB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/Catechism_1604.jpg | 200 | image/jpeg | 33.6 kB | 2003-03-03 | PAGE IMAGE | single-page photograph linked from a 1559 page | fetched today (D) | linked from 1559/Confirmation_1559.htm |
| 1559/Churching_of_Women_1559.htm | 200 | text/html | 28.4 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/Communion_1559.htm | 200 | text/html | 69.7 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/Communion_1559.pdf | 200 | application/pdf | 2.9 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/Confirmation_1559.htm | 200 | text/html | 31.6 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/Confirmation_1559.pdf | 200 | application/pdf | 1.1 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/EP_1559.htm | 200 | text/html | 22.0 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-08-11 | HTML |
| 1559/EP_1559.pdf | 200 | application/pdf | 1.3 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/Godly_Prayers.htm | 200 | text/html | 63.7 kB | 2005-07-27 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" |  | HTML |
| 1559/Godly_prayers.pdf | 200 | application/pdf | 1.8 MB | 2001-10-19 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/Greek1638/index.htm | 200 | text/html | 7.0 kB | 2023-10-28 | INDEX | index page (walked; GET cached under its https key) |  | Greek translation |
| 1559/HC_1559_lg.jpg | 200 | image/jpeg | 96.4 kB | 2001-08-14 | PAGE IMAGE | single-page photograph linked from a 1559 page | fetched today (D) | linked from 1559/Communion_1559.htm |
| 1559/JamesI_Procl_Uniformity.htm | 200 | text/html | 13.4 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" |  | HTML |
| 1559/Kalendar_1559.htm | 200 | text/html | 142.3 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/Litany_1559.htm | 200 | text/html | 44.7 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-01 | HTML |
| 1559/Litany_1559.pdf | 200 | application/pdf | 2.7 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/MP_1559.htm | 200 | text/html | 40.5 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/MP_1559.pdf | 200 | application/pdf | 2.5 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/MP_1559_lg.jpg | 200 | image/jpeg | 77.7 kB | 2001-08-14 | PAGE IMAGE | single-page photograph linked from a 1559 page | fetched today (D) | linked from 1559/MP_1559.htm |
| 1559/Marriage_1559.htm | 200 | text/html | 31.7 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/Marriage_1559.pdf | 200 | application/pdf | 4.2 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/Ordinal_1559.pdf | 200 | application/pdf | 1.4 MB | 2007-03-20 | KEYING | typeset re-setting (JSL Blackletter/Founder's Caslon) of the HTML text "adjusted to agree with" a 1634 Barker copy (Griffiths 1634/1) — i.e. a keying of the 1604 text as printed 1634 |  | PDF |
| 1559/PDF1623.htm | 200 | text/html | 4.8 kB | 2011-05-13 | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | 1623 “Bible version” |
| 1559/Psalter1634.pdf | 200 | application/pdf | 52.2 MB | 2021-10-03 | PAGE SCAN | scan of the Psalter bound with the same 1634 book (index: 53MB) |  | 1634 Psalter |
| 1559/Sternhold&Hopkins1634.pdf | 200 | application/pdf | 74.7 MB | 2021-10-03 | PAGE SCAN | scan of the metrical psalms bound with the 1634 book (index: 76MB) — not BCP text |  | Psalms in Metre |
| 1559/Title_Page_1559.jpg | 200 | image/jpeg | 18.7 kB | 1999-03-28 | PAGE IMAGE | single-page photograph linked from a 1559 page |  | linked from 1559/BCP_1559.htm |
| 1559/Visitation_Sick_1559.htm | 200 | text/html | 30.8 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-09-02 | HTML |
| 1559/front_matter_1559.htm | 200 | text/html | 45.1 kB | 2005-07-12 | HTML | keyed web page; text from the 1890 reprint (Griffiths 1890/7) of Grafton 1559, 1604 changes "from an original edition published in 1634" | cached 2026-08-14 | HTML |

#### 1662 (59 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1662/1775.html | 200 | text/html | 8.6 kB | — | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | The 1662 BCP |
| 1662/1775_title.jpg | 200 | image/jpeg | 29.2 kB | 2021-01-24 | IMAGE | title-page / portrait image |  | linked from 1662/1775.html |
| 1662/Athanasius.pdf | 200 | application/pdf | 78.8 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Creed of St. Athanasius |
| 1662/BCP-Plaintune.pdf | 200 | application/pdf | 38.4 MB | 2024-04-05 | PAGE SCAN (by size) | The BCP with Plain-Tune (1843, Griffiths 1843/26), up to Holy Communion with music |  | The BCP with Plain-Tune |
| 1662/BCP1775.pdf | 200 | application/pdf | 21.1 MB | 2021-01-24 | PAGE SCAN | 1775 Wright & Gill, Oxford, quarto; PDF graphics + uncorrected OCR (long-s) (index: 21.5MB); "said to be the printing on which the first US BCP was based" |  | 1775 Book of Common Prayer |
| 1662/Baskerville.pdf | 200 | application/pdf | 2.2 MB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | as a single PDF file |
| 1662/Baskerville_title.jpg | 200 | image/jpeg | 24.1 kB | 2004-06-20 | IMAGE | title-page / portrait image |  | linked from 1662/baskerville.htm |
| 1662/HC.pdf | 200 | application/pdf | 156.9 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Holy Communion |
| 1662/Orig_manuscript/baptism.htm | 200 | text/html | 53.9 kB | 2012-01-05 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | publick |
| 1662/Orig_manuscript/catechism_conf_marriage.htm | 200 | text/html | 42.0 kB | 2012-01-06 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | The Catechism |
| 1662/Orig_manuscript/collects_epistles_gospels1.htm | 200 | text/html | 171.2 kB | 2012-01-04 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | First Sunday of Advent through the Sunday after Ascension Day |
| 1662/Orig_manuscript/collects_epistles_gospels2.htm | 200 | text/html | 149.5 kB | 2012-01-04 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | Whitsunday through All Saints Day |
| 1662/Orig_manuscript/convocation.pdf | 200 | application/pdf | 29.0 MB | 2022-12-21 | PAGE SCAN | the Convocation Book: a printed 1636 BCP with Sancroft's MS corrections of 1661; 1871 reprint (Griffiths 1871/1) of the 1870 photographic facsimile (index: 30MB) |  | Download or read |
| 1662/Orig_manuscript/ep.htm | 200 | text/html | 28.1 kB | 2012-01-04 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | The Order for Evening Prayer. |
| 1662/Orig_manuscript/front_matter.htm | 200 | text/html | 55.1 kB | 2012-01-04 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | publisher's preface |
| 1662/Orig_manuscript/hc.htm | 200 | text/html | 55.4 kB | 2012-01-07 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | The Order of the Ministration of the holy Communion. |
| 1662/Orig_manuscript/index.html | 200 | text/html | 13.9 kB | — | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | The making of the 1662 BCP |
| 1662/Orig_manuscript/litany_prayers.htm | 200 | text/html | 29.4 kB | 2012-01-04 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | The Litany. |
| 1662/Orig_manuscript/misc_pastoral.htm | 200 | text/html | 63.6 kB | 2012-01-07 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | Visitation of the sick |
| 1662/Orig_manuscript/mp.htm | 200 | text/html | 31.0 kB | 2012-01-04 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | The Order for Morning Prayer. |
| 1662/Orig_manuscript/ordinal.htm | 200 | text/html | 76.3 kB | 2012-01-11 | HTML | keyed transcription of the 1892 Eyre & Spottiswoode printed transcript of the Annexed Book (Griffiths 1892/2) — the SAME text as the repo's Wave-18/20 witness, keyed |  | Bishops |
| 1662/Statutory.pdf | 200 | application/pdf | 48.8 MB | 2013-10-18 | PAGE SCAN | Statutory Common Prayer (1901, ed. J. T. Tomlinson): 1662 text "without unauthorised changes", PDF graphics + uncorrected OCR |  | Download the Statutory Common Prayer |
| 1662/accession.pdf | 200 | application/pdf | 94.2 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Form of Prayer for the 25th day of October |
| 1662/articles.pdf | 200 | application/pdf | 143.6 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Articles of Religion |
| 1662/baptism.pdf | 200 | application/pdf | 158.4 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Publick Baptism of Infants. |
| 1662/baskerville.htm | 200 | text/html | 9.9 kB | 2020-11-12 | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | The 1662 BCP: |
| 1662/burial.pdf | 200 | application/pdf | 97.0 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Burial of the Dead |
| 1662/catechism&conf.pdf | 200 | application/pdf | 102.2 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | A Catechism |
| 1662/churching_women.pdf | 200 | application/pdf | 76.4 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Thanksgiving of Women after Child-bearing |
| 1662/collects.pdf | 200 | application/pdf | 572.2 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Collects, Epistles, and Gospels |
| 1662/commination.pdf | 200 | application/pdf | 90.1 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | A Commination |
| 1662/deviations.html | 200 | text/html | 47.6 kB | — | HTML | keyed web page / description | fetched today (D) | Deviations of Modern [1892] Editions of the 1662 Prayer Book from the Text of the Sealed B |
| 1662/ep.pdf | 200 | application/pdf | 143.6 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Order for Evening Prayer |
| 1662/intro.pdf | 200 | application/pdf | 120.3 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Preface |
| 1662/january30.pdf | 200 | application/pdf | 103.2 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Form of Prayer for the 30th Day of January |
| 1662/litany.pdf | 200 | application/pdf | 106.6 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Litany |
| 1662/marriage.pdf | 200 | application/pdf | 105.2 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Solemnization of Matrimony |
| 1662/may29.pdf | 200 | application/pdf | 95.4 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Form of Prayer for the 29th Day of May |
| 1662/mp.pdf | 200 | application/pdf | 101.6 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Order for Morning Prayer. |
| 1662/nov5.pdf | 200 | application/pdf | 98.9 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Form of Prayer for the 5th Day of November |
| 1662/pray&thanks.pdf | 200 | application/pdf | 112.3 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Prayers and Thanksgivings |
| 1662/prayer_assasination.pdf | 200 | application/pdf | 269.4 kB | 2021-01-24 | PAGE SCAN | loose c.1800 state-service inserts found in the 1775 book |  | Form of Prayer and Thanksgiving |
| 1662/prayer_sea.pdf | 200 | application/pdf | 163.3 kB | 2010-10-13 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Forms of Prayer to be used at Sea |
| 1662/prayer_war.pdf | 200 | application/pdf | 175.5 kB | 2021-01-24 | PAGE SCAN | loose c.1800 state-service inserts found in the 1775 book |  | Prayer to be used ... during the War |
| 1662/psalms.pdf | 200 | application/pdf | 651.2 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | The Psalter |
| 1662/statutory.htm | 200 | text/html | 31.9 kB | 2013-10-18 | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | Statutory Common Prayer |
| 1662/visit_sick.pdf | 200 | application/pdf | 114.9 kB | 2007-03-20 | KEYING | typeset re-setting (Storm "John Baskerville" font) of Baskerville's 1762 Cambridge printing; the repo's documented 1662 cross-check (ligatures drop out of the text layer) |  | Visitation of the Sick |
| Sturt/Part01.pdf | 200 | application/pdf | 9.9 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 1: |
| Sturt/Part02.pdf | 200 | application/pdf | 14.8 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 2: |
| Sturt/Part03.pdf | 200 | application/pdf | 14.7 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 3: |
| Sturt/Part04.pdf | 200 | application/pdf | 16.7 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 4: |
| Sturt/Part05.pdf | 200 | application/pdf | 15.4 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 5: |
| Sturt/Part06.pdf | 200 | application/pdf | 13.3 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 6: |
| Sturt/Part07.pdf | 200 | application/pdf | 12.5 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 7: |
| Sturt/Part08.pdf | 200 | application/pdf | 16.4 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 8: |
| Sturt/Part09.pdf | 200 | application/pdf | 17.8 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 9: |
| Sturt/Part10.pdf | 200 | application/pdf | 16.5 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Part 10: |
| Sturt/front_matter.pdf | 200 | application/pdf | 15.6 MB | 2008-11-21 | PAGE SCAN | John Sturt's engraved BCP of 1717 (Griffiths 1717/2), engraved plates scanned at 400 dpi |  | Front Matter: |
| Sturt/index.html | 200 | text/html | 9.1 kB | — | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | The 1662 BCP |

#### Scotland (1637, 1764, 1929) (58 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| Scotland/BCP1929.pdf | 200 | application/pdf | 74.0 MB | 2016-02-01 | PAGE SCAN | the full 1929 Scottish BCP, "a printing from ~1950" as PDF graphics (Scotland/Scotland.htm: 76MB) |  | 1929 Scottish Book of Common Prayer |
| Scotland/BCP_1637.htm | 200 | text/html | 15.8 kB | 2018-06-19 | INDEX | index page (walked; GET cached under its https key) | cached 2026-08-11 | 1637 Scottish Prayer Book |
| Scotland/Baptism_1637.htm | 200 | text/html | 40.4 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-12 | Baptism, Both Public and Private |
| Scotland/Baptism_Scot.htm | 200 | text/html | 79.0 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Baptism |
| Scotland/Burial_1637.htm | 200 | text/html | 18.9 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-13 | Burial |
| Scotland/Burial_Scot.htm | 200 | text/html | 77.4 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Burial of the Dead |
| Scotland/Churching_of_Women_1637.htm | 200 | text/html | 8.8 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-13 | The Thanksgiving of Women after Child-birth |
| Scotland/Churching_of_Women_Scot.htm | 200 | text/html | 13.6 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | Thanksgiving of Women after Child-birth |
| Scotland/Collects1_1637.htm | 200 | text/html | 66.1 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Advent through Holy Week |
| Scotland/Collects2_1637.htm | 200 | text/html | 80.2 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-31 | Easter through the Sundays after Trinity |
| Scotland/Collects3_1637.htm | 200 | text/html | 39.9 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Saints' Days |
| Scotland/Commination_1637.htm | 200 | text/html | 29.4 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-13 | A Commination against Sinners |
| Scotland/Communion1lg_1637.jpg | 200 | image/jpeg | 90.8 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Communion2lg_1637.jpg | 200 | image/jpeg | 88.2 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Communion3lg_1637.jpg | 200 | image/jpeg | 97.3 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Communion4lg_1637.jpg | 200 | image/jpeg | 95.9 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Communion5lg_1637.jpg | 200 | image/jpeg | 85.0 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Communion6lg_1637.jpg | 200 | image/jpeg | 93.0 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Communion_1637.htm | 200 | text/html | 81.5 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-12 | ministration of the Holy Communion |
| Scotland/Confirmation_1637.htm | 200 | text/html | 30.5 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-12 | Scotch Liturgy of 1637 |
| Scotland/EP_1637.htm | 200 | text/html | 23.2 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-11 | Evening Prayer |
| Scotland/EP_Scot.htm | 200 | text/html | 32.2 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | Evening Prayer |
| Scotland/Gillies1929BCP.pdf | 200 | application/pdf | 8.7 MB | 2016-01-06 | OTHER (commentary) | commentary on the 1929 book (Perry, Gillies), PDF graphics; not BCP text |  | The Scottish Book of Common Prayer - Another Aspect |
| Scotland/Kalendar_1637.htm | 200 | text/html | 124.4 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | Table and Calendar |
| Scotland/Lectionary_1637.htm | 200 | text/html | 52.9 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | Proper Psalms and Lessons at Morning and Evening Prayer, for Sundays and Certain Feasts an |
| Scotland/Litany_1637.htm | 200 | text/html | 38.9 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-11 | The Litany |
| Scotland/MP_1637.htm | 200 | text/html | 40.3 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-10 | Morning Prayer |
| Scotland/MP_1637.jpg | 200 | image/jpeg | 56.1 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page | fetched today (D) | linked from Scotland/ |
| Scotland/MP_Scot.htm | 200 | text/html | 59.9 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Introduction to Morning and Evening Prayer |
| Scotland/Marriage_1637.htm | 200 | text/html | 33.4 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-13 | Matrimony |
| Scotland/Marriage_Scot.htm | 200 | text/html | 47.0 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Matrimony |
| Scotland/Penitential_Scot.htm | 200 | text/html | 17.8 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Penitential Service |
| Scotland/Perry1929.pdf | 200 | application/pdf | 10.9 MB | 2016-01-23 | OTHER (commentary) | commentary on the 1929 book (Perry, Gillies), PDF graphics; not BCP text |  | The Scottish Prayer Book: Its Value & History |
| Scotland/Scot1764_Communion.htm | 200 | text/html | 42.0 kB | 2019-02-13 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | 1764 Communion Office |
| Scotland/Scot_Collects_Epistles_Gospels.htm | 200 | text/html | 20.1 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | The Collects, Epistles, and Gospels |
| Scotland/Scot_Compline.htm | 200 | text/html | 32.2 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | Compline |
| Scotland/Scot_English_Communion.htm | 200 | text/html | 91.4 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | English |
| Scotland/Scot_Front_Matter.htm | 200 | text/html | 28.3 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Title Page, Table of Contents, etc. |
| Scotland/Scot_Litany.htm | 200 | text/html | 37.8 kB | 2009-02-15 | HTML | keyed web page (Wohlers) | cached 2026-08-11 | Litanies |
| Scotland/Scot_Ordinal.htm | 200 | text/html | 93.4 kB | 2009-02-15 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Bishops |
| Scotland/Scot_Scottish_Communion.htm | 200 | text/html | 68.2 kB | 2009-02-15 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Scottish |
| Scotland/Scot_Tables_Rules.htm | 200 | text/html | 20.3 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Tables and Rules |
| Scotland/Scot_prayers&thanks.htm | 200 | text/html | 75.7 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Prayers and Thanksgivings |
| Scotland/Scotland1712_title.jpg | 200 | image/jpeg | 12.3 kB | 2005-03-07 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Scottish1764.jpg | 200 | image/jpeg | 11.5 kB | 2001-07-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Scottish_BCP1929.pdf | 200 | application/pdf | 3.3 MB | 2018-12-03 | OTHER (history) | NOT the prayer book: Alan Campbell Don, *The Scottish Book of Common Prayer 1929*, "a short illustrated general history" (Scotland.htm). SOURCES.md calls this file "the justus full-book PDF" — a misidentification | fetched today (D) | The Scottish Book of Common Prayer 1929 |
| Scotland/Title_Page_1637.jpg | 200 | image/jpeg | 31.0 kB | 1999-08-08 | PAGE IMAGE | page photograph / title image linked from a Scottish page |  | linked from Scotland/ |
| Scotland/Visitation_Sick_1637.htm | 200 | text/html | 29.7 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-08-13 | Visitation of the Sick |
| Scotland/Visitation_Sick_Scot.htm | 200 | text/html | 59.6 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Visitation of the Sick |
| Scotland/catechism&confirmation_Scot.htm | 200 | text/html | 41.3 kB | 2009-02-15 | HTML | keyed web page (Wohlers) |  | Catechism |
| Scotland/front_matter_1637.htm | 200 | text/html | 28.3 kB | 2009-02-20 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | A Proclamation for the authorising of the book of Common Prayer |
| Scotland/james6.html | 200 | text/html | 11.5 kB | — | HTML | keyed web page (Wohlers) |  | Scottish Liturgies of the Reign of James VI |
| Scotland/wee_bookie1724.html | 200 | text/html | 33.5 kB | — | HTML | keyed web page (Wohlers) |  | 1724 |
| Scotland/wee_bookie1743.html | 200 | text/html | 34.5 kB | — | HTML | keyed web page (Wohlers) |  | 1743 |
| Scotland/wee_bookie1755.html | 200 | text/html | 34.4 kB | — | HTML | keyed web page (Wohlers) |  | 1755 |
| Scotland/wee_bookie1796.html | 200 | text/html | 42.0 kB | — | HTML | keyed web page (Wohlers) |  | 1796 |
| Scotland/wee_bookie1800.html | 200 | text/html | 35.2 kB | — | HTML | keyed web page (Wohlers) |  | 1800 |
| Scotland/wee_bookies.html | 200 | text/html | 32.8 kB | — | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | Tabular View of the Variations of Order |

#### 1789 — 1790 first edition and 1790 partial folio (21 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1789/1790/1790folio.pdf | 200 | application/pdf | 68.6 MB | 2020-11-23 | PAGE SCAN | 1790 partial folio (Griffiths 1793/12, dated 1790 by MS note; "unique copy" per Gibson): scanned, uncorrected extractable OCR text; includes the Tables of Lessons and a page of hymns omitted from the typeset file (index: 70MB). Wave 13 recorded its TEXT LAYER as unusable OCR of a long-s original — the page IMAGES were never examined |  | scanned file |
| 1789/1790/baptism.pdf | 200 | application/pdf | 263.2 kB | 2013-01-30 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Public Baptism |
| 1789/1790/bcp.pdf | 200 | application/pdf | 1.3 MB | 2013-02-02 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing | fetched today (D) | as a single file |
| 1789/1790/burial.pdf | 200 | application/pdf | 109.4 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Burial of the Dead |
| 1789/1790/catechism&confirm.pdf | 200 | application/pdf | 114.6 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | A Catechism |
| 1789/1790/churching_women.pdf | 200 | application/pdf | 92.2 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | The Churching of Women |
| 1789/1790/ep&litany.pdf | 200 | application/pdf | 136.1 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | The Order for Daily Evening Prayer |
| 1789/1790/family_prayer.pdf | 200 | application/pdf | 130.9 kB | 2013-01-30 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Prayer to be used in Families |
| 1789/1790/folio_bcp.pdf | 200 | application/pdf | 352.6 kB | 2013-02-02 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 partial folio, same line/page breaks (index: 350kB) | fetched today (D) | typeset file |
| 1789/1790/folio_thanksgiving.pdf | 200 | application/pdf | 92.6 kB | 2005-12-11 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | folio |
| 1789/1790/front_matter.pdf | 200 | application/pdf | 308.1 kB | 2013-01-30 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing | fetched today (D) | Ratification of the Book of Common Prayer |
| 1789/1790/hc.pdf | 200 | application/pdf | 249.3 kB | 2013-01-30 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Holy Communion |
| 1789/1790/marriage.pdf | 200 | application/pdf | 100.5 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Matrimony |
| 1789/1790/mp.pdf | 200 | application/pdf | 126.7 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | The Order for Daily Morning Prayer |
| 1789/1790/pray&thanks.pdf | 200 | application/pdf | 117.9 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Prayers and Thanksgivings upon several Occasions |
| 1789/1790/prayer_at_sea.pdf | 200 | application/pdf | 119.9 kB | 2005-11-22 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Prayer to be used at Sea |
| 1789/1790/propers.pdf | 200 | application/pdf | 1.1 MB | 2018-10-10 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | The Collects Epistles, and Gospels |
| 1789/1790/selections_psalms.pdf | 200 | application/pdf | 161.4 kB | 2005-11-25 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Selections of Psalms, |
| 1789/1790/thanksgiving.pdf | 200 | application/pdf | 98.8 kB | 2005-11-22 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Prayer and Thanksgiving to Almighty God, for the Fruits of the earth |
| 1789/1790/visitation_prisoners.pdf | 200 | application/pdf | 121.9 kB | 2005-11-22 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Visitation of Prisoners |
| 1789/1790/visitation_sick.pdf | 200 | application/pdf | 129.1 kB | 2005-11-19 | KEYING | typeset (InDesign, Caslon Old Face) re-creation of the 1790 FIRST EDITION, Hall & Sellers (Griffiths 1790/13), same dimensions and line/page breaks; 12 damaged pages laid out from an 1800 Hall & Sellers printing |  | Visitation of the Sick |

#### 1789 — 1795 first folio (4 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1789/1795%20folio/index.html | 200 | text/html | 5.2 kB | — | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | 1795 Altar Book |
| 1789/1795%20folio/psalms.pdf | 200 | application/pdf | 38.2 MB | 2013-09-02 | PAGE SCAN | 1795 "first folio" altar book, Hugh Gaine, New York (Griffiths 1795/11); PDF graphics + uncorrected OCR; title page missing, some MP/EP pages damaged and repaired |  | Psalter |
| 1789/1795%20folio/readings.pdf | 200 | application/pdf | 36.2 MB | 2013-09-02 | PAGE SCAN | 1795 "first folio" altar book, Hugh Gaine, New York (Griffiths 1795/11); PDF graphics + uncorrected OCR; title page missing, some MP/EP pages damaged and repaired |  | Collects, Epistles & Gospels |
| 1789/1795%20folio/services.pdf | 200 | application/pdf | 37.3 MB | 2013-09-02 | PAGE SCAN | 1795 "first folio" altar book, Hugh Gaine, New York (Griffiths 1795/11); PDF graphics + uncorrected OCR; title page missing, some MP/EP pages damaged and repaired |  | All Services |

#### 1789 — 1845 Standard (6 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1789/1845Standard/1845std.pdf | 200 | application/pdf | 262.2 MB | 2023-11-12 | PAGE SCAN | 1845 Standard Edition (Griffiths 1845/36); PDF graphics + unproofread OCR ("better PDFs" 11 Nov 2023) |  | The entire book |
| 1789/1845Standard/hymns.pdf | 200 | application/pdf | 37.8 MB | 2023-11-12 | PAGE SCAN | 1845 Standard Edition (Griffiths 1845/36); PDF graphics + unproofread OCR ("better PDFs" 11 Nov 2023) |  | Psalms in Metre & Hymns |
| 1789/1845Standard/index.html | 200 | text/html | 9.9 kB | — | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | 1845 Standard |
| 1789/1845Standard/psalms.pdf | 200 | application/pdf | 60.8 MB | 2023-11-12 | PAGE SCAN | 1845 Standard Edition (Griffiths 1845/36); PDF graphics + unproofread OCR ("better PDFs" 11 Nov 2023) |  | The Psalter & Selections of Psalms |
| 1789/1845Standard/readings.pdf | 200 | application/pdf | 53.0 MB | 2023-11-12 | PAGE SCAN | 1845 Standard Edition (Griffiths 1845/36); PDF graphics + unproofread OCR ("better PDFs" 11 Nov 2023) |  | Collects, Epistles & Gospels |
| 1789/1845Standard/services.pdf | 200 | application/pdf | 72.3 MB | 2023-11-12 | PAGE SCAN | 1845 Standard Edition (Griffiths 1845/36); PDF graphics + unproofread OCR ("better PDFs" 11 Nov 2023) |  | All Services |

#### 1789 — 1871 Standard (25 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1789/1871Standard/1871Std.pdf | 200 | application/pdf | 3.2 MB | 2024-05-31 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | as a single PDF |
| 1789/1871Standard/Baptism.pdf | 200 | application/pdf | 253.4 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | The Ministration of Public Baptism of Infants |
| 1789/1871Standard/Bishops.pdf | 200 | application/pdf | 159.4 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Consecrating a Bishop |
| 1789/1871Standard/Burial.pdf | 200 | application/pdf | 106.5 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | the Burial of the Dead |
| 1789/1871Standard/Catechism&Confirmation.pdf | 200 | application/pdf | 94.4 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | A Catechism |
| 1789/1871Standard/Communion.pdf | 200 | application/pdf | 234.4 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Holy Communion |
| 1789/1871Standard/Consecration.pdf | 200 | application/pdf | 132.7 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Consecration of a Church or Chapel |
| 1789/1871Standard/Deacons.pdf | 200 | application/pdf | 132.4 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Making Deacons |
| 1789/1871Standard/EP.pdf | 200 | application/pdf | 102.0 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | The Order for Daily Evening Prayer |
| 1789/1871Standard/Family_Prayer.pdf | 200 | application/pdf | 90.3 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Forms of Prayer to be used in Families |
| 1789/1871Standard/Front_Matter.pdf | 200 | application/pdf | 197.5 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Ratification of the Book of Common Prayer |
| 1789/1871Standard/Institution.pdf | 200 | application/pdf | 151.8 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Institution of Ministers |
| 1789/1871Standard/Litany.pdf | 200 | application/pdf | 79.9 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | The Litany. |
| 1789/1871Standard/MP.pdf | 200 | application/pdf | 110.7 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | The Order for Daily Morning Prayer. |
| 1789/1871Standard/Marriage.pdf | 200 | application/pdf | 90.4 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Solemnization of Matrimony |
| 1789/1871Standard/Ordinal_Communion.pdf | 200 | application/pdf | 195.1 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Holy Communion |
| 1789/1871Standard/Ordinal_Litany.pdf | 200 | application/pdf | 78.2 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Litany and Suffrages |
| 1789/1871Standard/Pray&Thanks.pdf | 200 | application/pdf | 94.2 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Prayers and Thanksgivings upon several Occasions |
| 1789/1871Standard/Prayer&Thanksgiving.pdf | 200 | application/pdf | 74.6 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | A Form of Prayer and Thanksgiving |
| 1789/1871Standard/Priests.pdf | 200 | application/pdf | 168.2 kB | 2013-01-30 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Ordering Priests |
| 1789/1871Standard/Readings.pdf | 200 | application/pdf | 1.7 MB | 2020-11-01 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | The Collects Epistles, and Gospels |
| 1789/1871Standard/Selection_Psalms.pdf | 200 | application/pdf | 166.6 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Selections of Psalms |
| 1789/1871Standard/Visitation_Prisoners.pdf | 200 | application/pdf | 219.4 kB | 2024-05-31 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | the Visitation of Prisoners |
| 1789/1871Standard/Visitation_Sick.pdf | 200 | application/pdf | 116.5 kB | 2007-03-20 | KEYING | typeset (DeVinne) re-creation of the 1871 Standard (Griffiths 1871/17), same line/page breaks |  | Visitation of the Sick |
| 1789/1871Standard/index.htm | 200 | text/html | 10.6 kB | 2014-03-10 | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | 1871 Standard |

#### 1789 (main directory) (73 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1789/7Trinity_1843.jpg | 200 | image/jpeg | 20.9 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/collects_epistles_gospels_1789_1892.htm |
| 1789/Advent1_1865.jpg | 200 | image/jpeg | 20.9 kB | 1999-05-14 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/collects_epistles_gospels_1789_1892.htm |
| 1789/Ash-Wednesday_1849.jpg | 200 | image/jpeg | 21.7 kB | 1999-05-14 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/collects_epistles_gospels_1789_1892.htm |
| 1789/BCP_1789.htm | 200 | text/html | 30.0 kB | 2023-11-11 | INDEX | index page (walked; GET cached under its https key) | cached 2026-08-11 | 18th c. US BCP's |
| 1789/BCP_1789_wp6.zip | 200 | application/zip | 489.1 kB | 1999-05-23 | OTHER | WordPerfect 6 bundle of the 1789 files |  | All the above files |
| 1789/Baptism_1789.htm | 200 | text/html | 71.8 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-01 | HTML |
| 1789/Baptism_1789.pdf | 200 | application/pdf | 102.2 kB | 2002-08-18 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Baptism_1854.jpg | 200 | image/jpeg | 31.4 kB | 2000-05-02 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Baptism_1789.htm |
| 1789/Bishops_1789.htm | 200 | text/html | 38.6 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Bishops_1789.pdf | 200 | application/pdf | 97.4 kB | 2002-08-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Burial.jpg | 200 | image/jpeg | 10.8 kB | 2003-05-10 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Burial_1789.htm |
| 1789/Burial_1789.htm | 200 | text/html | 29.3 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Burial_1789.pdf | 200 | application/pdf | 63.3 kB | 2002-08-18 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Burial_1843.jpg | 200 | image/jpeg | 20.6 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Burial_1789.htm |
| 1789/Catechism.htm | 200 | text/html | 20.1 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Catechism_1789.pdf | 200 | application/pdf | 59.7 kB | 2002-08-18 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Churching_of_Women_1789.htm | 200 | text/html | 10.8 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Churching_of_Women_1789.pdf | 200 | application/pdf | 49.8 kB | 2002-08-18 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Communion_1789.htm | 200 | text/html | 63.0 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Communion_1789.pdf | 200 | application/pdf | 246.9 kB | 2005-02-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Communion_1810.jpg | 200 | image/jpeg | 27.3 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Communion_1789.htm |
| 1789/Communion_1827.jpg | 200 | image/jpeg | 10.3 kB | 2003-11-23 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Communion_1789.htm |
| 1789/Confirmation_1789.htm | 200 | text/html | 13.5 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Confirmation_1789.pdf | 200 | application/pdf | 50.3 kB | 2002-08-18 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Confirmation_1849.jpg | 200 | image/jpeg | 28.2 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Confirmation_1789.htm |
| 1789/Consecration_1789.htm | 200 | text/html | 28.0 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline |  | HTML |
| 1789/Consecration_1789.pdf | 200 | application/pdf | 81.9 kB | 2002-08-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Deacon_1789.htm | 200 | text/html | 25.4 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Deacon_1789.pdf | 200 | application/pdf | 83.0 kB | 2002-08-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/EP_1789.htm | 200 | text/html | 39.2 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/EP_1789.pdf | 200 | application/pdf | 70.1 kB | 2002-08-08 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/EP_1790Folio.jpg | 200 | image/jpeg | 38.8 kB | 2004-10-18 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page | fetched today (D) | linked from 1789/EP_1789.htm |
| 1789/EP_1810.jpg | 200 | image/jpeg | 34.8 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/EP_1789.htm |
| 1789/Family_Prayer_1789.htm | 200 | text/html | 18.1 kB | 2023-11-18 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-01 | HTML |
| 1789/Family_Prayer_1789.pdf | 200 | application/pdf | 59.6 kB | 2002-08-19 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/FrontMatter_1789.htm | 200 | text/html | 114.0 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-08-14 | HTML |
| 1789/Institution_1789.htm | 200 | text/html | 33.8 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline |  | HTML |
| 1789/Institution_1789.pdf | 200 | application/pdf | 94.2 kB | 2002-08-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Litany_1789.htm | 200 | text/html | 21.9 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Litany_1789.pdf | 200 | application/pdf | 97.3 kB | 2005-02-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Litany_1849.jpg | 200 | image/jpeg | 25.4 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Litany_1789.htm |
| 1789/MP_1789.htm | 200 | text/html | 45.9 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/MP_1789.pdf | 200 | application/pdf | 76.0 kB | 2002-08-08 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 | fetched today (D) | PDF |
| 1789/MP_1821.jpg | 200 | image/jpeg | 32.4 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/MP_1789.htm |
| 1789/Marriage.jpg | 200 | image/jpeg | 9.7 kB | 2003-05-10 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Marriage_1789.htm |
| 1789/Marriage2.jpg | 200 | image/jpeg | 11.0 kB | 2003-11-23 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Marriage_1789.htm |
| 1789/Marriage_1789.htm | 200 | text/html | 18.6 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Marriage_1789.pdf | 200 | application/pdf | 54.3 kB | 2002-08-18 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Marriage_1854.jpg | 200 | image/jpeg | 36.5 kB | 2000-05-02 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Marriage_1789.htm |
| 1789/Ordinal_Communion_1789.htm | 200 | text/html | 58.1 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline |  | HTML |
| 1789/Ordinal_Communion_1789.pdf | 200 | application/pdf | 131.7 kB | 2002-08-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Ordinal_Litany_1789.htm | 200 | text/html | 17.9 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline |  | HTML |
| 1789/Ordinal_Litany_1789.pdf | 200 | application/pdf | 73.6 kB | 2002-08-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Prayer&Thanksgiving_1789.htm | 200 | text/html | 17.6 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-01 | HTML |
| 1789/Prayer&Thanksgiving_1789.pdf | 200 | application/pdf | 54.4 kB | 2002-08-19 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Prayer_at_Sea_1789.htm | 200 | text/html | 36.2 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-01 | HTML |
| 1789/Prayer_at_Sea_1789.pdf | 200 | application/pdf | 68.8 kB | 2002-08-19 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Prayers&Thanks_1789.htm | 200 | text/html | 31.9 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-01 | HTML |
| 1789/Prayers&Thanks_1789.pdf | 200 | application/pdf | 66.3 kB | 2002-08-08 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Prayers_1810.jpg | 200 | image/jpeg | 33.5 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Prayers_Thanks_1789.htm |
| 1789/Priests_1789.htm | 200 | text/html | 40.4 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Priests_1789.pdf | 200 | application/pdf | 104.1 kB | 2002-08-24 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Psalms_1865.jpg | 200 | image/jpeg | 25.1 kB | 2000-08-04 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/Psalter_1789.htm |
| 1789/Psalter_1789.htm | 200 | text/html | 18.2 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-04 | HTML |
| 1789/ReadingsA.pdf | 200 | application/pdf | 258.3 kB | 2003-11-23 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | First Sunday in Advent through Ascension Day |
| 1789/ReadingsB.pdf | 200 | application/pdf | 236.0 kB | 2019-12-31 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | from Sunday after Ascension, including Saints' Days |
| 1789/Tables&Rules_1789.htm | 200 | text/html | 87.2 kB | 2013-01-21 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Title_Page_1821.jpg | 200 | image/jpeg | 12.2 kB | 2000-04-02 | PAGE IMAGE | single-page photograph from a later printing (year in filename) linked from a 1789 page |  | linked from 1789/FrontMatter_1789.htm |
| 1789/Visitation_Prisoners_1789.htm | 200 | text/html | 43.0 kB | 2024-05-30 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline |  | HTML |
| 1789/Visitation_Prisoners_1789.pdf | 200 | application/pdf | 72.6 kB | 2002-08-19 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/Visitation_Sick_1789.htm | 200 | text/html | 42.1 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-09-02 | HTML |
| 1789/Visitation_Sick_1789.pdf | 200 | application/pdf | 76.6 kB | 2002-08-18 | KEYING | typeset PDF "based on" a NY Bible & Common Prayer Book Society 24mo, Griffiths 1865/19 |  | PDF |
| 1789/collects_epistles_gospels_1789&1892.htm | 200 | text/html | 18.0 kB | 2005-07-12 | HTML | keyed web page; composite of eight printings certified 1810–1876, Standard-edition changes noted inline | cached 2026-08-17 | HTML |

#### 1892 Standard Book (24 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1892Standard/1892Standard_title.jpg | 200 | image/jpeg | 7.8 kB | 2005-07-17 | IMAGE |  |  | linked from 1892Standard/index.htm |
| 1892Standard/1892standard.pdf | 200 | application/pdf | 66.8 MB | 2022-12-05 | PAGE SCAN | 1892 Standard Book, subscribers' edition; 596 bitonal page images, no text layer (Wave 17 witness) | cached 2026-09-11 | subscribers' edition |
| 1892Standard/Readings.pdf | 200 | application/pdf | 2.3 MB | 2019-12-31 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Collects, Epistles, and Gospels |
| 1892Standard/articles.pdf | 200 | application/pdf | 171.6 kB | 2005-08-11 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Articles of Religion |
| 1892Standard/at_sea&prisoners.pdf | 200 | application/pdf | 265.7 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Prayer to be used at Sea |
| 1892Standard/baptism.pdf | 200 | application/pdf | 267.0 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Public Baptism of Infants |
| 1892Standard/bcp.pdf | 200 | application/pdf | 2.6 MB | 2013-02-03 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) | cached 2026-09-11 | single PDF file |
| 1892Standard/burial.pdf | 200 | application/pdf | 137.8 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Burial of the Dead |
| 1892Standard/catechism&confirm.pdf | 200 | application/pdf | 96.7 kB | 2005-07-17 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | A Catechism |
| 1892Standard/churching_women.pdf | 200 | application/pdf | 80.9 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Churching of Women |
| 1892Standard/consecration&institution.pdf | 200 | application/pdf | 180.1 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Consecration of a Church |
| 1892Standard/front_matter.pdf | 200 | application/pdf | 222.6 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) | cached 2026-09-11 | Ratification of the Book of Common Prayer |
| 1892Standard/harvest&family.pdf | 200 | application/pdf | 185.7 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Form of Prayer and Thanksgiving |
| 1892Standard/hc.pdf | 200 | application/pdf | 314.3 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Holy Communion |
| 1892Standard/independent_article.htm | 200 | text/html | 28.1 kB | 2024-02-19 | HTML |  |  | Evolution of the Standard Prayer Book of 1892 |
| 1892Standard/index.htm | 200 | text/html | 14.5 kB | 2024-03-23 | INDEX | index page (walked; GET cached under its https key) | cached 2026-09-11 | 1892 Standard Book |
| 1892Standard/litany.pdf | 200 | application/pdf | 104.0 kB | 2005-07-17 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Litany |
| 1892Standard/marriage.pdf | 200 | application/pdf | 71.5 kB | 2005-07-17 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Solemnization of Matrimony |
| 1892Standard/mp&ep.pdf | 200 | application/pdf | 328.3 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Morning Prayer |
| 1892Standard/ordinal.pdf | 200 | application/pdf | 527.8 kB | 2013-01-30 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Making, Ordaining, and Consecrating Bishops, Priests, and Deacons |
| 1892Standard/pray&thanks.pdf | 200 | application/pdf | 140.1 kB | 2005-07-17 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Prayers and Thanksgivings |
| 1892Standard/psalter.pdf | 200 | application/pdf | 826.4 kB | 2005-08-17 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) | cached 2026-09-11 | The Psalter |
| 1892Standard/supplemental_report.pdf | 200 | application/pdf | 2.2 MB | 2024-03-23 | PAGE SCAN? | Supplemental Report on the 1892 Standard Book (added 22 Mar 2024) |  | Supplemental Report |
| 1892Standard/visitation_sick.pdf | 200 | application/pdf | 113.5 kB | 2005-07-17 | KEYING | InDesign typeset (DeVinne) re-creation of the 1892 Standard Book, page for page (Wave 16: one keying with 1892/Psalms.pdf) |  | Visitation of the Sick |

#### 1892 (44 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1892/1889Report_changes.html | 200 | text/html | 66.8 kB | — | HTML | keyed web page (Wohlers) |  | Proposed Alterations & Additions, and Book of Offices |
| 1892/2articles.html | 200 | text/html | 126.7 kB | — | HTML | keyed web page (Wohlers) |  | Two articles from the American Church Review of 1882 |
| 1892/BCP1892.pdf | 200 | application/pdf | 6.7 MB | 2006-12-21 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | as one single file |
| 1892/BCP_1892.htm | 200 | text/html | 28.5 kB | 2023-11-19 | INDEX | index page (walked; GET cached under its https key) | cached 2026-08-11 | 1892 Book of Common Prayer |
| 1892/BCP_1892_wp6.zip | 200 | application/zip | 673.8 kB | 2004-03-23 | OTHER | WordPerfect 6 bundle |  | All the above files |
| 1892/Baptism_1892.htm | 200 | text/html | 66.6 kB | 2013-01-30 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Public Baptism of Infants |
| 1892/Baptism_1892.pdf | 200 | application/pdf | 139.2 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Burial_1892.pdf | 200 | application/pdf | 80.9 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Campaign.htm | 200 | text/html | 9.8 kB | 2014-06-01 | HTML | keyed web page (Wohlers) |  | Campaign Prayer Book |
| 1892/Catechism&Confirm_1892.pdf | 200 | application/pdf | 83.2 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Churching_of_Women_1892.pdf | 200 | application/pdf | 53.0 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Communion_1892.htm | 200 | text/html | 65.5 kB | 2013-01-30 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Holy Communion |
| 1892/Communion_1892.pdf | 200 | application/pdf | 136.9 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Compline_1892.htm | 200 | text/html | 22.8 kB | 2005-07-12 | HTML | keyed web page (Wohlers) |  | Office of Compline |
| 1892/Confirmation_1892.htm | 200 | text/html | 14.2 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Order of Confirmation |
| 1892/Consecration_1892.pdf | 200 | application/pdf | 66.3 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/EP_1892.htm | 200 | text/html | 44.1 kB | 2013-01-30 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Evening Prayer |
| 1892/EP_1892.pdf | 200 | application/pdf | 107.8 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Family_Prayer_1892.pdf | 200 | application/pdf | 75.9 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/French1892.pdf | 200 | application/pdf | 26.3 MB | 2017-03-18 | OTHER (translation) | French translation of the 1892 book (27.6 MB, probably page graphics) — not an English text |  | French |
| 1892/Front_Matter_1892.htm | 200 | text/html | 54.2 kB | 2013-01-30 | HTML | keyed web page (Wohlers) | cached 2026-09-11 | The Ratification |
| 1892/Institution_1892.htm | 200 | text/html | 22.3 kB | 2013-01-30 | HTML | keyed web page (Wohlers) |  | Institution of Ministers |
| 1892/Institution_1892.pdf | 200 | application/pdf | 73.4 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Lectionary_1892.htm | 200 | text/html | 190.3 kB | 2005-07-12 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Tables of Proper Lessons |
| 1892/Litany_1892.pdf | 200 | application/pdf | 77.6 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/MP_1892.htm | 200 | text/html | 46.2 kB | 2014-06-01 | HTML | keyed web page (Wohlers) | cached 2026-09-02 | Morning Prayer |
| 1892/MP_1892.pdf | 200 | application/pdf | 158.1 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) | fetched today (D) | PDF |
| 1892/Marriage_1892.pdf | 200 | application/pdf | 65.8 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Ordinal_Communion_1892.pdf | 200 | application/pdf | 105.1 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Ordinal_Litany_1892.pdf | 200 | application/pdf | 59.9 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Ordinations_1892.pdf | 200 | application/pdf | 139.8 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/PB_Edward7.htm | 200 | text/html | 4.7 kB | 2023-10-31 | HTML | keyed web page (Wohlers) |  | American Appendix to the Prayer Book of Edward VII |
| 1892/Pray&Thanks_1892.htm | 200 | text/html | 44.1 kB | 2013-01-30 | HTML | keyed web page (Wohlers) | cached 2026-09-01 | Prayers and Thanksgivings |
| 1892/Pray&Thanks_1892.pdf | 200 | application/pdf | 97.4 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Prayer&Thanksgiving_1892.pdf | 200 | application/pdf | 61.4 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Prayer_at_Sea_1892.pdf | 200 | application/pdf | 78.0 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Psalms.pdf | 200 | application/pdf | 626.3 kB | 2004-03-23 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) | cached 2026-09-11 | PDF |
| 1892/Readings_1892.pdf | 200 | application/pdf | 673.7 kB | 2006-01-03 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Visitation_Prisoners_1892.pdf | 200 | application/pdf | 80.0 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/Visitation_Sick_1789.htm | 404 | text/html | — | — | HTML | keyed web page (Wohlers) |  | Communion of the Sick |
| 1892/Visitation_Sick_1892.pdf | 200 | application/pdf | 95.7 kB | 2004-03-14 | KEYING | Wohlers text PDF (Corel/WordPerfect-produced, embedded fonts) |  | PDF |
| 1892/alterations_additions1.htm | 200 | text/html | 53.5 kB | 2023-11-19 | HTML | keyed web page (Wohlers) | cached 2026-08-14 | Alterations and Additions |
| 1892/alterations_additions_title.jpg | 200 | image/jpeg | 10.2 kB | 2012-02-27 | IMAGE | illustration / title image |  | linked from 1892/alterations_additions1.htm |
| 1892/cheyenne.html | 200 | text/html | 17.9 kB | — | HTML | keyed web page (Wohlers) |  | Cheyenne |

#### 1928 Standard Book (26 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1928Standard/1952std.pdf | 200 | application/pdf | 65.8 MB | 2014-09-22 | PAGE SCAN | 1952 facsimile of the 1928 Standard Book, page graphics (HANDOFF: ~67MB; the queued 1928 Psalter witness) | cached today by another workstream | the complete 1952 facsimile edition |
| 1928Standard/Standard.htm | 200 | text/html | 12.3 kB | 2018-02-20 | INDEX | index page (walked; GET cached under its https key) | cached 2026-09-11 | another set of PDF files |
| 1928Standard/articles.pdf | 200 | application/pdf | 122.8 kB | 2005-09-08 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | ARTICLES OF RELIGION |
| 1928Standard/baptism.pdf | 200 | application/pdf | 121.3 kB | 2005-08-30 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | HOLY BAPTISM |
| 1928Standard/bcp1928std.pdf | 200 | application/pdf | 1.9 MB | 2005-10-27 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) | cached 2026-09-11 | as a single PDF file |
| 1928Standard/bishops.pdf | 200 | application/pdf | 93.9 kB | 2005-09-06 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | BISHOPS |
| 1928Standard/burial.pdf | 200 | application/pdf | 112.8 kB | 2005-08-31 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | ORDER FOR THE BURIAL OF THE DEAD |
| 1928Standard/catechism.pdf | 200 | application/pdf | 77.4 kB | 2005-09-08 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | A CATECHISM |
| 1928Standard/consecration_church.pdf | 200 | application/pdf | 78.7 kB | 2005-09-06 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | FORM OF CONSECRATION OF A CHURCH OR CHAPEL |
| 1928Standard/deacons.pdf | 200 | application/pdf | 82.7 kB | 2005-09-05 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | DEACONS |
| 1928Standard/ep.pdf | 200 | application/pdf | 112.6 kB | 2011-01-18 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | EVENING PRAYER |
| 1928Standard/family_prayer.pdf | 200 | application/pdf | 137.1 kB | 2007-10-20 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | FORMS OF PRAYER TO BE USED IN FAMILIES |
| 1928Standard/front_matter.pdf | 200 | application/pdf | 92.4 kB | 2005-08-25 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) | cached 2026-09-11 | RATIFICATION OF THE BOOK OF COMMON PRAYER |
| 1928Standard/hc.pdf | 200 | application/pdf | 147.6 kB | 2007-10-20 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | HOLY COMMUNION |
| 1928Standard/institution_ministers.pdf | 200 | application/pdf | 79.5 kB | 2005-09-06 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | OFFICE OF INSTITUTION OF MINISTERS |
| 1928Standard/instruction&confirmation.pdf | 200 | application/pdf | 105.2 kB | 2005-08-30 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | OFFICES OF INSTRUCTION |
| 1928Standard/litany&penitential.pdf | 200 | application/pdf | 83.9 kB | 2005-08-25 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | THE LITANY |
| 1928Standard/marriage.pdf | 200 | application/pdf | 67.8 kB | 2005-08-30 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | SOLEMNIZATION OF MATRIMONY |
| 1928Standard/misc_pastoral.pdf | 200 | application/pdf | 121.2 kB | 2005-08-30 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | THANKSGIVING OF WOMEN AFTER CHILD-BIRTH |
| 1928Standard/mp.pdf | 200 | application/pdf | 134.8 kB | 2011-01-18 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | MORNING PRAYER |
| 1928Standard/ordinal_litany.pdf | 200 | application/pdf | 59.2 kB | 2005-09-06 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | LITANY AND SUFFRAGES FOR ORDINATIONS |
| 1928Standard/pray&thanks.pdf | 200 | application/pdf | 118.4 kB | 2005-08-25 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | PRAYERS AND THANKSGIVINGS |
| 1928Standard/priests.pdf | 200 | application/pdf | 99.6 kB | 2005-09-05 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | PRIESTS |
| 1928Standard/propers.pdf | 200 | application/pdf | 558.2 kB | 2007-10-20 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | THE COLLECTS, EPISTLES, AND GOSPELS |
| 1928Standard/psalms.pdf | 200 | application/pdf | 527.9 kB | 2005-09-04 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | THE PSALTER |
| 1928Standard/std_Ed_Brochure.pdf | 200 | application/pdf | 1.5 MB | 2018-02-20 | KEYING | Wohlers' InDesign re-setting (Kis BT) of the 1928 Standard Book — a keying, NOT a witness (R6) |  | sales brochure |

#### 1928 (51 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1928/5th%20Report.pdf | 200 | application/pdf | 6.0 MB | 2024-03-14 | OTHER (report) | the Fifth Report leading to the 1928 book (added 13 Mar 2024) |  | Fifth Report |
| 1928/Articles.htm | 200 | text/html | 37.5 kB | 2009-06-30 | HTML | keyed web page (Satucket clean HTML) |  | HTML |
| 1928/Articles_Religion.pdf | 200 | application/pdf | 110.0 kB | 2009-06-30 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/BCP.pdb | 200 | application/vnd.palm | 488.7 kB | 2004-09-30 | OTHER | bundle (WordPerfect / ePub / zipped HTML / PalmDB) |  | formatted for PDA's |
| 1928/BCP1928.pdf | 200 | application/pdf | 2.2 MB | 2015-04-09 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | All the above PDF files |
| 1928/BCP1929.pdf | 200 | application/pdf | 40.4 MB | 2015-04-11 | PAGE SCAN | original 1928 printing (JPX two-up spreads + hidden OCR; Wave 15 witness) | cached 2026-09-11 | The original 1928 printing |
| 1928/BCP1936.pdf | 200 | application/pdf | 34.9 MB | 2015-04-15 | PAGE SCAN | 1936 printing (JPX + hidden OCR; Wave 16 witness) | cached 2026-09-11 | 1936 version |
| 1928/BCP1945.pdf | 200 | application/pdf | 61.9 MB | 2015-04-15 | PAGE SCAN | 1945 printing as "PDF graphics (63MB)" per index — carries the 1945 lectionary revision (open fork, not wanted now) |  | 1945 version |
| 1928/BCP_1928.htm | 200 | text/html | 24.9 kB | 2021-04-29 | INDEX | index page (walked; GET cached under its https key) | cached 2026-09-11 | 1928 Book of Common Prayer |
| 1928/BCP_1928_wp6.zip | 200 | application/zip | 789.3 kB | 2007-10-20 | OTHER | bundle (WordPerfect / ePub / zipped HTML / PalmDB) |  | ZIP-compressed file in WordPerfect format |
| 1928/Baptism.htm | 200 | text/html | 35.9 kB | 2019-01-11 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-12 | HTML |
| 1928/Baptism_1928.pdf | 200 | application/pdf | 51.5 kB | 1998-07-14 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/BookOfCommonPrayer1928epub.zip | 200 | application/zip | 650.1 kB | 2011-01-28 | OTHER | bundle (WordPerfect / ePub / zipped HTML / PalmDB) |  | ePub format |
| 1928/Book_of_Common_Prayer_1928.zip | 200 | application/zip | 476.5 kB | 2007-10-20 | OTHER | bundle (WordPerfect / ePub / zipped HTML / PalmDB) |  | zipped (compressed) file |
| 1928/Burial.htm | 200 | text/html | 53.9 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-13 | HTML |
| 1928/Burial_1928.pdf | 200 | application/pdf | 106.8 kB | 2004-09-23 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Calendar&Tables_1928.pdf | 200 | application/pdf | 79.3 kB | 2004-09-23 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) | cached 2026-09-11 | PDF |
| 1928/Catechism.htm | 200 | text/html | 19.0 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) |  | HTML |
| 1928/Confirnation.htm | 200 | text/html | 47.8 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-12 | HTML |
| 1928/Consecration.htm | 200 | text/html | 17.8 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) |  | HTML |
| 1928/Consecration_church_1928.pdf | 200 | application/pdf | 79.6 kB | 2004-09-23 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/EP.htm | 200 | text/html | 46.3 kB | 2018-11-19 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-11 | HTML |
| 1928/EP_1928.pdf | 200 | application/pdf | 73.4 kB | 2011-01-18 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/End_matter_1928.pdf | 200 | application/pdf | 77.8 kB | 2004-04-19 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Family_Prayer.htm | 200 | text/html | 39.4 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-09-01 | HTML |
| 1928/Front_Matter_1928.pdf | 200 | application/pdf | 44.7 kB | 1998-07-07 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/HC.htm | 200 | text/html | 67.7 kB | 2018-11-19 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-12 | HTML |
| 1928/HC_1928.pdf | 200 | application/pdf | 141.5 kB | 2007-05-14 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Institution.htm | 200 | text/html | 20.4 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) |  | HTML |
| 1928/Instruction&Confirmation_1928.pdf | 200 | application/pdf | 58.1 kB | 1998-07-14 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Lectionary_1928.pdf | 200 | application/pdf | 89.7 kB | 2007-10-20 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) | cached 2026-09-11 | PDF |
| 1928/Lectionary_1945.pdf | 200 | application/pdf | 134.9 kB | 2007-11-16 | KEYING | Wohlers keying of the 1945 lectionary revision (open fork, not wanted now) |  | PDF |
| 1928/Litany&Penitential_1928.pdf | 200 | application/pdf | 66.0 kB | 2004-08-07 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Litany.htm | 200 | text/html | 26.1 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-11 | HTML |
| 1928/MP.htm | 200 | text/html | 57.4 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-11 | HTML |
| 1928/MP_1928.pdf | 200 | application/pdf | 82.8 kB | 2011-01-18 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Marriage.htm | 200 | text/html | 24.0 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-13 | HTML |
| 1928/Marriage_1928.pdf | 200 | application/pdf | 33.1 kB | 1998-07-14 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Misc_Pastoral_1928.pdf | 200 | application/pdf | 71.6 kB | 1998-07-14 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Ordinal.htm | 200 | text/html | 86.3 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-13 | HTML |
| 1928/Ordinal_1928.pdf | 200 | application/pdf | 186.4 kB | 2004-09-23 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Pray&Thanks.htm | 200 | text/html | 57.9 kB | 2018-11-19 | HTML | keyed web page (Satucket clean HTML) | cached 2026-09-01 | HTML |
| 1928/Prayers_1928.pdf | 200 | application/pdf | 98.4 kB | 2004-01-06 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Prop_1928.htm | 200 | text/html | 11.3 kB | 2024-03-14 | HTML | keyed web page (Satucket clean HTML) |  | here |
| 1928/Propers.pdf | 200 | application/pdf | 634.9 kB | 2006-08-02 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/Psalms.htm | 200 | text/html | 6.7 kB | 2006-08-02 | HTML | keyed web page (Satucket clean HTML) | cached 2026-09-04 | HTML |
| 1928/Psalms_1865.jpg | 200 | image/jpeg | 20.4 kB | 2005-03-17 | IMAGE | illustration |  | linked from 1928/Psalms.htm |
| 1928/Psalms_1928.pdf | 200 | application/pdf | 568.8 kB | 2004-12-10 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |
| 1928/S&S_index.htm | 200 | text/html | 9.4 kB | 2023-11-19 | HTML | keyed web page (Satucket clean HTML) |  | Soldiers & Sailors Prayer Book |
| 1928/Visitation_Sick.htm | 200 | text/html | 48.2 kB | 2005-07-12 | HTML | keyed web page (Satucket clean HTML) | cached 2026-08-13 | HTML |
| 1928/institution_ministers_1928.pdf | 200 | application/pdf | 63.5 kB | 2004-09-23 | KEYING | Wohlers text PDF (Corel-produced, embedded fonts; keyed from a LATER printing per SOURCES Wave 15) |  | PDF |

#### 1979 (root-level files) (119 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| 1979Prospectus.pdf | 200 | application/pdf | 10.4 MB | 2018-02-20 | OTHER | 1979 Standard Book prospectus |  | the 1979 Prospectus |
| Ash_Wednesday.rtf | 200 | application/rtf | 42.4 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| BCP_1979_MSWord.zip | 200 | application/zip | 692.0 kB | 2022-06-04 | OTHER | bundle (1979 formats / ASCII zip / fonts) |  | MSWord 97/2000/2002 format |
| Bishop.doc | 200 | application/msword | 65.5 kB | 2012-12-13 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Bishop.rtf | 200 | application/rtf | 145.4 kB | 2012-12-13 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Catechism.doc | 200 | application/msword | 92.0 kB | 2005-06-07 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Catechism.rtf | 200 | application/rtf | 142.7 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Compline&DailyDev.pdf | 200 | application/pdf | 199.3 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Consecration.doc | 200 | application/msword | 75.0 kB | 2005-05-23 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Consecration.rtf | 200 | application/rtf | 77.3 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| DailyDev.doc | 200 | application/msword | 69.0 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| DailyDev.rtf | 200 | application/rtf | 46.6 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Deacon.doc | 200 | application/msword | 64.5 kB | 2005-05-23 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Deacon.rtf | 200 | application/rtf | 75.0 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Easter%20Vigil2015.rtf | 200 | application/rtf | 45.8 kB | 2022-06-04 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Garamond.zip | 200 | application/zip | 115.0 kB | 1998-01-17 | OTHER | bundle (1979 formats / ASCII zip / fonts) |  | Download fonts |
| Historical_Docs.doc | 200 | application/msword | 149.5 kB | 2005-06-07 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Historical_Docs.pdf | 200 | application/pdf | 154.9 kB | 2006-05-08 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Historical_Docs.rtf | 200 | application/rtf | 139.6 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Holy%20Week2015.rtf | 200 | application/rtf | 53.9 kB | 2022-06-04 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Institution&Consecration.pdf | 200 | application/pdf | 144.3 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Institution.doc | 200 | application/msword | 57.5 kB | 2005-05-23 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Institution.rtf | 200 | application/rtf | 56.1 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Min_at_Death.rtf | 200 | application/rtf | 28.0 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Misc_Pastoral.pdf | 200 | application/pdf | 149.3 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Noonday&Evening.pdf | 200 | application/pdf | 134.5 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Ordination_Litany.doc | 200 | application/msword | 51.5 kB | 2005-05-23 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Ordination_Litany.rtf | 200 | application/rtf | 47.2 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Ordinations.pdf | 200 | application/pdf | 319.9 kB | 2012-12-13 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Pray&tnx.doc | 200 | application/msword | 146.5 kB | 2005-06-07 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Pray&tnx.rtf | 200 | application/rtf | 59.0 kB | 2006-07-25 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Preface&Calendar.pdf | 200 | application/pdf | 177.7 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Priest.doc | 200 | application/msword | 68.0 kB | 2005-05-23 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| Priest.rtf | 200 | application/rtf | 53.7 kB | 2006-07-25 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| Psalms.pdf | 200 | application/pdf | 585.0 kB | 2005-05-30 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| RCL_Sunday.pdf | 200 | application/pdf | 405.7 kB | 2007-10-06 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | replacement BCP pages |
| SpecialDays.pdf | 200 | application/pdf | 243.7 kB | 2022-06-04 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| Special_Days.doc | 200 | application/msword | 150.5 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| baptism.doc | 200 | application/msword | 89.0 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| baptism.pdf | 200 | application/pdf | 154.4 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| baptism.rtf | 200 | application/rtf | 101.2 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| bcp.zip | 200 | application/zip | 307.1 kB | 1997-12-02 | OTHER | bundle (1979 formats / ASCII zip / fonts) |  | here |
| bcp79.pdf | 200 | application/pdf | 4.7 MB | 2008-05-16 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | as a single PDF file |
| bcp_1979_rtf.zip | 200 | application/zip | 568.3 kB | 2022-06-04 | OTHER | bundle (1979 formats / ASCII zip / fonts) |  | RTF format |
| bcpastrl.txt | 200 | text/plain | 110.5 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-12 | BCPASTRL.TXT |
| bcpcolct.txt | 200 | text/plain | 136.0 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-14 | BCPCOLCT.TXT |
| bcpepscl.txt | 200 | text/plain | 83.4 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-12 | BCPEPSCL.TXT |
| bcpeuchr.txt | 200 | text/plain | 109.4 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-12 | BCPEUCHR.TXT |
| bcpinfo.txt | 200 | text/plain | 7.1 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-14 | BCPINFO.TXT |
| bcplectn.txt | 200 | text/plain | 113.1 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-09-02 | BCPLECTN.TXT |
| bcpoffce.txt | 200 | text/plain | 178.0 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-11 | BCPOFFCE.TXT |
| bcpprayr.txt | 200 | text/plain | 123.0 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-11 | BCPPRAYR.TXT |
| bcpsalt1.txt | 200 | text/plain | 120.7 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-09-04 | BCPSALT1.TXT |
| bcpsalt2.txt | 200 | text/plain | 128.3 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-09-04 | BCPSALT2.TXT |
| bcpspecl.txt | 200 | text/plain | 57.1 kB | 2002-01-20 | TEXT | 1993 ASCII e-text of the 1979 book (the repo's 1979 carrier) | cached 2026-08-12 | BCPSPECL.TXT |
| bcpwp6.zip | 200 | application/zip | 776.7 kB | 2022-06-04 | OTHER | bundle (1979 formats / ASCII zip / fonts) |  | WordPerfect format |
| burial1.doc | 200 | application/msword | 106.5 kB | 2005-05-21 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| burial1.pdf | 200 | application/pdf | 159.9 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| burial1.rtf | 200 | application/rtf | 120.5 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| burial2.doc | 200 | application/msword | 88.5 kB | 2007-03-31 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| burial2.pdf | 200 | application/pdf | 131.6 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| burial2.rtf | 200 | application/rtf | 41.8 kB | 2007-03-31 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| catechism.pdf | 200 | application/pdf | 146.1 kB | 2005-05-31 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| colctrad.doc | 200 | application/msword | 233.0 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| colctrad.pdf | 200 | application/pdf | 225.3 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| colctrad.rtf | 200 | application/rtf | 101.7 kB | 2006-07-25 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| collect_contemp.doc | 200 | application/msword | 219.0 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| collect_contemp.pdf | 200 | application/pdf | 269.7 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| collect_contemp.rtf | 200 | application/rtf | 91.7 kB | 2006-07-25 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| compline.doc | 200 | application/msword | 60.0 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| compline.rtf | 200 | application/rtf | 63.7 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| confirm.doc | 200 | application/msword | 56.0 kB | 2005-05-21 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| confirm.pdf | 200 | application/pdf | 125.8 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| confirm.rtf | 200 | application/rtf | 45.5 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| ep1.doc | 200 | application/msword | 58.5 kB | 2014-12-18 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| ep1.pdf | 200 | application/pdf | 119.3 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| ep1.rtf | 200 | application/rtf | 37.3 kB | 2014-12-18 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| ep2.doc | 200 | application/msword | 69.0 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| ep2.pdf | 200 | application/pdf | 117.6 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| ep2.rtf | 200 | application/rtf | 65.8 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| euchr1.doc | 200 | application/msword | 158.5 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| euchr1.pdf | 200 | application/pdf | 156.7 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| euchr1.rtf | 200 | application/rtf | 153.9 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| euchr2.doc | 200 | application/msword | 216.0 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| euchr2.pdf | 200 | application/pdf | 208.6 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| euchr2.rtf | 200 | application/rtf | 342.4 kB | 2005-05-05 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| euchr3.doc | 200 | application/msword | 59.5 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| euchr3.pdf | 200 | application/pdf | 110.0 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| euchr3.rtf | 200 | application/rtf | 33.1 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| evening.doc | 200 | application/msword | 49.5 kB | 2005-06-08 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| evening.rtf | 200 | application/rtf | 30.6 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| formatted_1979.htm | 200 | text/html | 28.9 kB | 2022-06-04 | INDEX | index page (walked; GET cached under its https key) | fetched today (D) | Fonts |
| front_matter.doc | 200 | application/msword | 133.0 kB | 2005-04-09 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| lectionary.pdf | 200 | application/pdf | 426.5 kB | 2019-12-31 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| litany.doc | 200 | application/msword | 51.5 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| litany.pdf | 200 | application/pdf | 96.3 kB | 2005-05-16 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| litany.rtf | 200 | application/rtf | 34.9 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| marriage.doc | 200 | application/msword | 81.5 kB | 2005-05-21 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| marriage.pdf | 200 | application/pdf | 125.4 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| marriage.rtf | 200 | application/rtf | 79.3 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| min_sick.doc | 200 | application/msword | 76.5 kB | 2005-05-21 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| min_sick.rtf | 200 | application/rtf | 17.1 kB | 2006-07-25 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| mp1.doc | 200 | application/msword | 111.5 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| mp1.pdf | 200 | application/pdf | 202.4 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| mp1.rtf | 200 | application/rtf | 113.5 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| mp2.doc | 200 | application/msword | 134.5 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| mp2.pdf | 200 | application/pdf | 174.1 kB | 2005-05-23 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| mp2.rtf | 200 | application/rtf | 126.1 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| noonday.doc | 200 | application/msword | 46.5 kB | 2005-05-16 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| noonday.rtf | 200 | application/rtf | 45.0 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| pray&tnx.pdf | 200 | application/pdf | 156.5 kB | 2005-05-31 | KEYING | Wohlers' formatted re-setting of the 1979 book (Garamond) |  | PDF |
| psalms1.doc | 200 | application/msword | 427.0 kB | 2005-05-30 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| psalms1.rtf | 200 | application/rtf | 972.2 kB | 2014-12-27 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| psalms2.doc | 200 | application/msword | 448.0 kB | 2005-05-30 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| psalms2.rtf | 200 | application/rtf | 1.3 MB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| reconcil.doc | 200 | application/msword | 45.5 kB | 2005-05-21 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| reconcil.rtf | 200 | application/rtf | 30.9 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |
| tnxchild.doc | 200 | application/msword | 48.5 kB | 2005-05-21 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | MSWord |
| tnxchild.rtf | 200 | application/rtf | 33.3 kB | 2005-04-10 | KEYING | Wohlers' formatted 1979 text, word-processor file |  | RTF |

#### Other pages linked from the edition indexes (46 files)

| Path (under /resources/bcp/) | HTTP | Type | Size | Last-Modified | CLASS | Printing / note | Cache | Index link text |
|---|---|---|---|---|---|---|---|---|
| (site)/1928/Articles.htm | 404 | text/html | — | — | HTML |  |  |  |
| (site)/Italian/index.html | 404 | text/html | — | — | INDEX | index page (walked; GET cached under its https key) |  | Italian |
| (site)/Swedish/index.html | 404 | text/html | — | — | INDEX | index page (walked; GET cached under its https key) |  | Swedish |
| (site)/resources/bcp.htm | 404 | text/html | — | — | HTML |  |  | 1662 |
| (site)/resources/pc/bcp/ | REFUSED-HOST via 301 |  | — | — | OTHER |  |  | Project Canterbury |
| (site)/resources/pc/bcp/magyar.html | REFUSED-HOST via 301 |  | — | — | HTML |  |  | Hungarian |
| (site)/resources/pc/bcp/swedish.html | REFUSED-HOST via 301 |  | — | — | HTML |  |  | Swedish |
| (site)/resources/pc/bcp/tigara.html | REFUSED-HOST via 301 |  | — | — | HTML |  |  | Tigara |
| 1786/BCP_1786.htm | 200 | text/html | 17.1 kB | 2024-03-20 | INDEX | index page (walked; GET cached under its https key) |  | 1786 Proposed US BCP. |
| British_Museum_Exhibition.pdf | 200 | application/pdf | 6.1 MB | 2024-05-30 | PDF? |  |  | Catalogue of an Exhibition Commemorating the 400th Anniversay of the BCP |
| China/Chinese1983.html | 200 | text/html | 12.0 kB | — | HTML |  |  | 1983 East Asia BCP in Chinese |
| CofE1928/CofE1928_Litany&Prayers.htm | 200 | text/html | 111.8 kB | 2024-05-30 | HTML |  |  | 1928 C of E Quincunque Vult |
| Communion_Nonjurors.htm | 200 | text/html | 86.6 kB | 2014-01-24 | HTML |  |  | New Communion-Office |
| Dakota1789/index.html | 200 | text/html | 9.5 kB | — | INDEX | index page (walked; GET cached under its https key) |  | Dakota |
| Esperanto/index.htm | 200 | text/html | 7.0 kB | 2023-11-10 | INDEX | index page (walked; GET cached under its https key) |  | portions of the BCP in Esperanto |
| French1662/Jersey/index.html | 200 | text/html | 5.8 kB | — | INDEX | index page (walked; GET cached under its https key) |  | French 1662 BCP |
| French1789/French_1789.htm | 200 | text/html | 22.5 kB | 2014-02-27 | HTML |  |  | French |
| German1892/German_1892.htm | 200 | text/html | 11.2 kB | 2014-08-27 | HTML |  |  | German |
| India/SIndia_euchr_intro.htm | 200 | text/html | 21.4 kB | 2024-03-22 | HTML |  |  | 1950 Eucharist |
| Ireland/amendments1861.html | 200 | text/html | 57.5 kB | — | HTML |  |  | Amendments to the Book of Common Prayer |
| Italian1892/Italian1892.htm | 200 | text/html | 14.9 kB | 2014-07-26 | HTML |  |  | Italian |
| Latin1560/BCP_Latin1560.htm | 200 | text/html | 17.7 kB | 2023-11-17 | HTML |  |  | a Latin translation |
| Latin1560/Collects_epistles_gospels_Latin.htm | 200 | text/html | 200.1 kB | 2023-11-17 | HTML |  |  | 1560 Latin translation |
| Liturgiae_Americanae.htm | 200 | text/html | 6.0 kB | 2007-02-23 | HTML |  |  | a much more detailed history |
| Mohawk/index.htm | 200 | text/html | 9.1 kB | 2008-07-15 | INDEX | index page (walked; GET cached under its https key) |  | Mohawk |
| Nonjurors.htm | 200 | text/html | 9.6 kB | 2014-01-24 | HTML |  |  | Nonjuring |
| Offices1914/Offices_1914.htm | 200 | text/html | 16.3 kB | 2014-09-08 | HTML |  |  | A Book of Offices |
| Ojibwe/index.html | 200 | text/html | 9.0 kB | — | INDEX | index page (walked; GET cached under its https key) |  | Ojibwe |
| Ottawa/index.html | 200 | text/html | 8.2 kB | — | INDEX | index page (walked; GET cached under its https key) |  | Ottawa |
| Sarum/index.htm | 200 | text/html | 8.2 kB | 2024-02-19 | INDEX | index page (walked; GET cached under its https key) |  | Sarum Rite |
| Seabury.htm | 200 | text/html | 44.7 kB | 2007-02-23 | HTML |  |  | Communion Service |
| Spain/index.htm | 200 | text/html | 18.4 kB | 2024-03-20 | INDEX | index page (walked; GET cached under its https key) |  | 1954 BCP of the Spanish Reformed Episcopal Church |
| Story_of_the_Prayer_Book.pdf | 200 | application/pdf | 10.5 MB | 2023-11-22 | PDF? |  |  | The Story of the Prayer Book |
| Taylor_Communion.htm | 200 | text/html | 49.1 kB | 2010-02-07 | HTML |  |  | Jeremy Taylor's Communion Office |
| Variations.htm | 200 | text/html | 28.0 kB | 2024-02-19 | HTML |  | fetched today (D) | Variations in the 1662 Book |
| Wales/Churchpeoples/index.html | 200 | text/html | 11.9 kB | — | INDEX | index page (walked; GET cached under its https key) |  | Churchpeople's Prayer Book |
| Wales/welsh1567.htm | 200 | text/html | 5.6 kB | 2016-10-07 | HTML |  |  | Welsh translation |
| archive.org/details/comy00chur | 404 | text/html | — | — | OTHER |  |  | 1666 |
| books.google.com/books?id=NpBFAAAAcAAJ | 404 | text/html | — | — | OTHER |  |  | 1675 |
| books.google.com/books?id=aNgUAAAAQAAJ | 404 | text/html | — | — | OTHER |  |  | 1745 |
| books.google.com/books?id=gLdFAAAAcAAJ | 404 | text/html | — | — | OTHER |  |  | 1706 |
| books.google.com/books?id=z1JVAAAAcAAJ | 404 | text/html | — | — | OTHER |  |  | 1799 |
| index.html | 200 | text/html | 7.3 kB | — | INDEX | index page (walked; GET cached under its https key) |  | Book of Common Prayer Home |
| languages.html | 200 | text/html | 96.3 kB | — | HTML |  |  | Other Languages page |
| std_eds1.htm | 200 | text/html | 57.0 kB | 2023-11-11 | HTML |  | fetched today (D) | mentioned by Gibson |
| std_eds2.htm | 200 | text/html | 52.7 kB | 2023-11-11 | HTML |  | fetched today (D) | The Standard Editions of the American Book of Common Prayer |

<!-- totals: {'1549': 57, '1552': 21, '1559 (and the 1604 text)': 36, '1662': 59, 'Scotland (1637, 1764, 1929)': 58, '1789 — 1790 first edition and 1790 partial folio': 21, '1789 — 1795 first folio': 4, '1789 — 1845 Standard': 6, '1789 — 1871 Standard': 25, '1789 (main directory)': 73, '1892 Standard Book': 24, '1892': 44, '1928 Standard Book': 26, '1928': 51, '1979 (root-level files)': 119, 'Other pages linked from the edition indexes': 46} all 670 -->
