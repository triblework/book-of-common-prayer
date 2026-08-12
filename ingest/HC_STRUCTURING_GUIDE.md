# Wave 4 — Holy Communion structuring guide (for edition authors)

You are structuring ONE edition's Holy Communion service into the repo format.
The **words are already transcribed** for you in a byte-faithful *spine* file. Your
job is to add MARKDOWN STRUCTURE (anchors, rubric markers, speaker labels) around
those words — **never to change, add, paraphrase, modernize, or invent words.**
The whole point of this project is exact-source diffs; fabrication is the cardinal
sin. When the spine is unclear, keep it as printed and flag with `<!-- VERIFY -->`.

## Inputs
- Your spine: `ingest/spines/<YEAR>.md` — the cleaned source text, in order.
- Format exemplars (READ THESE FIRST):
  - `editions/1662/daily-office/morning-prayer.md` — house format.
  - `editions/1552/holy-communion/holy-communion.md` — a fully-structured HC.
  - `editions/1549/holy-communion/holy-communion.md` — an HC with a different order.
- Output: write `editions/<YEAR>/holy-communion/holy-communion.md`.

## The canonical `##` anchor menu (spec §3.2), in canonical order
Use these EXACT spellings. Place each anchor **in the order THIS edition actually
uses it** (not the menu's order) — a moved section must read as delete-here +
insert-there. Include only the anchors this edition has; omit the rest.

```
## The Lord's Prayer          (opening position, if the edition opens here)
## The Collect for Purity
## The Introit                (1549 proper psalm; later dropped)
## The Ten Commandments       (Decalogue; enters 1552, kept after)
## The Summary of the Law     (American line)
## Kyrie Eleison              (1549 ninefold; American Kyrie)
## Gloria in Excelsis         (early position — 1549)
## The Collects
## The Collect for the King
## A Prayer for the President  (American line replaces the King's collect)
## The Epistle
## The Gospel
## The Nicene Creed
## The Sermon
## The Offertory
## The Prayer for the Whole State of Christ's Church
## The Exhortations
## The Invitation
## The General Confession
## The Absolution
## The Comfortable Words
## The Sursum Corda
## The Preface
## The Proper Prefaces
## Sanctus
## The Prayer of Humble Access
## The Prayer of Consecration
## The Communion              (administration + words of delivery)
## The Lord's Prayer          (post-communion position, 1552+)
## The Prayer of Oblation
## The Prayer of Thanksgiving
## Gloria in Excelsis         (near-the-end position — 1552+)
## The Blessing
## The Rubrics                (incl. the 1552/1662 Declaration on Kneeling — "Black Rubric")
```

`## Gloria in Excelsis` and `## The Lord's Prayer` intentionally appear TWICE.
Populate whichever position this edition uses; the other simply does not appear.
If this edition has a section with no menu anchor and it is a real, named part of
the printed service, you MAY add a faithful `##` heading for it (e.g. the American
`## The Decalogue` / `## The Summary of the Law`), but prefer a menu anchor when one
fits, and never split a single printed prayer across two anchors.

## Formatting rules (match the exemplars exactly)
- `#` one title line (title-case the ALL-CAPS source title; keep source spelling,
  e.g. `# The Order for the Administration of the Lord's Supper, or Holy Communion.`).
- `## ` section anchors from the menu above.
- `> ` for every rubric (stage direction / instruction). The spine already marks
  most rubrics with `> `. Keep them; a rubric that got merged into text, re-mark it.
- Plain lines = spoken/sung text.
- `**Label.**` bold speaker labels, using the designation AS PRINTED in the spine
  (`**Priest.**`, `**Answer.**`, `**Ministre.**`, `**People.**`, `**The Clerkes.**`).
  A line like `Answer. We lift them up...` becomes `**Answer.** We lift them up...`.
- One unit per line is enforced later by the builder's sentence_split; you do NOT
  need to split prose paragraphs yourself, but DO put each versicle/response,
  each speaker line, each offertory sentence, and each heading on its own line.
- Blank line between blocks (after each `##`, around `>` rubrics), as in exemplars.

## Faithfulness rules (critical)
- Keep the source's period spelling verbatim (Lorde, holye, synnes, geve...).
  Do NOT modernize — normalization happens later, mechanically.
- REMOVE justus editorial insertions that are not part of the liturgical text:
  - bracketed glosses inside the text: `dissimulers [dissemblers]` -> `dissimulers`,
    `PREVENT [=go before] us` -> `PREVENT us`, `Zache [Zaccheus]` -> `Zache`.
  - standalone editorial footnote lines: `* study in some printings`,
    `* God of God in several printings.`, `[actually Tobit 4:7]`.
  - image captions / page-scan notes that leaked in: `The Mass, from a 15th C, Prymer`,
    any paragraph explaining an image or the Black Rubric's printing history.
  (The Black Rubric TEXT itself is liturgical — KEEP it, under `## The Rubrics`.
  Only the justus paragraph *describing* the Black Rubric is a caption — drop that.)
- Obvious OCR letter-scannos may be silently fixed (`etemall`->`eternall`,
  `accustomabty`->`accustomably`). If a fix is not obvious, keep as printed + VERIFY.
- Genuine printer errors that are historically real (e.g. a wrong scripture
  citation) are KEPT as printed and flagged: add an inline
  `<!-- VERIFY: source prints 'X'; likely means 'Y'; confirm against a page scan -->`
  on its own line right after the affected line.

## Self-check before you finish (REQUIRED)
Run:
```
python3 ingest/fidelity_check.py editions/<YEAR>/holy-communion/holy-communion.md ingest/spines/<YEAR>.md
```
It prints any word in your file that is NOT in the spine. For EACH flagged word,
either fix it (it was a typo you introduced) or justify it (an obvious OCR fix).
The goal is CLEAN or a short list of justified OCR fixes only. If a real word you
kept is flagged, you changed the spelling — revert to the spine's spelling.

## Report back (do NOT paste the liturgical text)
Return only: (1) the ordered list of `##` anchors you used; (2) the file's line
count; (3) the fidelity_check result and your one-line justification for each
flagged word; (4) each `<!-- VERIFY -->` you added, with its reason. Nothing else.
