# Wave 6 — Pastoral occasional offices: confirmed source map

Five services, five files under `occasional-offices/`:
`matrimony.md`, `visitation-sick.md`, `burial.md`, `churching.md`, `commination.md`.

All source URLs below were CONFIRMED against the justus per-year index pages
(`<year>/BCP_<year>.htm`), the Scotland index (`Scotland/BCP_1637.htm`), the CoE
BCP index, and the 1979 PD ASCII e-text — on 2026-08-13.

## Presence (confirmed; encode in editions.yaml)

Ten daily-office editions carry Matrimony / Visitation / Burial:
English 1549 1552 1559 1604 1662, Scottish 1637, American 1789 1892 1928 1979.
ABSENT at 1764 (Communion-only "Wee Bookie"); inherited-absent at 1929 (this
repo's Scottish line is Communion-only after 1637, exactly as MP/EP/Baptism).
  → add the 3 services to those ten `present:` lists; add the 3 to 1764 `absent:`.
  → 1929 inherits the drop (parent 1764 lacks them) — no change needed.

Churching of Women: English 1549 1552 1559 1604 1662, Scottish 1637,
American 1789 1892 1928, AND 1979 (as its lineal replacement "A Thanksgiving for
the Birth or Adoption of a Child" — DECISION: represent under churching.md; the
churching→thanksgiving transformation is the meaningful diff). Absent 1764/1929.
  → add churching to `present:` of those 9 + 1979 = 10 editions; add to 1764 `absent:`.

Commination: English 1549 1552 1559 1604 1662, Scottish 1637. DROPPED on the
American line: 1789 forks from 1662 (which HAS it) so 1789 must list
`occasional-offices/commination` in `absent:`; 1892/1928/1979 inherit the absence.
Absent 1764/1929 (Communion-only). The 1979 book has no Commination; its nearest
relative is the Ash Wednesday liturgy — NOT mapped (prefer absence), per spec.
  → add commination to `present:` of English 1549-1662 + 1637; add to 1789 `absent:`.

## 1604 apparatus finding (checked the justus 1559 pages)
- Matrimony 1604: NO apparatus mentions → unchanged from 1559 → `reviewed-unchanged`,
  inherit 1559 (author NO 1604 file).
- Visitation 1604: NO apparatus mentions → unchanged from 1559 → inherit 1559.
- Burial 1604: ONE change — `* "into" in 1604.` → author a 1604 burial.md deriving
  from 1559 with that single word change.
- Churching 1604: ONE change — `* "Minister" in 1604.` → author a 1604 churching.md.
- Commination 1604: check the 1559 commination apparatus (bundled on
  Churching_of_Women_1559.htm#Commination) when authoring; derive accordingly.

## Matrimony (occasional-offices/matrimony)
- 1549  justus 1549/Marriage_1549.htm
- 1552  justus 1552/Marriage_1552.htm
- 1559  justus 1559/Marriage_1559.htm
- 1604  DERIVE from 1559 (reviewed-unchanged — no apparatus deltas)
- 1662  CoE  form-solemnization-matrimony
- 1637  justus Scotland/Marriage_1637.htm
- 1789  justus 1789/Marriage_1789.htm
- 1892  justus 1892/Marriage_1892.pdf   (text-layer PDF; Read tool extracts clean text)
- 1928  justus 1928/Marriage.htm        (Churching bundled at #Churching_Women — extract Marriage only)
- 1979  bcpastrl.txt  "The Celebration and Blessing of a Marriage" (contemporary; transform-script)

## Visitation of the Sick (occasional-offices/visitation-sick)
Includes "The Communion of the Sick" section as printed (bundled across editions).
- 1549  justus 1549/Visitation_Sick_1549.htm  (+ #Communion section)
- 1552  justus 1552/Visitation_Sick_1552.htm
- 1559  justus 1559/Visitation_Sick_1559.htm
- 1604  DERIVE from 1559 (reviewed-unchanged)
- 1662  CoE  visitation-sick  + communion-sick  (concatenate the two printed-consecutive offices)
- 1637  justus Scotland/Visitation_Sick_1637.htm
- 1789  justus 1789/Visitation_Sick_1789.htm  (NOTE: 1789 also has a separate
        Visitation_Prisoners_1789.htm — OUT OF SCOPE, do not include)
- 1892  justus 1892/Visitation_Sick_1892.pdf
- 1928  justus 1928/Visitation_Sick.htm  (+ #Communion)
- 1979  bcpastrl.txt  "Ministration to the Sick" (Part I Ministry of the Word,
        Part II Laying on of Hands and Anointing, Part III Holy Communion; transform-script)

## Burial of the Dead (occasional-offices/burial)
- 1549  justus 1549/Burial_1549.htm
- 1552  justus 1552/Burial_1552.htm
- 1559  justus 1559/Burial_1559.htm
- 1604  DERIVE from 1559 + `* "into" in 1604.`
- 1662  CoE  burial-dead
- 1637  justus Scotland/Burial_1637.htm
- 1789  justus 1789/Burial_1789.htm
- 1892  justus 1892/Burial_1892.pdf
- 1928  justus 1928/Burial.htm  (has #Child — the Burial of a Child; include as printed)
- 1979  bcpastrl.txt  "The Burial of the Dead: Rite One" (office file) +
        "The Burial of the Dead: Rite Two" (## Rite Two section) — handle BOTH, like MP/HC.

## Churching of Women (occasional-offices/churching)
- 1549  justus 1549/Purification_Women_1549.htm  (1549 title: "The Order of the Purification of Women")
- 1552  justus 1552/Churching_Women_1552.htm
- 1559  justus 1559/Churching_of_Women_1559.htm
- 1604  DERIVE from 1559 + `* "Minister" in 1604.`
- 1662  CoE  churching-women
- 1637  justus Scotland/Churching_of_Women_1637.htm
- 1789  justus 1789/Churching_of_Women_1789.htm
- 1892  justus 1892/Churching_of_Women_1892.pdf
- 1928  justus 1928/Marriage.htm#Churching_Women  (bundled on the Marriage page — extract Churching only)
- 1979  bcpastrl.txt  "A Thanksgiving for the Birth or Adoption of a Child" (transform-script)

## Commination (occasional-offices/commination)
- 1549  justus 1549/Ashwednesday_1549.htm  ("The First Day of Lent, commonly called Ash-Wednesday"
        = the 1549 form of the Commination: the exhortation + the "Cursed is he..." curses + Ps 51)
- 1552  justus 1552/Commination_1552.htm
- 1559  justus 1559/Churching_of_Women_1559.htm#Commination  (bundled after churching)
- 1604  DERIVE from 1559 + apparatus
- 1662  CoE  commination
- 1637  justus Scotland/Commination_1637.htm
- (American line 1789/1892/1928/1979: ABSENT — model as `absent:` at 1789)

## CoE note
CoE base: churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/<slug>
`scrape.fetch` returns 200 even for a wrong slug (SPA shell); the correct slugs
above yield real content (verified: matrimony ~16.8K chars, commination ~12.2K).
CONFIRMED slugs: form-solemnization-matrimony, visitation-sick, communion-sick,
burial-dead, churching-women, commination.

## 1892 note
justus serves the 1892 occasional offices ONLY as text-layer PDFs (its HTML index
links back to the 1789 HTML). The PDFs are WordPerfect-generated with a real text
layer — the Read tool extracts clean text. Source of truth = the 1892 PDF; the
Satucket header notes "few significant changes vs 1789" (verify each cell; do not
assume identical).
