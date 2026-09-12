# Wave 17 — the 1892 Psalter against the Standard Book scan: guide

The first wave whose witness is a **page scan with no text layer**, and the
first to correct a published transcription at scale. It closes the largest item
in HANDOFF §8.

## The finding

`1892/Psalms.pdf` — the carrier Wave 13 built the 1892 Psalter from — is not
the 1892 text in its spelling. The book prints **show** and **judgment**; the
carrier prints *shew* and *judgement*, which appear on none of the 180 scanned
Psalter pages. It also hyphenates sixteen words the book does not, loses the
mediant in six verses, and misreads seven words (four of which the justus
change log had already disputed; the scan vindicated the change log every
time).

151 corrections: 103 spelling, 34 hyphenation, 7 readings, 7 pointing.

## The method (reusable for any scan without a text layer)

No PDF rasterizer is installed on this machine, and pypdf cannot decode JBIG2.
The pipeline is therefore:

1. `w17_render.py` — split one page out with pypdf, render it with macOS Quick
   Look (`qlmanage -t -s <px>`), which honours the requested size; 2400px for
   locating, 4400px for reading. `crop()` wraps `sips`.
2. `w17_ocr.swift` / `w17_ocrbox.swift` — Vision framework OCR (`swiftc -O`),
   `usesLanguageCorrection = false` so the page's own spelling survives. The
   `ocrbox` variant also returns per-line pixel boxes, which is what makes
   line-level re-reading possible.
3. `w17_scan_ocr.json` — the whole Psalter's page OCR, kept in the repo as the
   witness record.
4. For each candidate: align the cell against the page OCR to find the page,
   score the page's lines by word overlap with the cell verse, crop the best
   line from the 4400px render and **OCR that crop on its own**. Two
   independent reads must agree; anything else is read by eye.

`w17_evidence.json` records, for every correction, the scan page and either the
second machine read (`auto`) or the reading taken by eye (`eye`).

## What the scan is and is not good for

- **Good:** lexical classes counted across the whole book (0 instances of
  "shew" in 180 pages is decisive), and any single word read at 4400px.
- **Not good:** punctuation at page-OCR resolution. `:` and `;` are not
  reliably distinguished, so all seven pointing corrections were read by eye,
  and **no** claim is made about the pointing of verses Wave 13's mediant gate
  did not flag.
- **Undecidable:** a word broken across a line. Psalm 1:3's *water-side* is
  printed "water-" / "side", so the page cannot say; it keeps the carrier's
  hyphen and a VERIFY.

## Rebuild and gates

```bash
python3 ingest/w13_build_1892.py     # applies w17_witness to the parsed carrier
python3 ingest/w17_gates.py          # evidence, attestation, containment, pointing
python3 ingest/w13_fidelity.py       # 0 unattested (scan-supplied words allowed)
python3 ingest/w13_audit.py; python3 ingest/w13_changelog.py   # 55/55
python3 ingest/gen_wave17_provenance.py
python3 tools/verify_index.py --root . --check
```

The containment gate is the important one: it applies these corrections to the
**published** cell and requires the result to equal the new cell exactly, so
nothing else can have changed.

## Lessons

- **Two keyings are not two witnesses.** `1892Standard/psalter.pdf` looked like
  a witness in Wave 16 but shares the carrier's freak errors ("Eqypt"); it took
  page images to settle anything.
- **A transcription can be right about its edition's substance and wrong about
  its orthography.** The change-log gate passed 51/55 in Wave 13, which
  established the PDF really is the 1892 text — and said nothing about *shew*.
- Ask what a source cannot say (a line-break hyphen), and record that.
