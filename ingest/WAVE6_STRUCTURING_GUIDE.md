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

### occasional-offices/burial  (exemplar: editions/1552)
```
## The Procession       (rubric + "I am the resurrection…", "I know that my Redeemer…", "We brought nothing…")
## At the Grave         ("Man that is born of a woman…", "In the midst of life we be in death…")
## The Committal        (the casting of earth; 1549 "I commend thy soul to God…earth to earth"; 1552+ "Forasmuch as it hath pleased…we commit his body")
## The Anthem           ("I heard a voice from heaven…")
## The Commendation     (1549 ONLY — the prayers for the dead after the anthem: "We commend into thy hands…the soul", "Almighty God, we give thee hearty thanks for this thy servant")
## The Psalms           (1549 ONLY — the office of Psalms said in church: Ps 116 Dilexi quoniam, Ps 146 Lauda anima mea, Ps 139 Domine probasti)
## The Lesson           (1 Corinthians 15 "Christ is risen from the dead…")
## The Lord's Prayer    (the Kyrie + Our Father)
## The Suffrages        (1549 ONLY — "Enter not, O Lord, into judgement…", "From the gates of hell…")
## The Prayer           (1549 "O Lord, with whom do live the spirits…"; 1552+ "Almighty God, with whom do live the spirits…")
## The Collect          ("O merciful God, the Father of our Lord Jesus Christ…")
## The Celebration of Holy Communion  (1549 ONLY — Introit Ps 42 Quemadmodum)
## The Epistle          (1549 Communion — 1 Thess. iv "I would not have you ignorant…")
## The Gospel           (1549 Communion — John vi "Jesus said to his disciples…")
```
### occasional-offices/visitation-sick  (format exemplar for markdown conventions: editions/1552/occasional-offices/burial.md — but follow THIS menu)
Includes "The Communion of the Sick" as a section (it is printed with the Visitation across editions).
```
## The Introduction     (rubric + "Peace be in this house, and to all that dwell in it.")
## The Antiphon         ("Remember not, Lord, our iniquities…")
## The Lord's Prayer    (the Kyrie "Lord, have mercy…" + Our Father)
## The Suffrages        ("O Lord, save thy servant…")
## The Prayers          ("O Lord, look down from heaven…", "Hear us, Almighty and most merciful God…")
## The Exhortation      ("Dearly beloved, know this: that Almighty God is the Lord of life and death…")
## The Examination      (the interrogation of faith "Dost thou believe in God the Father almighty?…as it is in Baptism", then the charity/forgiveness/will/restitution/alms rubrics)
## The Absolution       (the special-confession rubric + "Our Lord Jesus Christ, who hath left power to his Church to absolve…I absolve thee…")
## The Collect          ("O most merciful God, which according to the multitude of thy mercies…")
## The Psalm            ("In te Domine speravi" / Psalm 71 [the source may mislabel it "Psal. xxi." — keep as printed + VERIFY, drop any "[actually Psalm 71]" editorial gloss] + the added anthem "O Saviour of the world, save us…")
## The Unction          (1549 ONLY — the anointing of the sick: rubric + "As with this visible oil thy body is outwardly anointed…" — absent from 1552 onward)
## The Blessing         ("The Almighty Lord, which is a most strong tower to all them that put their trust in him…")
## The Communion of the Sick   (the "THE COMMUNION OF THE SICK" heading + its opening rubric + ## The Collect [Almighty everliving God, maker of mankind] + The Epistle [Heb. xii] + The Gospel [John v] + the distribution & spiritual-communion & plague rubrics)
```
Notes: 1549 additionally has the Unction (anointing) and may print extra antiphons/psalms
— include them under the nearest anchor / a faithful `##` heading. 1662 and the American
books rework the exhortation, drop the anointing, and the American line splits out a
separate "Communion of the Sick" (already folded here) and adds prayers — include only
what the edition prints, in printed order. NOTE the 1789 book ALSO has a separate
"Visitation of Prisoners" service — that is OUT OF SCOPE; transcribe only Visitation of
the Sick (+ Communion of the Sick). Place out-of-position marginal citations inline.

### occasional-offices/burial (continued)
The flagship diff is the 1549→1552 Reformation stripping: 1549 is a full requiem
(soul-commendation "I commend thy soul", explicit prayers FOR the dead, an office
of psalms, and a Communion of the dead); 1552 reduces it to the graveside form and
rewrites the Committal ("Forasmuch…we commit his body") and the Prayer to REMOVE
prayer for the dead. Keep the SAME anchor names where a section persists (Committal,
Anchor, Lesson, Prayer, Collect) so the rewrite reads as a body diff; the
1549-only sections (Commendation, Psalms, Suffrages, Celebration, Epistle, Gospel)
simply absent from later books. 1549 prints scripture citations (John xi., Job xix.,
1 Tim. vi., Job i., Job ix., Apoca. xiiii.) in the margin; the justus cleaner may dump
them on their own lines out of position — place each inline at the END of the sentence
it annotates (as the 1552 exemplar does), stripping any editorial gloss like
"[=Revelation]". Later editions (1662/American) add "The sentences", the "Thou knowest,
Lord" reworkings, additional prayers, and (American) a committal at the grave — include
what each prints under the nearest anchor, adding a faithful `##` heading for a clearly
new labelled section.
