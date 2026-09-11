# Wave 16 — the backlog pass: guide

Wave 16 has no new service family. It works through items HANDOFF §8 recorded,
and it is the first wave whose witnesses are **other justus files** rather than
a scan alone.

## What it changed

| Cell | Change | Script |
|---|---|---|
| 1892 `front-matter/concerning-the-service` | NEW | `w16_build.concerning_1892` |
| 1928 `front-matter/concerning-the-service` | NEW | `w16_build.concerning_1928` |
| 1892 `psalter/selections` | NEW (recorded gap closed) | `w16_build.selections_1892` |
| 1892 `tables/feasts-and-fasts` | rebuilt in 1928's line shape, words unchanged | `w16_build.feasts_1892` |
| 1892 `tables/proper-psalms` | 7 witness corrections; both VERIFYs resolved | `w13_build_extras` + `w16_witness.PROPER_1892` |
| 1928 `tables/proper-psalms` | Palm Sunday 132 → 131; the VERIFY resolved | `w15_witness` (entry withdrawn) |

## The slot ruling (the open backlog question)

`front-matter/concerning-the-service` holds **what a book prints under that
title**. On the English line that is the 1549 Preface, renamed in 1662; on the
American line a rules text, introduced 1892, rewritten 1928, replaced 1979.
Wave 9 had already put 1979's there on that basis, so the question was already
answered by precedent. 1789 prints nothing under the title and keeps its
`absent:`, so `v1789` deletes the file and `v1892` re-creates it.

## Witnesses (and one non-witness)

| Role | File | Notes |
|---|---|---|
| witness | `1892Standard/front_matter.pdf` | the 1892 **Standard Book**, keyed and set page for page after the original. Reads like a proofread text where it differs from the older justus HTML ("fit" for "lit"), but may descend from the same keying — so not counted as independent |
| witness | `1892/Front_Matter_1892.htm` | prints its own copy of the Proper Psalms table, keyed apart from `Psalms_1892.htm` (the Wave-13 carrier, an OCR-grade page) |
| witness | `1928/BCP1936.pdf` | a 1936 printing, scanned; a different setting in lining figures. Pre-1945, so it carries the original lectionary |
| **not** a witness | `1892Standard/psalter.pdf` | shares the 1892 Psalter carrier's own slips ("Eqypt", "stretch our her hands"), so the two are one keying. ~470 word differences, mostly shew/show and judgement/judgment, direction unknown. The 14 Psalter VERIFYs stand |

Raw PDFs are fetched into `scrape-cache/` with a `.pdf` suffix, as in Wave 15.

## Method notes

- **Brace tables.** 1892 prints the Rules as two brace tables (four names } "Sunday
  is" { four values } "Weeks before Easter."). Each row is read across, which
  repeats the words the brace prints once for four rows — the same normalization
  the tables already use, and what 1928 prints as sentences. The gate proves no
  word of the Wave-14 cell was lost and that only those shared words were added.
- **Damaged figures.** Read the glyph, not the number: crop the scan, render the
  line as ASCII at pixel level (`scratchpad/bl/bmp.py` pattern), and compare the
  stroke positions with the same figure elsewhere on the line. Wave 15's "132"
  failed that test; its top serif sits over a centred stem (old-style 1), while
  the old-style 2 of "24" hooks right.
- **Two keyings are not two witnesses** unless they disagree somewhere. Shared
  freak errors ("Eqypt") prove a common ancestor.

## Rebuild and gates

```bash
python3 ingest/w16_build.py          # the four 1892/1928 cells
python3 ingest/w13_build_extras.py   # 1892 proper-psalms (witness corrections)
python3 ingest/w15_psalms.py         # 1928 proper-psalms (132 withdrawn)
python3 ingest/w16_editions.py       # presence (idempotent)
python3 ingest/gen_wave16_provenance.py   # provenance (idempotent)
python3 ingest/w16_gates.py          # fabrication, loss, structure, sensitivity
python3 ingest/w15_fidelity.py; python3 ingest/w15_audit.py
python3 ingest/w14_fidelity.py; python3 ingest/w14_audit.py
python3 tools/verify_index.py --root . --check
```

`w16_gates.py` compares the rebuilt 1892 Tables and Rules against the Wave-14
cell at commit `e50503f4`, so that check is pinned to authoring history.
