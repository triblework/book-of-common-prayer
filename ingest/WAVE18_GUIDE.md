# Wave 18 — the 1662 text against the Annexed Book: guide

The first wave to read the 1662 node against a 1662 authority. It closes eight
open flags, corrects two verses of the Psalter, deletes two lines of website
chrome that had been published as liturgy, and states plainly what this witness
can and cannot settle.

## The witness

*The Book of Common Prayer ... from the original manuscript attached to the Act
of Uniformity of 1662*, Her Majesty's Printing Office, September 1892 —
Wikimedia Commons, `File:The_Book_of_Common_Prayer.pdf`, PD-US, 577 page images
(26.4 MB, sha256 `72f4771c…`). This is the **Annexed Book**: the manuscript the
Convocations subscribed on 20 December 1661 and the legal standard of the 1662
text, set in type "verbatim et literatim" and then compared, word by word and
stop by stop, with the photographs from which the 1891 House of Lords facsimile
was made.

Three texts, not two, are in play:

| | what it is | orthography |
|---|---|---|
| carrier | the Church of England's currently authorized 1662 text | modernized |
| witness | the Annexed Book (this reproduction) | the MS's own, erratic |
| neither | the printed Sealed Books of 1662 | a third thing again |

The witness's own preface says the earliest printed copies "are found to differ
considerably from that original standard in various details of orthography and
punctuation", and concludes that the MS was "intended to be a record of the
language only ... and not to be a standard of orthography". **So this wave
collates substance and structure and nothing else.** The witness reads
`vngodly`, `ioy`, `shew`, `soveraign`; Psalm 90:1 opens "O Lord thou hast been
our refuge" where the carrier has "Lord, thou hast been our refuge". Those are
differences between printings, not errors, and not one of them was imported.

## The pipeline (Wave 17's, pointed at a new book)

`w18_render.py` (pypdf split → Quick Look raster) → `bin/w17_ocr` /
`bin/w17_ocrbox` (Vision, `usesLanguageCorrection = false`) → `w18_scan.py`
writes the page record. The whole book is read at 2400px
(`w18_scan_ocr.json`, 575 pages, 17,496 lines); the Psalter is read again at
4400px (`w18_psalter_ocr.json`, 163 pages, 5,587 lines) because at 2400 Vision
drops about one line in six on these dense pages, which is fatal to a
verse-by-verse alignment. `w18_read.py` supplies the second read: it finds the
line, crops it out of a 4400px render and OCRs the crop alone. Where Vision
merges a whole paragraph into one garbled block — it does this on the pages
that matter most — an item carries an explicit `box` and the block is cropped
by coordinates instead.

## The Psalter alignment

`w18_psalter.py` aligns 2,508 carrier verses to the scan on a **skeleton** of
each word (u=v, i=j=y, doubles collapsed, final -e dropped), never on its
letters: the skeleton exists only to find the place on the page. Unique 4-gram
anchors common to both streams (17,773 of them) are chained by longest
increasing subsequence, and every verse is placed between its neighbouring
anchors. A greedy forward scan was tried first and derailed inside Psalm 2 —
one dropped OCR line and it never recovered.

`w18_mediant.py` then asks one question per verse: does the witness print a
mark on the word the carrier's mediant follows?

```
verses 2508: agree 1561, unread 330, absent 2, span too loose 615
```

`absent` is the only finding: **two verses in the whole Psalter carry no
mediant in the carrier, and the book points both.** `unread` is OCR damage, not
evidence of absence — `--sample 30` re-read thirty of them line by line at
4400px and found the mediant legible, and in the same place, in 25.

## What changed

**Two corrections** (`w18_witness.POINTING`), each read twice by machine and
once by eye:

| verse | carrier | the Annexed Book |
|---|---|---|
| 2:12 | `…from the right way, if his wrath…` | `…from the [right] way : if his wrath…` (p. 346) |
| 68:1 | `…be scattered let them also…` | `…be scattered : let them also…` (p. 413) |

After them every one of the 2,508 verses carries exactly one mediant.

**Eight flags closed.** Psalm 89:50 is confirmed as printed (the doxology stands
inside verse 50, no verse 51, p. 443). The five monarch flags are answered:
the book prays for **King Charles** in Morning Prayer (p. 70), Evening Prayer
(p. 80), the Litany (p. 86), the Ordinal's litany (p. 526) and the prayer for
the Church Militant (p. 254), so the name the source prints is period-correct.
The psalm-cento flag at sea is answered: the book labels the one psalm it uses
("Confitemini Domino. Psal. 107.", p. 513) and prints no label over the
composite hymns (p. 517).

**Two lines of website chrome deleted.** `prayers-at-sea.md` had published
"To experience the best that the Church of England website has to offer, you
need to enable JavaScript…" and "Popular search items" as text. The Wave-8
structuring rule already said to drop site furniture; nothing enforced it.
`w18_gates.py` now refuses it corpus-wide.

## What did NOT change, and why

**The royal names.** The Annexed Book names the King and leaves every other
royal name a BLANK — in Morning Prayer and Evening Prayer the title itself
breaks off at "A Prayer for" and the prayer at "we humbly beseech thee to
bless"; in the Litany and the Ordinal the petition breaks off after "bless and
preserve". The carrier fills those blanks with the living Royal Family (Queen
Camilla, William Prince of Wales, the Princess of Wales). The blank is a real
reading, but it does not say what a 1662 cell should print, and printing a
blank is not what the source prints either. The four flags now record the
finding; **the choice is the maintainer's.**

**The communion admission rubric.** The rubric the carrier prints — an account
to the Ordinary, seven days, an opportunity for interview — is not in the 1662
text at all; the Annexed Book prints the "open and notorious evil liver" rubric
of 1549–1604 (p. 246). Substituting it would mean importing the manuscript's
orthography into a modernized cell. Recorded, not done.

**"Foreasmuch"** (Publick Baptism). The MS reads "Forasmuch" (pp. 277, 283) —
but a witness that disclaims its own orthography cannot settle a spelling. The
flag now records the check instead of asking for a scan.

**"her Majesty's Navy"** (Prayers at Sea). The book reads "his Majesties Navy"
(p. 508). The carrier's reading is the same reign-dependency as the royal
names, one reign further out of date, in a file that prays for "King CHARLES".
Newly flagged; same ruling pending.

## Rebuild and gates

```bash
python3 ingest/w13_build.py          # applies w18_witness to the parsed carrier
python3 ingest/w18_cells.py          # the seven structured cells (idempotent)
python3 ingest/w18_evidence.py       # re-reads every item off the scan
python3 ingest/w18_gates.py          # evidence, containment, chrome, pointing
python3 ingest/w13_fidelity.py       # 0 unattested
python3 ingest/w13_audit.py          # 0 anomalies
python3 ingest/gen_wave18_provenance.py
python3 tools/verify_index.py --root . --check
```

The containment gate is again the important one, in two halves: the published
psalter cells plus exactly these two corrections must equal the new cells, and
the published structured cells minus the chrome must have exactly the new
cells' words. Nothing else can have moved.

## Lessons

- **A witness can be authoritative about words and worthless about spelling**,
  and say so itself. Read the preface before collating.
- **Silence can be the reading.** The blank in the Prayer for the Royal Family
  is evidence; it is just not an instruction.
- **Gates enforce what guides only ask for.** The site chrome sat in a
  published cell for ten waves because the rule against it lived in a
  structuring guide and in nothing executable.
- A source that is down has to be waited out: justus.anglican.org was
  unreachable throughout this wave, which is why the 1928 Psalter (whose
  witness is the 1952 facsimile on that host) is still untouched.
