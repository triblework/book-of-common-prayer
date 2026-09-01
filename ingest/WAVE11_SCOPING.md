# Wave 11 — Prayers and Thanksgivings: source survey + scoping options

> ## DECISION — LOCKED (maintainer ruling, 2026-09-01)
>
> **Placement: option (b).** Own family `prayers-and-thanksgivings/<slug>.md`,
> one file per prayer, for **every** edition that carries the block — including
> 1552–1637, where the book prints it inline after the Litany suffrages. That
> inline placement is recorded as a **book-order note in NOTICE.md and in the
> per-edition `provenance.yaml` records**, not as a text diff (the Wave-9
> `of-ceremonies` precedent).
>
> **Scope boundary: the following four are EXCLUDED from this wave** and are
> each their own (small) future wave, not folded in here:
> 1. 1662 *Forms of Prayer to be used at Sea* (CoE slug `prayers-be-used-sea`)
> 2. the 1892/1928 *Penitential Office*
> 3. *Family Prayer* (1789 `Family_Prayer_1789.htm`, 1928 `Family_Prayer.htm`)
> 4. the 1789 *Prayer and Thanksgiving to Almighty God*
>    (`Prayer&Thanksgiving_1789.htm`)
>
> These are adjacent on the same source pages and MUST be sliced off
> deliberately — see §1 "Other findings".
>
> Do not re-litigate either half of this ruling; it is the durable record.


Authoring-only. Written before any build, to record what the sources actually
say and to frame the placement decision. **Nothing here is transcribed text —
this is an inventory and a structural argument.**

## 1. Presence, as established from the sources' own apparatus

The brief's starting premise was that 1559 and 1637 both carry state prayers +
occasional prayers + thanksgivings. **The 1559 source's own apparatus
contradicts the thanksgivings half of that**, and the correction matters because
it moves a whole sub-block from 1559 to 1604.

`ingest/spines-w9/1559_litany.md` carries these editorial notes, which are the
things that license the deltas (never inference):

- `The following Thanksgivings were added in 1604:` — the five thanksgivings
  (Rain, fair Weather, Plenty, peace and victory, Deliverance from the Plague,
  + `Or this`) are **1604**, not 1559.
- `[prayer added 1604]` in the 1559 row of the page's own "Variations in the
  State Prayers" table, under the *Prayer for the Royal Family* column — so the
  royal-family prayer is **1604**, not 1559.
- `* Replaced by a prayer for the King in 1604 (see below)` — the 1559 *Prayer
  for the Queenes Majesty* becomes the King's prayer at 1604.
- `This prayer added in 1604 (see below for variations).` — sits immediately
  after the `O God, whose nature and propertie…` block. **Attribution needs
  confirming against the page markup** before use (the spine has lost the
  visual association of the note to its referent). VERIFY at build time.

The 1637 book, which follows 1604, carries the full set — independent
corroboration that the thanksgivings entered at 1604.

### Per-edition inventory (confirmed against the four spines + fetched pages)

| Edition | Block contents |
|---|---|
| **1549** | **Nothing.** Litany ends at the Chrysostom collect. Confirmed at `1549_litany.md`. |
| **1552** | Occasional prayers only: Rain, fair Weather, Dearth and Famine (+ a second form, `Or thus`), War, Plague. No state prayers, no Grace, no thanksgivings. Ends `And the Letany shall ever ende with thys Collecte folowyng:` |
| **1559** | State prayer for the Queen's Majesty; Clergy; Chrysostom; the Grace (`ii. Corin. xiii.`); then the 5 occasional prayers. **No** royal-family prayer, **no** thanksgivings. Loses 1552's second dearth form. |
| **1604** | Adds the Royal Family prayer, the 5(+1) Thanksgivings, and (pending the VERIFY above) `O God, whose nature and property…`; Queen→King wording. |
| **1637** | Full set: King; Queen/Prince Charles/royal progeny; holy Clergie; **Ember weeks**; Chrysostom; Grace; 5 occasional; concluding collect; 6 thanksgivings. |
| **1662** | Own section, `prayers-and-thanksgivings`. Adds the **High Court of Parliament**, the two congregation rubrics, **A General Thanksgiving**, **For restoring Publick Peace at Home**. Litany already ends `Here endeth the Litany.` |
| **1789 / 1892 / 1928** | Own section on justus. 1892 notably adds Unity of God's People, Missions, Fruitful Seasons, a Sick Child, a Person under Affliction, Recovery from Sickness, Safe Return from Sea. |
| **1979** | Own section: **70 numbered Prayers + 11 Thanksgivings**, in 7 subsections (World, Church, National Life, Social Order, Natural Order, Family and Personal Life, Other Prayers) + Thanksgivings. |
| **1764 / 1929** | **Absent** — the Communion-only Scottish line (1764 already carries `the-litany/litany` in `absent:`; 1929 inherits). |

### Other findings to carry into the build
- **Possible 1637 rain/dearth swap.** 1552 and 1559 print `which by thy Sonne
  Jesus Christe hast promised…` under *For Rain* and `whose gift it is that the
  raine doth fall…` under *Dearth and Famine*; the 1637 page prints them the
  other way round. Genuine revision or a justus transposition — **VERIFY against
  a 1637 scan; do not smooth it away either direction.**
- 1662 prints Dearth and Famine in **two** forms, `(i)` and `(ii)`.
- The 1892/1928 justus pages **bundle adjacent material** that is not this
  section (a Penitential Office; Family Prayer; "A Prayer and Thanksgiving to
  Almighty God" is a separate 1789 page entirely). Slice deliberately.

## 2. Sources confirmed

| Edition | Source | Status |
|---|---|---|
| 1552 / 1559 / 1637 | `ingest/spines-w9/{1552,1559,1637}_litany.md` | already in repo |
| 1549 | `ingest/spines-w9/1549_litany.md` | confirms absence |
| 1604 | derived from the 1559 page's apparatus (the notes above) | in repo |
| 1662 | CoE `…/book-common-prayer/prayers-and-thanksgivings` | fetched OK |
| 1789 | `http://justus…/1789/Prayers&Thanks_1789.htm` | fetched OK |
| 1892 | `http://justus…/1892/Pray&Thanks_1892.htm` | fetched OK |
| 1928 | `http://justus…/1928/Pray&Thanks.htm` | fetched OK |
| 1979 | cached `bcpprayr.txt` (`<page N>` / `<Section>` markers, numbered TOC) | cached |

justus over **http** throughout (the https vhost 404s); CoE over https.

## 3. The placement options

### (a) Inline, under the existing `## The Prayers` anchor of `the-litany/litany.md`
Matches 1552–1637, where the block genuinely is part of the Litany.
**Against:** 1662 and the whole American line moved it *out* — their Litany ends
`Here endeth the Litany.` and 1928/1979 print an explicit cross-reference to the
separate section. Putting it back inside their Litany file misstates their
structure. It also buries every per-prayer diff in one file, and would drop
1979's 81 units into `litany.md`.

### (b) Own family, `prayers-and-thanksgivings/<slug>.md`, one file per prayer
**Recommended.** Gives per-prayer lineage and presence tracking — which is this
repo's whole signal — and matches 1662+ exactly.
**Cost, honestly:** it lifts the block out of the 1552–1637 Litany, where the
book really does print it inline. That cost is a *book-order* fact, and the repo
already has a precedent for recording exactly that: Wave 9's `of-ceremonies`
moved from end-of-book (1549) to front (1552) and was recorded as **a note in
NOTICE.md, not a text diff**. Same treatment here. The 1552 Litany also keeps
its own printed closing rubric, so nothing is invented to paper over the seam.

### (c) Hybrid — inline before 1662, own family from 1662
Superficially "matches each book", but it is the **worst** option for this repo,
and not a close call. The builder aligns files **by path**. A prayer continuously
present from 1552 to 1928 (For Rain, For fair Weather, Dearth, War, Plague) would
live at `the-litany/litany.md` through 1637 and at
`prayers-and-thanksgivings/for-rain.md` from 1662. `git diff v1637 v1662` would
then render a mass **deletion** from the Litany and a mass **insertion** of new
files — manufacturing a textual discontinuity at exactly the point where the text
in fact continued. That is the "a missing section reads as *this edition didn't
have it*" failure `AUDIT_METHOD.md` exists to prevent, except deliberately
built in.

## 4. Recommendation — ACCEPTED (see the locked decision at the top)

**(b)**, with the 1552–1637 inline placement recorded in NOTICE.md and in each
affected `provenance.yaml` record.

Reasons, in order:
1. It is the only option under which the block's *growth* — the thing the brief
   correctly identifies as the historical signal — reads as clean per-prayer
   inserts: 1552 five files appear, 1559 adds state prayers, **1604 adds the
   thanksgivings**, 1662 adds Parliament and the General Thanksgiving, 1892 adds
   the pastoral prayers, 1979 adds seventy.
2. Presence/absence per prayer becomes machine-checkable in `editions.yaml`,
   so `w11_audit.py` can run the same anchor-set loss gate as Wave 10.
3. It matches the structure of the majority of editions carrying the block
   (1662, 1789, 1892, 1928, 1979 = 5 of the 9), and the cost falls on a
   *placement* fact that the repo already knows how to record losslessly.
4. Scale is proven: ~110–120 files is the same order as Wave 10's 106 occasions.

### Scope boundary to rule on
Recommend **excluding** as separate book divisions, not part of "Prayers and
Thanksgivings upon several Occasions": the 1662 *Forms of Prayer to be used at
Sea* (`prayers-be-used-sea`), the 1892/1928 *Penitential Office*, *Family
Prayer*, and the 1789 *Prayer and Thanksgiving to Almighty God*. Each is its own
section and would be its own (small) wave.
