# NOTICE — Provenance and copyright of the texts

The software/tooling in this repository is under the MIT `LICENSE`. **The
prayer-book texts under `texts/` are not.** This file records their provenance
and copyright status. See `SOURCES.md` for per-file source URLs and retrieval
dates.

## Summary of copyright status by edition

| Edition | Line | Status | Notes |
|--------:|------|--------|-------|
| 1549 | English | Public domain | First Edwardian book. |
| 1552 | English | Public domain | Second Edwardian book. |
| 1559 | English | Public domain | Elizabethan Settlement. |
| 1604 | English | Public domain | Jacobean / Hampton Court. |
| 1662 | English | Public domain **outside the UK**; **Crown copyright within the UK** | See the 1662 note below. |
| 1637 | Scottish | Public domain | "Laud's Liturgy". |
| 1764 | Scottish | Public domain | Scottish Communion Office. |
| 1929 | Scottish | Public domain | Scottish Book of Common Prayer. |
| 1789 | American | Public domain | First American book; US editions were PD on publication. |
| 1892 | American | Public domain | |
| 1928 | American | Public domain | |
| 1979 | American | Public domain | The 1979 text is explicitly public domain. |

## The 1662 Book of Common Prayer — Crown rights acknowledgment

The 1662 Book of Common Prayer is in the public domain in most of the world.
**In the United Kingdom, rights in the 1662 text are held by the Crown** in
perpetuity by royal prerogative, and are administered by Cambridge University
Press (and, for Bible content, the King's/Queen's Printer). Reproduction within
the UK is by permission of the Crown's patentee.

In acknowledgment of that convention, files transcribing the 1662 edition carry
the acknowledgment string:

```
BCP 1662
```

in their header, and the string is recorded here as required:

**BCP 1662**

## Texts deliberately EXCLUDED (still under active copyright)

The following are **not** included anywhere in this repository, on any branch:

- Church of England *Common Worship* (2000).
- Church of Ireland Book of Common Prayer (2004).
- Modern Canadian, Australian, and other 20th–21st-century non-US revisions.
- The proposed English 1928 "Deposited Book" (included only if a clear
  public-domain source is confirmed; otherwise omitted and noted in
  `SOURCES.md`).

If you believe any text here is included in error, please open an issue.

## Genealogical influence note

The American 1789 Communion Office borrowed substantially from the Scottish
1764 Communion Office (the "Wee Bookie"). Whether or not the git graph models
this as an explicit merge (see the brief §6D), the influence is real and is
recorded here for the historical record.

## History rebuilds

The published branches and tags are build artifacts, regenerated from the
`authoring` source whenever a service is added or deepened. Rebuild log:

- **2026-08-11** — Wave 1: Morning Prayer brought to full Tier-1 across all ten
  daily-office editions.
- **2026-08-12** — Wave 2: Evening Prayer added at full Tier-1 across the same
  ten editions (1764/1929 remain Communion-only).
- **2026-08-12** — Wave 3: The Litany added at full Tier-1 across the same ten
  editions (1764/1929 remain Communion-only). Litany scope is the Litany proper
  through the Grace; appended occasional/state prayers are deferred.
- **2026-08-12** — Wave 4: Holy Communion added at full Tier-1 across **all twelve**
  editions (English 1549–1662, Scottish 1637/1764/1929, American 1789–1979). The
  Scottish 1764 and 1929 opening slices were deepened to the full office. Flagship
  diffs: the 1549→1552 restructuring, the Gloria in Excelsis moving to the end, the
  words of administration, and the Black Rubric (Declaration on Kneeling) appearing
  in 1552, vanishing in 1559, and returning in 1662; the American 1789 rite carries
  the Scottish 1764 eucharistic prayer (`git diff v1764 v1789`).

## A note on transcription

These transcriptions follow public-domain source transcriptions (principally
Charles Wohlers' collection at the Society of Archbishop Justus) cross-checked,
where practical, against public-domain page scans. Transcription involves
editorial judgment; passages whose reading is uncertain are marked inline with
`<!-- VERIFY: ... -->` comments and listed in `SOURCES.md`.
