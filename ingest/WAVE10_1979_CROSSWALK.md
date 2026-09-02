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
lectionary-tables wave (Wave 14).

### E-text defects encountered in 10a
`bcpcolct.txt` lost material in its 1993 keying. In 10a: the **Traditional**
Fourth Sunday of Advent and Eighth Sunday after the Epiphany, and the
**Contemporary** Sixth Sunday after the Epiphany. Each affected cell carries an
inline VERIFY naming the defect. Nothing is reconstructed from memory, and no
substitute source has been added to the allow-list to paper over it.


---

## 10c — the Trinity Sundays: where the evidence runs out

Sub-wave 10c is the case Decision C was written for. 1979 does not merely rename
the Sundays after Trinity; it **replaces the reckoning**, keying the season to
calendar-dated Propers. Trinity 4 is not Proper 4, and no day-level
correspondence exists to anchor a mapping.

That matters because it removes the corroboration 10a relied on. There, a low
full-text score with a high opening score was trustworthy — the Epiphany collect
scores **0.39 full / 1.00 opening** and is a genuine modernized descendant,
because it is the collect for the same day. In 10c nothing plays that role, and
collects share stock openings ("O God, who...", "Almighty God..."), so opening
similarity alone is **formula noise**: `trinity-22` scores 0.04 full / 0.80
opening against Proper 6, which is no evidence of descent whatsoever.

**Rule adopted, as the faithful reading of Decision C:**

- Where the DAY corresponds (all of 10a, and Easter/Ascension/Whitsunday in 10c),
  a high opening score is sufficient — the day corroborates it.
- Where the day does NOT correspond (Trinity → Propers), only a **high full-text
  score** is sufficient. A lineal descendant that merely modernizes retains most
  of its words. Opening-only agreement is recorded as **unproven** and does not
  drive a mapping.

Forcing the unproven ones onto historic slugs would fabricate a cross-edition
comparison, which the prime directive forbids outright.

### Evidence (Traditional set, scored against the 1928 collects)

Confident descendants (full-text ≥ 0.55):

| historic slug | 1979 occasion | full | open |
|---|---|---:|---:|
| `trinity-1` | Sixth Sunday after the Epiphany | 0.86 | 0.90 |
| `trinity-4` | Proper 12 | 0.78 | 1.00 |
| `trinity-6` | Sixth Sunday of Easter | 0.61 | 1.00 |
| `trinity-7` | Proper 17 | 0.72 | 1.00 |
| `trinity-11` | Proper 21 | 0.75 | 1.00 |
| `trinity-12` | Proper 22 | 0.81 | 1.00 |
| `trinity-13` | Proper 26 | 0.64 | 0.94 |
| `trinity-17` | Proper 23 | 0.78 | 0.95 |
| `trinity-19` | Proper 19 | 0.80 | 0.94 |
| `trinity-20` | Proper 2 | 0.59 | 0.87 |

Unproven (opening-only agreement; NOT mapped): `trinity-2`, `trinity-3`,
`trinity-5`, `trinity-8`, `trinity-9`, `trinity-10`, `trinity-14`, `trinity-15`,
`trinity-16`, `trinity-18`, `trinity-21`, `trinity-22`, `trinity-23`,
`trinity-24`, `trinity-25`.

### RESOLVED (maintainer, 2026-08-31): option (a) — place by lineage

> **FLAGGED FOR REVIEW.** The maintainer chose (a) and asked that the choice be
> recorded as needing review — not that it is known to be wrong. It is a
> considered trade-off held open on purpose: a later pass should look at it
> again with fresh evidence and may keep (a) or prefer (b).

Where a Sunday after Trinity's collect survives in 1979 **at a Proper**, the 1979
collect is placed at the historic slug, so `git diff v1928 v1979` shows the
modernization. What that costs, stated plainly:

- It attaches a 1979 collect to a **day 1979 does not observe**. The file asserts
  "this is the collect for the Nth Sunday after Trinity", and 1979 has no such
  Sunday.
- It leaves the 1979 calendar **partially represented**: the Propers appear only
  through the historic slugs they map onto, not as occasions in their own right.
- Every cell placed this way carries an inline `<!-- VERIFY -->` saying so, so the
  claim is never silent.

Applied to eight slugs: `trinity-4` (Proper 12), `trinity-7` (17), `trinity-11`
(21), `trinity-12` (22), `trinity-13` (26), `trinity-17` (23), `trinity-19` (19),
`trinity-20` (2).

**Deliberately NOT applied** to `trinity-1` and `trinity-6`, whose confident
descendants are 1979's Sixth Sunday after the Epiphany and Sixth Sunday of Easter.
Those are real DAYS that 1979 keeps and that the repo already carries at
`epiphany-6` and `easter-5`. Placing them again at a Trinity slug would put one
1979 text at two slugs and invent a second occasion for it. They are `absent:`
instead, with the lineage recorded here.

The fifteen unproven slugs and Whitsun Monday/Tuesday are `absent:` at 1979 —
1979 neither observes those days nor supplies a collect the evidence ties to them.

**Original question, kept for the record.** **Open question for the maintainer**, because it changes what the repo asserts and
is not settled by the evidence: for a Sunday after Trinity whose collect 1979
carries at a Proper, do we (a) place the 1979 collect at the historic slug — the
lineage reading of Decision C, which yields a modernization diff but attaches a
collect to a day 1979 does not observe; or (b) mark the historic slugs `absent:`
at 1979 and give the Propers their own `proper-N` slugs — which is truer to the
1979 calendar but yields no diff for the Trinity season? 10a and 10b needed no
such choice, since every occasion there survives as a day.
