# Wave 5 — Baptism family + Confirmation structuring guide (for edition authors)

You are structuring ONE edition of ONE service into the repo format. The **words
are already transcribed** for you in a byte-faithful *spine* file. Your job is to
add MARKDOWN STRUCTURE (anchors, rubric markers, speaker labels) around those
words — **never to change, add, paraphrase, modernize, or invent words.** The
whole point of this project is exact-source diffs; fabrication is the cardinal
sin. When the spine is unclear, keep it as printed and flag with `<!-- VERIFY -->`.

## Format (match the exemplars exactly)
- `#` one title line (title-case the ALL-CAPS source title; keep the source's own
  period spelling, e.g. `# The Ministracion of Baptisme to be used in the Churche.`).
- `## ` section anchors from the menu for this service (below). Include only the
  anchors THIS edition actually has, in the order it uses them. A section's
  presence/absence or a move is itself the meaningful diff.
- `> ` for every rubric (stage direction / instruction). The spine marks most
  rubrics with `> `; keep them. A rubric merged into text — re-mark it.
- Plain lines = spoken/prayed text.
- `**Label.**` bold speaker labels using the designation AS PRINTED
  (`**Answer.**`, `**Minister.**`, `**Priest.**`, `**Aunswere.**`). A line like
  `Answer. I renounce them all` → `**Answer.** I renounce them all`. (CoE spines
  run the label into the text, `Answer.I renounce…` — split it: `**Answer.** I renounce…`.)
- One unit per line for versicles/responses/speaker lines/each heading. Prose
  paragraphs may stay one-per-line (the builder splits sentences later).
- Blank line between blocks.

## Faithfulness (critical)
- Keep the source's period spelling verbatim (Lorde, holye, synnes, geve, baptyse…).
  Do NOT modernize — normalization happens later, mechanically.
- REMOVE justus/CoE apparatus that is NOT liturgical text:
  - editorial glosses inside the text: `laver [=water]` → `laver`, `feare [=revere]` → `feare`.
  - standalone footnote lines: `* head in several printings`, `* "the" in 1604.`
  - image captions / scan notes: `Two pages from the Confirmation service, 1549 BCP.`,
    `First Page of the 1552 Confirmation Service`, `Skip to main content`, `Menu`, `## Social`.
  - When a footnote records a variant reading for a word you keep, drop the footnote
    line but add an inline `<!-- VERIFY: source prints 'X'; footnote notes 'Y' in some printings; confirm against a page scan -->`.
- Obvious OCR letter-scannos (`etemall`→`eternall`, `chide`→`childe`) may be silently
  fixed. If a fix is NOT obvious (a whole wrong word, a bad citation, `Lard` for
  `Lord`), keep as printed and flag inline with `<!-- VERIFY: source prints 'X'; likely 'Y'; kept as printed; confirm against a page scan -->`.
- Do NOT include Catechism Q&A that is bundled on a Confirmation page (1549/1559/1928).
  Keep only the Confirmation office. Where the source prints the Catechism's TITLE
  lines, you MAY keep those title lines (they are source text) but STOP before the
  Question/Answer body; add a plain `<!-- ... -->` note that the Catechism body is
  transcribed under the Catechism service. (See the 1549/1552 confirmation exemplars.)

## Anchor menus (use EXACT spellings; include only what this edition has)

### occasional-offices/public-baptism  (exemplars: editions/1549, editions/1552)
```
## The Introduction
## The Exhortation
## The Flood Prayer
## The Signing with the Cross      (1549 EARLY, before the second prayer; 1552+ AFTER the Baptism — one anchor, it moves)
## The Second Prayer
## The Exorcism                    (1549 only)
## The Gospel
## The Exhortation upon the Gospel
## The Lord's Prayer               (1549 only, mid-office)
## The Creed                       (1549 only)
## The Thanksgiving
## The Address to the Godparents
## The Vows
## The Prayer over the Children    (1552+)
## The Blessing of the Water       (1552+ inline; 1662 has a distinct one)
## The Baptism
## The White Vesture               (1549 only — the Chrisom)
## The Anointing                   (1549 only)
## The Reception                   (1552+)
## The Lord's Prayer               (1552+ post-baptism position)
## The Thanksgiving after Baptism  (1552+)
## The Final Exhortation
## The Rubrics
```

### occasional-offices/private-baptism  (exemplars: editions/1549, editions/1552)
```
## The Introduction
## The Private Baptism             (the emergency form: call on God, name+dip+words, assurance)
## The Examination                 (the "By whom / who present / with what words" questions)
## The Certificate                 ("I certify you…")
## The Gospel
## The Exhortation upon the Gospel
## The Lord's Prayer
## The Creed                       (1549 only, as a separate step; 1552+ fold it into the Vows)
## The Vows
## The White Vesture               (1549 only)
## The Thanksgiving
## The Final Exhortation
## Conditional Baptism             (the "If thou be not baptized already" form)
```
(1662/American add `## The Reception` and `## The Receiving into the Church`
sections and drop older ones — follow the printed structure; add a faithful `##`
heading for a printed section that has no menu anchor.)

### occasional-offices/baptism-riper-years  (exemplar: editions/1662, once authored)
Follows Public Baptism's shape but for adults ("such as are of riper years"),
with adult questions answered by the candidate. Reuse public-baptism anchors that
apply (`## The Exhortation`, `## The Flood Prayer`, `## The Gospel`,
`## The Exhortation upon the Gospel`, `## The Address to the Godparents`,
`## The Vows`, `## The Blessing of the Water`, `## The Baptism`, `## The Reception`,
`## The Lord's Prayer`, `## The Thanksgiving after Baptism`, `## The Final Exhortation`,
`## The Rubrics`), plus `## The Introduction`.

### occasional-offices/confirmation  (exemplars: editions/1549, editions/1552)
```
## The Preface
## The Renewal of Vows             (1662+ — "Do ye here, in the presence of God… renew…"; also the 1604-added questions where present)
## The Confirmation                (versicles + the sevenfold-gifts prayer "Almighty and everliving God, who hast vouchsafed to regenerate…")
## The Signing with the Cross      (1549 ONLY — the "Sign them, O Lord" versicle + "I sign thee with the sign of the cross")
## The Imposition of Hands         (1552+ — "Defend, O Lord, this child/this thy servant with thy heavenly grace…")
## The Lord's Prayer               (1662+)
## The Collect                     ("Almighty and everliving God, which makest us both to will and to do…")
## The Blessing
## The Rubrics
```

## Self-check before finishing (REQUIRED)
```
python3 ingest/fidelity_check.py editions/<YEAR>/occasional-offices/<service>.md ingest/<spine-path>
```
It prints any word in your file NOT in the spine. For EACH flagged word, fix it (a
typo you introduced) or justify it (an obvious OCR fix). Goal: CLEAN, or a short
list of justified OCR fixes only.

## Report back (do NOT paste the liturgical text)
Return only: (1) file path(s) written; (2) ordered `##` anchors used per file;
(3) line count per file; (4) fidelity_check result per file + one-line justification
for each flagged word; (5) each `<!-- VERIFY -->` you added with its reason. Nothing else.
