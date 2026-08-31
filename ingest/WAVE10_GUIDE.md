# Wave 10 — Collects, Epistles & Gospels: the authoring guide

Authoring-only (never published). Records, once, the decisions every Wave-10
sub-wave (10a–10d) reuses: the file family, the slug scheme, the canonical anchor
menu, and the reading-citation rule. Written during 10a; extend, don't fork.

The three scoping decisions (A seasonal sub-waves, B "full Collect + bare
citation", C 1979 comparability via a crosswalk) are recorded in `HANDOFF.md` and
are **locked**. This file is the *implementation* of them.

---

## 1. File family and slug scheme

One file per **occasion**, under a new service family:

    collects-epistles-gospels/<slug>.md
      -> authoring:  editions/<year>/collects-epistles-gospels/<slug>.md
      -> published:  texts/original/collects-epistles-gospels/<slug>.md

Slugs are **lineage keys**, not calendar indices: the same occasion carries the
same slug in every edition that keeps it, so a reworded collect or a re-appointed
reading reads as a body diff (spec §1.7). A slug is never renumbered; an edition
that renames the occasion changes the `# Title` heading only (a heading diff, the
Wave-9 `front-matter/concerning-the-service` pattern).

The full slug list is fixed up front so nothing has to be renamed in 10b–10d:

| sub-wave | slugs |
|---|---|
| **10a** | `advent-1` `advent-2` `advent-3` `advent-4` `christmas-day` `christmas-1` `christmas-2` `circumcision` `epiphany` `epiphany-1` … `epiphany-6` |
| **10b** | `septuagesima` `sexagesima` `quinquagesima` `ash-wednesday` `lent-1` … `lent-5` `palm-sunday` `monday-before-easter` `tuesday-before-easter` `wednesday-before-easter` `thursday-before-easter` `good-friday` `easter-even` |
| **10c** | `easter-day` `easter-monday` `easter-tuesday` `easter-1` … `easter-5` `ascension-day` `ascension-1` `whitsunday` `whit-monday` `whit-tuesday` `trinity-sunday` `trinity-1` … `trinity-25` |
| **10d** | `st-andrew` `st-thomas` `st-stephen` `st-john-evangelist` `holy-innocents` `conversion-st-paul` `purification` `st-matthias` `annunciation` `st-mark` `st-philip-st-james` `st-barnabas` `st-john-baptist` `st-peter` `st-mary-magdalene` `st-james` `transfiguration` `st-bartholomew` `st-matthew` `st-michael` `st-luke` `st-simon-st-jude` `all-saints` |

Notes on slugs that already need a decision recorded:

- `christmas-1` = "The Sunday after Christmas Day". `christmas-2` = "The Second
  Sunday after Christmas Day", which the **English line does not have**: it is an
  American addition (1789+) and is kept by 1979. Absent at 1549–1662 and 1637.
- `circumcision` = "The Circumcision of Christ"; the 1979 renames the day **The
  Holy Name** — same day, same collect lineage, so **same slug**, renamed title.
- `epiphany-6` is a **1662 addition**: 1549/1552/1559 print only five Sundays
  after the Epiphany. Clean insert at `v1604→v1662`.
- `purification` is titled "The Presentation of Christ in the Temple" in the
  American line — same feast, same slug, heading diff.
- **St. Stephen, St. John the Evangelist and Holy Innocents are 10d, not 10a.**
  The justus 1549 page prints them inside its *Christmas* block, but 1662 and the
  whole American line print them in the **Saints' Days** sequence, which is what
  Decision A's "St. Andrew … All Saints" names. Keeping the three with the other
  fixed feasts keeps each sub-wave one coherent source unit. (Recorded here so the
  choice is auditable; moving them is only a scheduling change, not a rename.)
- 1979-only occasions with **no historic ancestor** (Propers 1–29, St. Joseph,
  The Visitation, St. Mary the Virgin, St. James of Jerusalem, Independence Day,
  Thanksgiving Day, the Common of Saints, the Various Occasions collects) get
  their **own** slugs in 10c/10d. They are never forced onto a historic slug —
  see `WAVE10_1979_CROSSWALK.md` and Decision C.

---

## 2. Canonical anchor menu

Record once, reuse in every edition. An edition populates the anchors it has and
omits the rest; a section that moves or is dropped then reads as exactly that.

```
# <Occasion, as that edition prints it>          <- title heading

## The Introit                                   <- 1549 only: proper-psalm citation
## The Collect
## The Collect (Contemporary)                    <- 1979 only: contemporary-language set
## The Epistle
## The Gospel

## The Introit (Second Communion)                <- 1549 Christmas Day
## The Collect (Second Communion)                <- Christmas Day, where a second Communion is printed
## The Epistle (Second Communion)
## The Gospel (Second Communion)

## The Proper Lessons                            <- 1549 only: proper psalms/lessons at Matins & Evensong
```

Rules:

- **Rubrics** printed with the occasion (`This Collect is to be repeated every
  day…`, the 1637 Gospel responses) stay with their section as `> ` lines.
- **Additional collects.** Where a book prints alternatives ("or this", the 1979
  Christmas Day set of three), they all live under `## The Collect`, separated by
  the source's own rubric (`> Or this.`). Do not invent extra anchors for them.
- **"For the Epistle."** When the appointed Epistle is from the Old Testament the
  books print *For the Epistle* rather than *The Epistle*. Keep the anchor
  `## The Epistle` (so the citation still diffs cleanly) and carry the printed
  label as a `> For the Epistle.` rubric line above the citation.
- `## The Collect (Contemporary)` is the Rite I / Rite II pattern used elsewhere
  in the repo: the 1979 **Traditional** collect goes at `## The Collect` so it
  carries the `v1928→v1979` lineage diff, and the Contemporary rewrite sits
  alongside without corrupting that diff (Decision C.3).

---

## 3. Reading depth — the citation rule (implements Decision B)

The Collect(s) are transcribed **in full**. The Epistle and Gospel are given as
their **appointed citation only** — no incipit, no body. The 1549 Introit is the
proper-psalm citation.

The citation is written to the **precision the edition's own book prints**, in one
house form: modern book name, Arabic numerals, `Book Chapter` or
`Book Chapter:verse`.

| edition | what the book prints | what the file carries |
|---|---|---|
| 1549 / 1552 / 1559 | `The Epistle. Rom. xiii.` (chapter only) | `Romans 13` |
| 1662 | chapter + initial verse | `Romans 13:8` |
| 1637 | `Rom. 13.8.` | `Romans 13:8` |
| 1789 / 1892 / 1928 | `The Epistle. Rom. xiii. 8.` | `Romans 13:8` |

**Why not the end verse.** Only *editorial* apparatus supplies a closing verse:
justus prints `[Romans 13:8-14]` as its own modern identification on the 1549 and
1637 pages, and the Church of England's site renders 1662 as `Romans 13.8-14`. The
books themselves stop at the initial verse. Carrying an end verse for the editions
whose *source* happens to supply one would manufacture a diff out of a difference
between web sites — forbidden by the prime directive. The full modern range is
recorded in `provenance.yaml` instead, where it belongs.

Consequence, and it is the right one: `git diff v1559 v1662 -- …/advent-1.md`
shows `Romans 13` → `Romans 13:8`, which is the real change (initial verse numbers
enter the printed citations). Where the pericope itself is re-appointed — the
American line does this at several occasions — the citation diffs on book/chapter.

**Book-name canonicalization** is a mechanical table in `ingest/w10_cite.py`
(`Rom.`/`Roma.`→`Romans`, `St. Matt.`/`Mat.`/`Matt.`→`Matthew`, `1 Cor.`→`1
Corinthians`, `Apoc.`→`Revelation`, `Phil.`/`Philipp.`→`Philippians`, …). Roman
chapter/verse numerals are converted to Arabic. Every conversion is exercised by
the script's self-check, so a form the table does not know fails loudly rather
than being guessed at.

**1549 Introit.** The 1549 prints the proper psalm in full with its Latin incipit
(`Beatus vir. Psalm i.`). The file carries the citation with the incipit that
identifies it: `Beatus vir. Psalm 1`. (The psalm body is Wave 11, the Psalter.)

---

## 4. Method (file → file; no liturgical text through the model)

Same discipline as Waves 6–9 (`subagent-write-content-filter`): the collect bodies
flow **source → spine → script → file** and are never emitted as model tokens.

1. `ingest/hc_clean.py <url>` — byte-faithful spine from a justus/CoE page.
   `ingest/pdf_spine.py` — spine from the 1928 `Propers.pdf` (its text layer is
   **clean**, unlike the Wave-9 `Front_Matter_1928.pdf`; it is two-column
   landscape, so `ingest/w10_1928_spine.py` splits the columns before slicing).
2. `ingest/w10_slice.py` — the config-driven segmenter. It walks a spine, finds
   the occasion headings and the `The Collect.` / `The Epistle.` / `The Gospel.`
   markers, and emits one file per occasion with the anchor menu above. The
   editorial apparatus is *separated*, not transcribed: on the justus 1549 and
   1789 pages it lives in its own table column, which `ingest/w10_spine.py`
   captures as `NOTE:` lines.
3. `ingest/fidelity_check.py <authored.md> <spine.md>` — the anti-fabrication
   gate. Every authored word must be attested in the spine. Run on every cell.
4. VERIFY items: one `<!-- VERIFY: '<reading>' … -->` per line, doubtful reading
   first and single-quoted (`verify_index.py` keys on it).
5. `ingest/w10_editions.py` wires `editions.yaml`; `ingest/gen_wave10_provenance.py`
   scans the inline VERIFYs into `provenance.yaml` + `SOURCES.md` rows.

---

## 5. Per-edition presence (10a; confirmed against the indexes 2026-08-31)

| edition | present? | source |
|---|---|---|
| 1549 | yes, **with Introits** | justus `1549/Readings_{Advent,Xmas,Epiphany}_1549.htm` |
| 1552 | yes, **Introits dropped** | same pages — 1552/1559 deltas are the annotated apparatus |
| 1559 | yes | same pages (`"Amen"` added at the end of each collect; several occasion titles expanded "in the late 1500's") |
| 1604 | **inherits 1559** | no allow-listed 1604 propers text exists; see the gap note below |
| 1662 | yes | churchofengland.org `collects-epistles-and-gospels{,-N}` (slug map in `ingest/spines-w10/coe_slug_map.tsv`) |
| 1637 | yes | justus `Scotland/Collects1_1637.htm` (Advent–Holy Week) — the page prints **citations only**, which is exactly Decision B's depth |
| 1764 | **absent** | Communion-only "Wee Bookie", as MP/EP/Litany |
| 1929 | absent (inherits the 1764 drop) | |
| 1789 | yes | justus `1789/Readings1789&1892A.htm` |
| 1892 | yes | **same page** — it is a four-edition synoptic (1786 Proposed / 1789 / 1892 / 1928) with a per-edition apparatus column |
| 1928 | yes | the same synoptic, cross-checked against justus `1928/Propers.pdf` |
| 1979 | yes | PD e-text `bcpcolct.txt` (Traditional + Contemporary), via the Decision-C crosswalk |

**Recorded gap — 1604.** The justus apparatus states that *initial verse numbers
(rather than just chapter numbers) were added in 1604*. No allow-listed source
prints the 1604 propers, so that change is **not represented**: 1604 inherits
1559 and the omission is recorded in `SOURCES.md`/`NOTICE.md` rather than
reconstructed. Inferring the 1604 verse numbers from 1662 would be invention.

**Recorded gap — the 1979 e-text.** `bcpcolct.txt` has scattered dropouts where a
heading and its collect were lost in the 1993 keying. In 10a's range the
**Traditional** *Fourth Sunday of Advent* is gone (the Contemporary one survives);
elsewhere the Traditional set is missing *Eighth Sunday after the Epiphany* and
Propers 4/14/25, and the Contemporary set is missing *Sixth Sunday after the
Epiphany* and has a mangled *Fourth Sunday in Lent* heading. Affected cells carry
a `<!-- VERIFY -->` naming the defect; nothing is reconstructed from memory.
