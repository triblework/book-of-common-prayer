# Wave 10 — the 1979 crosswalk manifest

Authoring-only. Implements **Decision C**: make `git diff <historic> v1979`
meaningful *wherever a genuine correspondence exists*, and nowhere else. This
file records, per occasion, the 1979 mapping and the evidence for it, and it
drives the 1979 rows in `editions.yaml`.

Evidence is mechanical, not remembered. Two scripts produce it:

- `ingest/w10_xw_sameday.py` — for each 1979 occasion, compares its collect with
  the collect the historic books appoint **on that same day**, scoring both the
  full text and the opening clause.
- `ingest/w10_xw_reverse.py` — for each historic collect, finds where (if
  anywhere) it survives in the 1979 book.

Saved output: `ingest/spines-w10/xw_sameday_{trad,contemp}.txt`,
`ingest/spines-w10/xw_reverse_10a.txt`.

Both metrics are needed. The Epiphany collect scores only **0.39** on full text
but **1.00** on its opening: 1979 keeps the historic opening and rewrites the
second half. That is a modernized descendant, which full-text similarity alone
would have thrown away.

---

## The distinction this manifest turns on

Decision C's "map by LINEAGE, not by calendar number" guards against the
Trinity → Pentecost renumbering, where *the days themselves* do not correspond
(Trinity 4 is not Proper 4). **In sub-wave 10a that hazard does not arise**: every
10a occasion is a fixed day or a fixed Sunday that 1979 still keeps, so the
occasion correspondence is exact and unambiguous.

So a 10a slug maps by day, and the question the manifest answers per occasion is
the *second* one: **is the collect 1979 appoints on that day the descendant of
the historic one, or a replacement?** Both outcomes are truthful body diffs at the
same slug — "on this day, 1979 prays these words" — and neither fabricates a
comparison. What *would* fabricate one is moving a 1979 collect onto a historic
slug whose day it does not occupy; nothing here does that.

Where a historic collect is replaced on its own day but **survives elsewhere in
1979**, that is recorded as a cross-reference, not as a slug mapping. Those
destinations are Propers, which belong to sub-wave 10c; the mapping is resolved
there, and recording it now is what keeps 10a's slugs forward-compatible.

---

## 10a — the manifest

`full`/`open` = same-day similarity (Traditional set). "Survives at" comes from
the reverse scan.

| slug | 1979 occasion | full | open | collect | rationale |
|---|---|---:|---:|---|---|
| `advent-1` | First Sunday of Advent | 0.96 | 1.00 | **continues** | Kept almost verbatim; the diff is pure modernization. |
| `advent-2` | Second Sunday of Advent | 0.03 | 0.34 | **replaced** | New collect on this day. The historic collect survives at **Proper 28** (0.88/1.00) → 10c. |
| `advent-3` | Third Sunday of Advent | 0.03 | 0.39 | **replaced** | New collect. The historic collect has no confident match in 1979 (best 0.05/0.54 — formula noise). |
| `advent-4` | Fourth Sunday of Advent | — | — | **e-text defect** | The Traditional collect is LOST from `bcpcolct.txt`; the Contemporary one survives. Carried with a VERIFY; not reconstructed. |
| `christmas-day` | The Nativity of Our Lord: Christmas Day | 1.00 | 1.00 | **continues** | 1979 prints three collects for the day; one is the historic collect unchanged. |
| `christmas-1` | First Sunday after Christmas Day | 0.10 | 0.59 | **replaced** | The 1928 book repeats the Christmas Day collect here; 1979 appoints a distinct one. The collect 1979 uses is the historic **`christmas-2`** collect (0.79/1.00) — a shift *within* 10a. |
| `christmas-2` | Second Sunday after Christmas Day | 0.38 | 0.31 | **replaced** | Its historic collect moved to the First Sunday after Christmas (above); 1979 appoints a new one here. |
| `circumcision` | The Holy Name | 0.04 | 0.38 | **replaced**, day renamed | Same day (1 January), so same slug; the 1979 title change is a heading diff. New collect. |
| `epiphany` | The Epiphany | 0.39 | 1.00 | **continues** | Historic opening kept, second half rewritten — the modernization case. |
| `epiphany-1` | First Sunday after the Epiphany: The Baptism of our Lord | 0.04 | 0.35 | **replaced** | 1979 makes the day the Baptism of our Lord with a new collect. The historic collect survives at **Proper 10** (0.86/1.00) → 10c. |
| `epiphany-2` | Second Sunday after the Epiphany | 0.11 | 0.40 | **replaced** | Historic collect survives at **1979 Epiphany 4** (0.54/1.00) — a shift within the season. |
| `epiphany-3` | Third Sunday after the Epiphany | 0.20 | 0.28 | **replaced** | No confident survival (best 0.45/0.63). |
| `epiphany-4` | Fourth Sunday after the Epiphany | 0.11 | 0.42 | **replaced** | 1979 appoints the historic `epiphany-2` collect here (see above). |
| `epiphany-5` | Fifth Sunday after the Epiphany | 0.08 | 0.29 | **replaced** | No confident survival (best 0.06/0.65 — formula noise). |
| `epiphany-6` | Sixth Sunday after the Epiphany | 0.03 | 0.31 | **replaced** | Historic collect survives at **Proper 27** (0.57/1.00) → 10c. Contemporary set is missing this occasion in the e-text → VERIFY. |
| `epiphany-7` | Seventh Sunday after the Epiphany | — | — | **new** | No historic counterpart: the historic books have only six Sundays after the Epiphany. Own slug; never forced onto a historic one. |
| `epiphany-8` | Eighth Sunday after the Epiphany | — | — | **new** | As above. Present in the Contemporary set; **missing from the Traditional set** in the e-text → VERIFY. |
| `epiphany-last` | Last Sunday after the Epiphany | — | — | **new** | 1979 introduces this Sunday; no historic ancestor. Own slug. |

### Traditional vs Contemporary
The Traditional collect sits at `## The Collect`, carrying the `v1928→v1979`
lineage diff. The Contemporary collect sits alongside at
`## The Collect (Contemporary)`, so its larger rewrite is visible without
corrupting that diff (Decision C.3 — the Rite I / Rite II pattern).

### Readings
1979 replaced the one-year eucharistic lectionary with the three-year (A/B/C)
lectionary, so it appoints **three** reading sets per Sunday. These are
structurally incommensurable with the single citation the historic books print,
and Decision C.4 forbids cramming them into that slot. The 1979 cells therefore
carry **collects only**: the `## The Epistle` / `## The Gospel` anchors inherited
from 1928 are dropped, which is the truthful statement that 1979 appoints no
single Epistle and Gospel for the day. The three-year sets are deferred to the
lectionary-tables wave (Wave 12).

### E-text defects encountered in 10a
`bcpcolct.txt` lost material in its 1993 keying. In 10a: the **Traditional**
Fourth Sunday of Advent and Eighth Sunday after the Epiphany, and the
**Contemporary** Sixth Sunday after the Epiphany. Each affected cell carries an
inline VERIFY naming the defect. Nothing is reconstructed from memory, and no
substitute source has been added to the allow-list to paper over it.
