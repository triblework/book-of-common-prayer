# Wave 21 — the 1928 Psalter against the original printing: guide

The last American psalter unread against a page scan, and the first wave to
read one cell against **two** scans of the same book and say what each may
settle. Three flags closed, seventeen corrections, ten printing differences
recorded. Rulings **R19** and **R20** in `RULINGS.md`.

## The witnesses (read their front matter first, R7)

| | `1928/BCP1929.pdf` | `1928Standard/1952std.pdf` |
|---|---|---|
| what it is | the "Cambridge Edition" (Old Corner Book Store, Boston), certified 1929 by the Custodian against a certified copy of the Standard Book: the **original printing** | Seabury Press 1952, a Meriden Gravure facsimile of Updike's Standard Book, certified Sept. 1952 as conforming to the Standard Book **"as amended by subsequent actions of General Conventions"** |
| size, sha256 | 42,365,481 B, `dd2367fe…d41ec0` | 68,953,844 B, `2197f453…289768` |
| pages | 319 grey JPX spreads, two book pages each | 336 (p. 1 is justus's typed note), colour JPX spreads |
| pagination | original: Calendar at xxix, Articles at 591 | 1945 lectionary (Calendar at xlvi); 1936 layout after the Psalter |
| Psalter pp. 345–525 | scans 192R–282R; book = 2·scan − 40 (+1 on the right) | scans 203R–293R; book = 2·scan − 62 (+1) |
| role | **the witness** (v1928 = the original printing, Wave 15) | second witness within limits (R19) |

They are two different typesettings with the same Psalter pagination, so a
compound one breaks at a line end is often whole in the other — which is the
facsimile's real value. `bcp1928std.pdf` is Wohlers's 2005 InDesign re-setting
in Kis BT: a keying, not a witness (R6).

**What the certificate decided.** "As amended by subsequent actions" made the
facsimile a later state of the text; on the page before the Psalter it prints
Good Friday 22:1–19 where the original prints 1–9 (what `v1928` carries). It
cannot by itself say what 1928 printed.

## The pipeline (`ingest/w21_*`)

```
w21_render.py        pypdf split -> Quick Look, or the native sips route; SIZE-CHECKED crops
w21_scan.py          gutter from the OCR line boxes; each book page cropped and OCR'd alone;
                     observations merged into printed lines by vertical centre
                     -> w21_1929_ocr.json, w21_1952_ocr.json (4400px, 181 pages each)
w21_ocrstats.py      lines per page; every 0-line page checked by eye (none in the Psalter)
w21_psalter.py       skeleton 4-gram anchors + LIS, word diff between anchors (Wave 18's method)
w21_mediant.py       agree / unread / absent per verse, per scan
w21_lexical.py       cell words no scan attests; scan words with no cell partner; a word sweep
w21_printdiff.py     where the two PRINTINGS differ
w21_reads.py         the second machine read: the line cropped and OCR'd on its own
w21_eyecrop.py       crops for the eye; w21_eye.txt is the eye record
w21_evidence.py      joins the eye record to the machine reads -> w21_evidence.json
w21_witness.py       the keyed corrections (applied by w13_build.py), the printing
                     disagreements, the flags opened; a POLICY switch records the ruling
w21_gates.py         evidence, attestation, containment (vs 710f635b by SHA), pointing, flags
```

Regeneration from a clean checkout is spelled out in the Phase 2 report's
§2.5 (binaries, fetches with sha256, renders, OCR, alignment, evidence,
build, gates); the eye record is the one thing not machine-regenerable.

## Counts

- Page OCR: 6,369 lines (1929) and 6,171 (1952); word recall against the cells
  98.2% / 97.3%. No Psalter page read to 0 lines.
- Verses placed: 2,477 / 2,443 of 2,508; the rest are drop-capital openings,
  cropped whole and read.
- Mediants: all 2,508 resolved on each scan. The 1929 printing lacks three
  (18:10, 73:20, 123:2) that the facsimile and the cell have; the three
  flagged verses are pointed in both.
- 323 eye readings on 268 places.
- **17 corrections**: 3 pointing, 1 reading, 2 spacing, 10 hyphenation, 1
  structure. 3 flags closed, 7 opened.

## What the scans can and cannot say

- **Words**: decisive at 4400px, read twice or by eye.
- **The mediant**: decisive by eye. The 1929 star is large and Vision reads it
  every time; the 1952 raised asterisk is often read as `"`.
- **Ordinary punctuation**: not collated — page OCR cannot tell `:` from `;`
  (the one comma recorded, 37:20, was found incidentally by eye).
- **A compound broken at a line end** is undecidable on that page; a second
  printing set differently often decides it (four settled here); five remain
  broken in both and are flagged.
- **The original printing is not error-free**: four misprints and three dropped
  asterisks in the Psalter alone. Where it disagrees with the Standard Book it
  is a witness to itself only (R19).
- **The keyed carrier agrees with the Standard Book in all ten disagreements**,
  so it was keyed from a Standard-conformant printing, not from BCP1929.

## Lessons

1. **`sips` crops fail silently.** `sips -c 3392 2200 --cropOffset 0 0 …`
   ignores the offset and crops about the centre; a crop reaching the bottom
   edge (`--cropOffset 1 0`) came back uncropped at full size. `w21_render.crop_at`
   checks every output's size and retries one pixel in. `w15_src.scan_crop`,
   `w18_render.crop` and `w18_read` (which clamps both offsets to 0 near a
   corner) are exposed. Earlier eye reads were of whatever the crop showed, so a
   wrong crop would have shown the wrong line rather than a wrong reading — but
   check the size of every crop from now on.
2. **OCR each book page of a spread on its own**: Vision merges lines across
   the gutter.
3. **Drop-capital openings are where page OCR fails**; crop the whole verse.
4. **A second printing of the same standard text is worth having for its line
   breaks, not its authority.**
5. **Read the certificate.**
6. **The shared fidelity gate needs an exemption whenever a scan supplies
   letters the carrier lacks** (here, the halves of hyphenated compounds):
   `w13_fidelity.py` subtracts `w21_witness.introduced_tokens()`, and
   `w21_gates` attests each one against the scans' own OCR.
