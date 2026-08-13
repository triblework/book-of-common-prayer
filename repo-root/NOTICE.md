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
- **2026-08-12** — Wave 5: the Christian-initiation offices added at full Tier-1.
  Four services under `occasional-offices/` — Public Baptism of Infants, Private
  Baptism, Baptism of Those of Riper Years, and Confirmation. Public/Private
  Baptism and Confirmation run across the same ten daily-office editions (English
  1549–1662, Scottish 1637, American 1789–1979); 1764/1929 remain Communion-only,
  so they carry none of them. Baptism of Riper Years is a 1662 addition, carried
  into the American line (1789/1892) and folded into a single Holy Baptism office
  by 1928/1979 (so it exists as a separate office only at 1662/1789/1892). Flagship
  diffs: the 1552 baptismal simplification (`git diff v1549 v1552 --
  texts/normalized/occasional-offices/public-baptism.md` — exorcism, chrisom, and
  anointing removed, signing with the cross moved after baptism); the 1604 Hampton
  Court restriction of private baptism to a lawful minister; the 1549→1552
  Confirmation change (the signing with the cross gives way to the "Defend, O Lord"
  imposition of hands). The 1979 offices were reflowed mechanically from the
  public-domain ASCII e-text (source → script → file). The 1549 "Blessing of the
  Font" prayers (an appendix printed after private baptism) are deferred to a later
  occasional-offices pass, as are the bundled Catechism bodies on the 1549/1559/1928
  Confirmation pages (the Catechism is its own wave).
- **2026-08-13** — Wave 6: the pastoral occasional offices added at full Tier-1.
  Five services under `occasional-offices/` — Matrimony, the Visitation of the Sick
  (with the Communion of the Sick), the Burial of the Dead, the Churching of Women,
  and the Commination. Matrimony, Visitation, and Burial run across the ten
  daily-office editions (English 1549–1662, Scottish 1637, American 1789–1979);
  1764/1929 remain Communion-only, so they carry none of them. Churching runs across
  them too — the 1979 book replaces it with "A Thanksgiving for the Birth or Adoption
  of a Child", represented under the same file. The **Commination is an
  English/Scottish office (1549–1662 + 1637) that the American line drops**: it is
  modelled as a clean deletion at 1789 (`git diff v1662 v1789 --
  texts/normalized/occasional-offices/commination.md`), which 1892/1928/1979 inherit;
  the 1979 book has no Commination and its nearest relative (the Ash Wednesday
  liturgy) is deliberately not mapped. Flagship diffs: the Reformation stripping of
  the Burial office in 1552 (`git diff v1549 v1552 --
  texts/normalized/occasional-offices/burial.md` — the 1549 requiem's commendation of
  the soul, prayers for the dead, office of psalms, and Communion of the dead removed,
  leaving the graveside form, with the committal and prayer rewritten to remove prayer
  for the dead); the 1549→1552 Matrimony changes (the "gold and silver" dropped from
  the giving of the ring, the blessing reworded, the apocryphal Tobias/Raphael
  reference removed); and the 1549 Commination's title as "The First Day of Lent,
  commonly called Ash-Wednesday". 1604 changes were derived from the justus 1559
  apparatus (Burial "unto"→"into"; Churching "Priest"→"Minister"; Matrimony,
  Visitation, and Commination unchanged and inherited). 1979 offices were reflowed
  mechanically from the public-domain ASCII e-text `bcpastrl.txt` (source → script →
  file), including the Burial's Rite One (office body) and Rite Two (separate section);
  the American 1892 offices, which justus serves only as text-layer PDFs, were
  extracted with pypdf layout mode. A handful of genuine e-text/print defects are kept
  verbatim and flagged inline (`<!-- VERIFY -->`) — see `SOURCES.md`.

## A note on transcription

These transcriptions follow public-domain source transcriptions (principally
Charles Wohlers' collection at the Society of Archbishop Justus) cross-checked,
where practical, against public-domain page scans. Transcription involves
editorial judgment; passages whose reading is uncertain are marked inline with
`<!-- VERIFY: ... -->` comments and listed in `SOURCES.md`.
