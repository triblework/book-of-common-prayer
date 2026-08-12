# Wave 5 — Baptism family + Confirmation: confirmed source map

Four services, four files under `occasional-offices/`:
`public-baptism.md`, `private-baptism.md`, `baptism-riper-years.md`, `confirmation.md`.

## Presence (confirmed against sources; encode in editions.yaml)
Ten daily-office editions carry public-baptism / private-baptism / confirmation:
English 1549 1552 1559 1604 1662, Scottish 1637, American 1789 1892 1928 1979.
ABSENT at 1764 (Communion-only "Wee Bookie") and inherited-absent at 1929.
  → add the 3 services to those ten `present:` lists; add the 3 to 1764 `absent:`.
  → 1929 inherits the drop (parent 1764 lacks them) — no change needed.

baptism-riper-years is a 1662 ADDITION. Present at: 1662, 1789, 1892.
  ABSENT at 1928 and 1979 (both fold adult baptism into a single Holy Baptism
  office — no separate riper-years service). Absent (by pre-existence) at
  1549/1552/1559/1604/1637 (Scottish line forks at 1604, before 1662).
  → add baptism-riper-years to `present:` of 1662, 1789, 1892.
  → add baptism-riper-years to `absent:` of 1928 (parent 1892 has it).
  → 1979 inherits the drop (parent 1928 lacks it) — no change needed.

## Public Baptism (occasional-offices/public-baptism)
- 1549  justus 1549/Baptism_1549.htm                      [DONE, flagship]
- 1552  justus 1552/Baptism_1552.htm                      [DONE, flagship]
- 1559  justus 1559/Baptism_1559.htm
- 1604  DERIVE from 1559 + justus-1559-apparatus deltas (see below)
- 1662  CoE public-baptism-infants
- 1637  justus Scotland/Baptism_1637.htm
- 1789  justus 1789/Baptism_1789.htm      (Public section)
- 1892  justus 1892/Baptism_1892.htm      (Public section)
- 1928  justus 1928/Baptism.htm           (single "Holy Baptism" office, Children+Adults folded)
- 1979  bcpspecl.txt  <Holy Baptism>      (transform-script; content-filter workaround)

## Private Baptism (occasional-offices/private-baptism)
Same justus/CoE baptism pages (the "…baptised in private houses" section):
- 1549  justus 1549/Baptism_1549.htm  ("OF THEM THAT BE BAPTYSED IN PRIVATE HOUSES")
- 1552  justus 1552/Baptism_1552.htm
- 1559  justus 1559/Baptism_1559.htm
- 1604  DERIVE from 1559 + apparatus — **the Hampton Court change**: 1604 adds the
        heading "[TO BE MINISTRED BY THE MINISTER OF THE PARISH, OR ANY OTHER LAWFUL
        MINISTER, THAT CAN BE PROCURED.]" + a 1604 rubric ("1604: > And also…") and
        word changes ("finde"/"bring"/"all is well done"/"such uncertaine answers").
- 1662  CoE private-baptism-infants
- 1637  justus Scotland/Baptism_1637.htm  ("Private Baptisme")
- 1789  justus 1789/Baptism_1789.htm      (#Private Baptism)
- 1892  justus 1892/Baptism_1892.htm      (#PrivateBaptism)
- 1928  justus 1928/Baptism.htm           (PRIVATE BAPTISM + THE RECEIVING OF ONE PRIVATELY BAPTIZED + CONDITIONAL)
- 1979  bcpspecl.txt  <Emergency Baptism>  (+ Conditional Baptism) (transform-script)

## Baptism of Riper Years (occasional-offices/baptism-riper-years)
- 1662  CoE public-baptism-such-are-riper   (NEW in 1662)
- 1789  justus 1789/Baptism_1789.htm      (#Adult Baptism — "BAPTISM TO SUCH AS ARE OF RIPER YEARS")
- 1892  justus 1892/Baptism_1892.htm      (#Adult Baptism)
- (1928/1979 absent — folded into single office)

## Confirmation (occasional-offices/confirmation)
- 1549  justus 1549/Confirmation_1549.htm  (COMBINED w/ Catechism — extract Confirmation ONLY)
- 1552  justus 1552/Confirmation_1552.htm
- 1559  justus 1559/Confirmation_1559.htm  (COMBINED w/ Catechism — extract Confirmation ONLY)
- 1604  DERIVE from 1559 + apparatus — 1604 changed the preface title and ADDED the
        renewal questions/answers ("The following questions & answers were added in 1604");
        word changes ("workes, the pompes and"; 'bothe' removed; 'prayers').
- 1662  CoE order-confirmation
- 1637  justus Scotland/Confirmation_1637.htm
- 1789  justus 1789/Confirmation_1789.htm
- 1892  justus 1892/Confirmation_1892.htm
- 1928  justus 1928/Confirnation.htm   (NOTE justus filename typo "Confirnation"; page bundles the Offices of Instruction — extract Confirmation ONLY)
- 1979  bcpastrl.txt  Confirmation rite  (Pastoral Offices, FIRST office; page 413-419;
        from "Concerning the Service" through "A Form of Commitment to Christian Service",
        bounded by "The Celebration and Blessing of a Marriage"). NOTE: handoff said
        bcpepscl.txt — that is WRONG; bcpepscl.txt is Ordination only. (transform-script)

## 1604 apparatus (verbatim, from justus 1559 pages)
Baptism:  `* "the" in 1604.` · `[…LAWFUL MINISTER…] * Added in 1604.` ·
          `1604: > And also…` (private-baptism rubric) ·
          `* "finde" and "bring" in 1604.` · `* "all is well done" in 1604.` ·
          `* "such uncertaine answers" in 1604.`
Confirm:  `1604 Title TO…` · `* "workes, the pompes and" in 1604.` ·
          `The following questions & answers were added in 1604` ·
          `1559 Title Confirmation, or laying on of hands. 1604 Title OUR…` ·
          `* 'bothe' removed in 1604.` · `† 'prayers' in 1604`

## CoE note
CoE slugs return the WHOLE-book page (~550K HTML) with the office embedded; slice to
the office when authoring. Base: churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/<slug>
