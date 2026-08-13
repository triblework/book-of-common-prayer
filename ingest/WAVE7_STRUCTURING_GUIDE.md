# Wave 7 — Catechism structuring guide (for edition authors)

You are structuring ONE edition of the **Catechism** into the repo format. The
words are already transcribed for you in a byte-faithful *spine* file. Your job is
to add MARKDOWN STRUCTURE (the `##` anchors, speaker labels) around those words —
**never to change, add, paraphrase, modernize, or invent words.** The whole point
of this project is exact-source diffs; fabrication is the cardinal sin. When the
spine is unclear, keep it as printed and flag with `<!-- VERIFY -->`.

## The catechism in the spine
For several editions the catechism is BUNDLED on the Confirmation page, so the
spine contains the whole Confirmation service. Use ONLY the catechism portion:
it BEGINS at the catechism title ("A Catechism, that is to say, an Instruction to
be learned…") and its first question "What is your name?", and ENDS at the last
catechism answer — pre-1604 that is the Lord's-Prayer exposition ("…And therefore
I say, Amen. So be it."); 1604-and-later it is the final Sacraments answer
("…and be in charity with all men."). Everything after that (the "So soon as the
children can say…" rubric, the Confirmation versicles "Our help is in the name of
the Lord", the prayers, "The Curate of every parish shall diligently…") is the
**Confirmation office** and belongs to confirmation.md — DO NOT include it.

## Format (match the exemplars: editions/1549 & editions/1552 catechism.md)
- `#` one title line — title-case the source title, keeping this edition's own
  period spelling (e.g. `# A Catechisme, that is to say, an instruccion to bee
  learned of every childe, before he be brought to be confirmed of the Bushop.`).
- `## ` anchors from the menu below, in order, including only the ones this edition
  has. A section's presence/absence is itself the meaningful diff.
- `**Label.**` bold speaker labels using the designation AS PRINTED
  (`**Question.**`, `**Aunswere.**`, `**Answere.**`, `**Answer.**`,
  `**Catechist.**`). A spine line `Question. What is your name?` →
  `**Question.** What is your name?`. Preserve each label's exact spelling as it
  varies within a page.
- The Ten Commandments: number each on its own line as printed (`I.`/`II.`/… or
  the source's own numbering). The Decalogue answer's opening ("The same which God
  spake in the twentieth chapter of Exodus…" 1604/1662; absent 1549) stays on the
  `**Aunswere.**` line, then each commandment on its own line.
- The Creed answer and the Lord's-Prayer answer stay as printed (one paragraph
  each unless the source clearly breaks them); the "Firstly / Secondly / Thirdly"
  lines of "What dost thou chiefly learn in these Articles" go one per line.
- One unit per line; blank line between blocks.

## The anchor menu (EXACT — reuse for every edition)
```
## The Baptismal Covenant   (Name / godparents / the three promises / "Dost thou not think thou art bound")
## The Creed                (Rehearse the Articles of thy Belief + "What dost thou chiefly learn in these Articles")
## The Ten Commandments     (how many / which be they [+ Exodus preamble 1552+] / Decalogue / duty to God / duty to neighbour)
## The Lord's Prayer        ("My good child, know this…" → say the Lord's Prayer + "What desirest thou of God in this Prayer")
## The Sacraments           (1604+ ONLY — "How many Sacraments hath Christ ordained…" / Baptism / Lord's Supper)
```
Pre-1604 editions (1549, 1552) have NO `## The Sacraments`. 1604 and later
(1604, 1662, 1637, 1789, 1892, 1979) DO. 1928 is recast as the "Offices of
Instruction" — see its own note.

## Faithfulness (critical)
- Keep the source's period spelling verbatim (Aunswere, beleve, commaundementes,
  goddes…). Do NOT modernize — normalization happens later, mechanically.
- REMOVE justus/CoE apparatus that is NOT liturgical text: editorial glosses inside
  the text (`gostly [=spiritually]` → `gostly`, `feare [=revere]` → `feare`,
  `appose [=examine]` → `appose`); image captions / scan notes ("Page from the
  1604 Book of Common Prayer…", "A Page from the Confirmation service…"); site
  chrome (Menu, Social, Search, JavaScript notices, cookie banners); standalone
  footnote lines.
- Obvious OCR letter-scannos (`Lard`→`Lord`, `woride`→`worlde`, `goadnes`→`goodnes`)
  may be silently fixed IF unambiguous; if a fix is not obvious, keep as printed and
  flag inline `<!-- VERIFY: source prints 'X'; likely 'Y'; kept as printed; confirm against a page scan -->`.
  Put each VERIFY on its OWN line, doubtful reading FIRST in single quotes.

## Self-check before finishing (REQUIRED)
```
python3 ingest/fidelity_check.py editions/<YEAR>/occasional-offices/catechism.md <spine-path>
```
For EACH flagged word, fix it (a typo you introduced) or justify it (an obvious OCR
fix). Goal: CLEAN, or a short list of justified OCR fixes only.

## Report back (do NOT paste the liturgical text)
Return only: (1) file path written; (2) ordered `##` anchors used; (3) line count;
(4) fidelity_check result + one-line justification for each flagged word;
(5) each `<!-- VERIFY -->` you added, with its reason. Nothing else.
