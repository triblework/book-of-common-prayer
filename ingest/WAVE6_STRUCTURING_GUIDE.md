# Wave 6 — Pastoral occasional offices structuring guide (for edition authors)

You are structuring ONE edition of ONE service into the repo format. The **words
are already transcribed** for you in a byte-faithful *spine* file. Your job is to
add MARKDOWN STRUCTURE (anchors, rubric markers, speaker labels) around those
words — **never to change, add, paraphrase, modernize, or invent words.** The
whole point of this project is exact-source diffs; fabrication is the cardinal
sin. When the spine is unclear, keep it as printed and flag with `<!-- VERIFY -->`.

## Format (match the exemplars exactly)
- `#` one title line (title-case the ALL-CAPS source title; keep the source's own
  period spelling, e.g. `# The Forme of Solemnizacion of Matrimonie.`).
- `## ` section anchors from the menu for this service (below). Include only the
  anchors THIS edition actually has, in the order it uses them. A section's
  presence/absence or a move is itself the meaningful diff.
- `> ` for every rubric (stage direction / instruction). The spine marks most
  rubrics with `> `; keep them. A rubric merged into text — re-mark it. NOTE: the
  justus cleaner sometimes marks a line `> ` that is actually SPOKEN text (an
  artifact of a source pilcrow, e.g. "With this ring I thee wed…", "Those whom God
  hath joined together…", a blessing). If a `> ` line is clearly words to be
  said/sung, render it as PLAIN spoken text, not a rubric. Use judgement; the
  exemplars show the pattern.
- Plain lines = spoken/prayed text.
- `**Label.**` bold speaker labels using the designation AS PRINTED
  (`**Answere.**`, `**Minister.**`, `**Priest.**`, `**Answer.**`, `**People.**`).
  A line like `Answer. Who putteth her trust in thee` → `**Answer.** Who putteth
  her trust in thee`. (CoE spines run the label into the text, `Answer.Who
  putteth…` — split it.)
- One unit per line for versicles/responses/speaker lines/each heading. Prose
  paragraphs may stay one-per-line (the builder splits sentences later).
- Canticle/psalm verses: one verse per line; render the mediant as ` : `
  (space-colon-space) where the source points it.
- Blank line between blocks.

## Faithfulness (critical)
- Keep the source's period spelling verbatim (Lorde, holye, wedlocke, buryeng…).
  Do NOT modernize — normalization happens later, mechanically.
- REMOVE justus/CoE apparatus that is NOT liturgical text:
  - editorial glosses inside the text: `Hierusalem [Jerusalem]` → `Hierusalem`,
    `conversacyon [=behavior]` → `conversacyon`, `thone [the one]` → `thone`.
  - standalone footnote lines recording variant readings: `* "into" in 1604.`
  - image captions / scan notes: `Matrimony, from a 15th C. Pontifical`,
    `Skip to main content`, `Menu`, `## Social`, `Some functionality has been
    disabled`, JavaScript notices, `Search`, cookie banners.
  - When a footnote records a variant reading for a word you keep, drop the footnote
    line but add an inline `<!-- VERIFY: source prints 'X'; footnote notes 'Y' in some printings; confirm against a page scan -->`.
- KEEP `[square brackets]` that are BCP optional-text typography (CoE 1662 prints
  e.g. `This is the first [second, or third] time of asking.`) — those brackets are
  part of the printed text, not an editorial gloss. (Rule of thumb: a gloss gives a
  modern synonym/definition; optional-text brackets give real liturgical words.)
- Obvious OCR letter-scannos (`etemall`→`eternall`, `chide`→`childe`, a word broken
  by a stray space like `speak yng`→`speakyng`) may be silently fixed. If a fix is
  NOT obvious (a whole wrong word, a bad citation, `Lard` for `Lord`), keep as
  printed and flag inline with `<!-- VERIFY: source prints 'X'; likely 'Y'; kept as printed; confirm against a page scan -->`.

## Self-check before finishing (REQUIRED)
```
python3 ingest/fidelity_check.py editions/<YEAR>/occasional-offices/<service>.md <spine-path>
```
It prints any word in your file NOT in the spine. For EACH flagged word, fix it (a
typo you introduced) or justify it (an obvious OCR fix). Goal: CLEAN, or a short
list of justified OCR fixes only.

## Report back (do NOT paste the liturgical text)
Return only: (1) file path written; (2) ordered `##` anchors used; (3) line count;
(4) fidelity_check result + one-line justification for each flagged word;
(5) each `<!-- VERIFY -->` you added with its reason. Nothing else.

---

## Anchor menus (use EXACT spellings; include only what this edition has)

### occasional-offices/matrimony  (exemplars: editions/1549, editions/1552)
```
## The Banns
## The Exhortation          ("Dearly beloved, we are gathered together…")
## The Charge               ("I require and charge you…" + the deferral rubric)
## The Consent              ("Wilt thou have this woman/man…" — I will)
## The Giving in Marriage   ("Who giveth this woman to be married to this man?")
## The Vows                 ("I N. take thee N. …I plight/give thee my troth")
## The Ring                 ("With this ring I thee wed…")
## The Prayer               ("O eternal God, Creator and Preserver…")
## The Joining of Hands     ("Those whom God hath joined together…")
## The Pronouncement        ("Forasmuch as N. and N. have consented…")
## The Blessing             ("God the Father… bless, preserve, and keep you…")
## The Psalm                (Beati omnes / Deus misereatur)
## The Lord's Prayer        (the Kyrie "Lord have mercy…" + Our Father)
## The Suffrages            ("O Lord, save thy servant…")
## The Prayers              ("O God of Abraham…", "O merciful Lord…", "O God, which by thy mighty power…")
## The Nuptial Blessing     ("Almighty God, who at the beginning did create…")
## The Homily               ("All ye which be married…" the duties of husbands and wives)
## The Rubrics              (final rubrics, e.g. the new-married must receive the Communion)
```
Later editions differ: the 1662/American books may drop the Psalm/Kyrie/suffrages
block or the concluding homily-rubric wording, add the sign-of-troth phrasing, or
reword the second nuptial blessing. Include only the anchors the edition prints, in
its printed order. If an edition prints a clearly-labelled section with no menu
anchor, add a faithful `##` heading for it.

### occasional-offices/commination  (exemplar: editions/1552)
```
## The Introduction     ("Brethren, in the primitive Church there was a godly discipline…")
## The Curses           (the Deuteronomy curses "Cursed is he that…" with the people's "Amen")
## The Exhortation      ("Now seeing that all they be accursed…")
## The Psalm            (Miserere mei Deus / Psalm 51)
## The Lord's Prayer    (the Kyrie "Lord have mercy…" + Our Father)
## The Suffrages        ("O Lord, save thy servants…")
## The Prayers          ("O Lord, we beseech thee…", "O most mighty God…")
## Turn Thou Us         ("Turn thou us, O good Lord…")
```
Notes: the FIRST curse ("Cursed is the man that maketh any carved or molten
image…") is spoken by the priest — render it as PLAIN text opening The Curses,
then the rubric "And the people shall answer, and say," then "Amen", then the
labelled `**Minister.**`/`**Answere.**` curse–response pairs. The `Turn Thou Us`
rubric differs by edition (1549 calls it an anthem "said or sung"; 1552+ the
people say it "after the Minister") — that rubric change is a meaningful diff.
Scripture citations: keep the printed citation (e.g. `Psa. cxviii.`) but STRIP any
justus modern-verse gloss inside the brackets (`[Psa. cxviii. =Ps. 119:21]` →
`Psa. cxviii.`; `[Esai. (Isaiah) xxvi.]` → `Esai. xxvi.`) and DROP pure word
glosses (`[=acknowledging]`, `[betime, =in good time]`, `[past]`).

### occasional-offices/churching  (exemplars: editions/1549, editions/1552)
```
## The Introduction   (rubric + "Forasmuch as it hath pleased Almighty God…")
## The Psalm          (1549/1552 Ps 121 "Levavi oculos"; 1662 & American use Ps 116 "Dilexi quoniam" and/or Ps 127 "Nisi Dominus")
## The Lord's Prayer  (the Kyrie "Lord have mercy…" + Our Father)
## The Suffrages      ("O Lord, save this woman thy servant…")
## The Prayer         ("O Almighty God, which hast delivered…")
## The Rubrics        (the offerings + Communion rubric)
```
Notes: the 1549 title is "The Order of the Purification of Women" (older name); 1552+
retitle it "The Thanksgiving of Women after Childbirth, commonly called the Churching
of Women." 1662 prints TWO psalms (Ps 116 and Ps 127, to be used one or other) — include
both as printed under The Psalm. Some editions add a preliminary rubric that the service
or its concluding prayer may be used at the Minister's discretion. Include only the
anchors the edition prints, in printed order.
