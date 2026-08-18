# Wave 10 — source map

Authoring-only. Every URL below was fetched and confirmed on **2026-08-17**.
justus is reachable over **plain HTTP only** (its HTTPS vhost 404s every path).

## Index pages (occasion → page/anchor)

| line | index |
|---|---|
| English 1549/1552/1559 | `http://justus.anglican.org/resources/bcp/1549/collects_epistles_gospels_1549.htm` |
| American 1786/1789/1892/1928 | `http://justus.anglican.org/resources/bcp/1789/collects_epistles_gospels_1789&1892.htm` |
| English 1662 | `https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer` |
| Scottish 1637 | `http://justus.anglican.org/resources/bcp/Scotland/Collects{1,2,3}_1637.htm` |
| American 1979 | `http://justus.anglican.org/resources/bcp/ASCII_1979.htm` → `bcpcolct.txt` |

## Per-edition content pages

### 1549 / 1552 / 1559 — one synoptic set, annotated
`http://justus.anglican.org/resources/bcp/1549/Readings_Advent_1549.htm`
`…/Readings_Xmas_1549.htm` · `…/Readings_Epiphany_1549.htm` (10a)
`…/Readings_Lent_1549.htm` · `…/Readings_HolyWeek_1549.htm` (10b)
`…/Reading_EasterWeek_1549.htm` · `…/Readings_EasterSeason_1549.htm` ·
`…/Readings_Ascension&Whitsuntide_1549.htm` · `…/Readings_Trinity{A,B,C}_1549.htm` (10c)
Saints' days pages (10d) are linked from the same index.

The page states the three books' propers are "with some small exceptions, all
identical", and carries the exceptions as apparatus:

- **Layout:** a two-column table. The **left** cell (`width=450`, Georgia) is the
  liturgical text; the **right** cell (`width=150`, Arial, `#999999`) is Wohlers'
  editorial note. `ingest/w10_spine.py` keeps them apart, so no editorial prose can
  leak into a transcription.
- **Grey brackets** `[…]*` inside the text mark material found only in some books,
  explained by the footnote directly beneath (`* Found only in the 1549 book.`,
  `* added 1552.`, `* added in late 1500's`).
- Known deltas already read off the apparatus: 1552 **drops the Introits** (and
  drops "INTROITES," from the section title); `"Amen"` is added at the end of each
  collect **in 1559 only**; several occasion titles gain "in Advent"/"after the
  Epiphany" "in the late 1500's"; **initial verse numbers were added in 1604**.
- The modern verse ranges printed in square brackets (`[Romans 13:8-14]`) are
  Wohlers' identification, **not** Prayer-Book text — recorded in provenance, kept
  out of the files (see `WAVE10_GUIDE.md` §3).

### 1604
No allow-listed source prints the 1604 propers. 1604 **inherits 1559**; the
apparatus's "initial verse numbers added in 1604" is recorded as an explicit gap
in `SOURCES.md`/`NOTICE.md` rather than reconstructed.

### 1662 — Church of England
89 per-occasion pages under
`…/book-common-prayer/collects-epistles-and-gospels` (`-0` … `-87`, plus `/all`
= All Saints and `/ash` = Ash Wednesday). The bare slug is *The Innocents' Day*.
The full slug → occasion map is `ingest/spines-w10/coe_slug_map.tsv`, built by
`ingest/w10_coe_index.py` (the site times out intermittently; the script retries
and the scrape cache makes re-runs free).
Page shape: `### The Collect` / `### The Epistle` / `### The Gospel`, each reading
headed by a modernized citation (`Romans 13.8-14`). Every 1662 file keeps the
`BCP 1662` Crown-copyright acknowledgment (spec §8).
10a slugs: `-1`…`-4` Advent 1–4 · `-6` Christmas Day · `-7` Sunday after Christmas
· `-8` Circumcision · `-9` Epiphany · `-10`…`-15` Epiphany 1–6.

### 1637 Scottish
`http://justus.anglican.org/resources/bcp/Scotland/Collects1_1637.htm` (Advent →
Holy Week; 10a + 10b), `Collects2_1637.htm` (Easter → Trinity; 10c),
`Collects3_1637.htm` (Saints' days; 10d).
The page prints the **collects in full and the readings as citations only**
(`Rom. 13.8. [-14]`) — Wohlers notes the original prints them at length from the
King James translation. That is exactly Decision B's depth. The 1637 also prints
its own Gospel rubrics (the Presbyter's announcement, "Thanks be to thee, O Lord")
which belong under `## The Gospel`.

### 1764 / 1929 Scottish
**Absent** — the Communion-only line, as with MP/EP/Litany/the offices.

### 1789 / 1892 / 1928 American
`http://justus.anglican.org/resources/bcp/1789/Readings1789&1892A.htm` (Advent →
Lent 5; 10a + part of 10b), `…B.htm` (Palm Sunday → Easter 5),
`…C.htm` (Ascension → Trinity 25), `…D.htm` (Saints' days).
This is a **four-edition synoptic**: "as found in the 1786 Proposed, 1789, 1892,
and 1928 U. S. Books of Common Prayer", with the same two-column apparatus marking
which edition each variant belongs to (`Heading, ADVENT SEASON. added in 1928`,
`* "the" added in 1892`, `Prop. (1786) Book only`). The 1786 Proposed Book is
**out of scope** — its variants are ignored, not transcribed.
American-line features visible already: a **Second Sunday after Christmas Day**
(no English counterpart), a **Sixth Sunday after the Epiphany**, "The Presentation
of Christ in the Temple" for the Purification, and a **Transfiguration**.

### 1928 cross-check
`http://justus.anglican.org/resources/bcp/1928/Propers.pdf` — 91 pages.
**Its text layer is clean** (unlike the Wave-9 `Front_Matter_1928.pdf`, whose font
layer was glyph-garbled): `pdf_spine.py` extracts it readably. It is
two-column landscape, so `ingest/w10_1928_spine.py` splits at the column gutter
and re-joins the drop-cap letters the layout strands at the start of the next
line. Used to confirm the synoptic's 1928 readings.

### 1979 American
`http://justus.anglican.org/resources/bcp/bcpcolct.txt` — the public-domain 1993
ASCII e-text, file 3 of 11. Structure: `<Collects:  Traditional>` … then
`<Collects:  Contemporary>`, each with `<Occasion>` headings, the collect body,
and a `*Preface of …*` line. `=Amen.=` is the e-text's emphasis marking.
**Known e-text defects** (dropouts from the 1993 keying, not Prayer-Book facts):
Traditional is missing *Fourth Sunday of Advent*, *Eighth Sunday after the
Epiphany*, and Propers 4/14/25; Contemporary is missing *Sixth Sunday after the
Epiphany* and has a corrupted *Fourth Sunday in Lent* heading. Affected cells get
a `<!-- VERIFY -->`; nothing is reconstructed. `bcp10.txt` (the single-file
assembly named in the header) is **404 on justus** — the per-part files are the
only copy.

## Spines produced so far

    ingest/spines-w10/1549_advent.md      1549/1552/1559 Advent
    ingest/spines-w10/1549_Xmas.md        1549/1552/1559 Christmas
    ingest/spines-w10/1549_Epiphany.md    1549/1552/1559 Epiphany (+ pre-Lent)
    ingest/spines-w10/1789_A.md           1786/1789/1892/1928 Advent → Lent 5
    ingest/spines-w10/1637_A.md           1637 Advent → Holy Week
    ingest/spines-w10/1928_propers.md     1928 Propers.pdf raw two-column spine
    ingest/spines-w10/1979_bcpcolct.txt   1979 collects e-text
    ingest/spines-w10/coe_slug_map.tsv    1662 slug → occasion map
