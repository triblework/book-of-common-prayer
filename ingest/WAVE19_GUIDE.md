# Wave 19 — the 1979 text against the publisher's own file: guide

The first **exact** collation in this repository. Waves 17 and 18 read page
images, so what they could prove was bounded by OCR; here both sides are text,
and the Psalter was compared verse by verse, word for word.

## The witness

Church Publishing Incorporated's own PDF of the 1979 Book of Common Prayer,
from the Episcopal Church, served by Wikimedia Commons as
`File:Book of common prayer (TEC, 1979).pdf` — 1001 pages, 4,911,934 bytes,
sha256 `d4552eb3…`, producer `Acrobat PDFWriter 3.0f1r8 for Power Macintosh`.
About 5 KB a page: a text PDF, not page images. The licence question is
answered on the file page — the US Book of Common Prayer has never been under
copyright, which the publisher states in its own copyright brochure, and
`NOTICE.md` already recorded 1979 as public domain.

The carrier for every 1979 cell is justus's 1993 ASCII e-text. A publisher's
typesetting and a volunteer keying are witnesses of **different classes**, so
R6 ("two keyings are not two witnesses") is satisfied and the publisher's file
is the book.

## What the witness cannot say

- **Small capitals.** The book prints the divine Name as LORD in small
  capitals; the text layer renders that "Lord". No letter-case is taken from
  it.
- **The pointing asterisk.** The extractor drops it in ten verses (33:16,
  34:3, 40:16, 71:21, 83:16, 83:17, 105:21, 105:22, 107:28) and turns it into
  a dash in a eleventh (144:15), while every neighbouring verse keeps it. That
  is extraction noise, not the book losing its pointing, so **no pointing is
  changed on this witness**.
- Four verses (40:11, 65:11, 119:166, 69:18) carry a stray "I" or quotation
  mark from the same cause.

Those fifteen verses are named in `w19_gates.py`, and the gate requires that
the corrected Psalter differ from the book **in exactly those fifteen places
and nowhere else**.

## The pipeline

`w19_witness_text.py` extracts the text page by page with pypdf (deterministic,
so the record is not committed — rebuild it from the cached PDF) and offers
`find()`. `w19_psalter.py` parses the book's Psalter out of pages 585–808 using
its own line structure:

```
The Psalter / Book One / First Day: Morning Prayer   <- furniture, dropped
1   Beatus vir qui non abiit                         <- psalm + incipit
1 Happy are they who have not walked in the counsel  <- verse, wrapping
the wicked, *                                           over several lines
Psalm 1   585                                        <- running foot
```

Four things made that harder than it looks, and each is handled explicitly: a
psalm's number and incipit are usually one line but sometimes two ("18" /
"Part 1 Diligam te, Domine."); long psalms are printed in parts
("Psalm 18: Part II   Et retribuet mihi") whose verse numbers simply continue;
Psalm 119's 22 portions are headings only — the book numbers its verses 1–176
straight through; and the extractor occasionally loses the space after a verse
number ("9O Lord, give victory") or merges a running head into the line below.
After those, 2,507 of 2,507 verses parse.

## What it found

| | |
|---|---|
| verses whose words differ | **24**, the keying wrong in every one |
| Latin incipits corrected | **17** (nine of them Wave 13's flagged truncations) |
| Psalm 119 portion headings | **3** (the æ ligature) |
| the keying's end-of-file marker published as psalm text | 1 |
| dropouts and typos in six other cells | 7 |
| 1979 inline flags | 143 → 127; none left in the Psalter |

`w19_survey.py` then measured the rest: outside the lectionary tables, 94% of
paragraphs are verbatim in the book (propers 89%, daily office 93%, holy
communion 94%, occasional offices 96%, ordinal 97%, prayers 98%). The ~110
that are not are the next pass's candidates. The tables match at 1.5% because
this repository renders them as long-form rows and the book prints them as
tables — that needs a different comparison, not a closer reading.

## Rebuild and gates

```bash
python3 ingest/w13_build_1979.py     # applies w19_witness to the parsed e-text
python3 ingest/w19_cells.py          # the six structured cells (idempotent)
python3 ingest/w19_evidence.py       # every reading looked up in the book
python3 ingest/w19_gates.py          # evidence, collation residue, containment
python3 ingest/w13_fidelity.py       # 0 unattested (book-supplied words allowed)
python3 ingest/w13_audit.py
python3 ingest/gen_wave19_provenance.py
python3 tools/verify_index.py --root . --check
```

## Lessons

- **An exact witness changes what a gate can assert.** With OCR the honest
  claim was "these readings are right"; here it is "the cell and the book
  differ in exactly fifteen places, and every one is a known artifact of the
  extractor". Prefer a witness you can diff.
- **Measure what a keying cost before trusting it.** The 1993 e-text is good —
  24 wrong verses in 2,507 — but it silently published its own end-of-file
  marker as scripture, and swallowed two whole passages elsewhere.
- **The survey is part of the wave.** Knowing that 94% of the remaining text
  matches, and which 6% does not, is what makes the next wave plannable.
