# Wave 8 — the Ordinal: confirmed source map + decisions

New service family `ordinal/` with FOUR files (siblings):
- `ordinal/preface.md`            — "The Preface" to the Ordinal ("It is evident unto all men…")
- `ordinal/ordering-deacons.md`   — The Form and Manner of Making of Deacons
- `ordinal/ordering-priests.md`   — The Form and Manner of Ordering of Priests
- `ordinal/consecration-bishops.md` — The Form of Consecrating of an Archbishop or Bishop

## DECISION 1 — the 1549 cell: represent at v1549 from the standalone 1550 Ordinal
The Ordinal was published **separately in 1550** and only bound into the book from
1552; the 1549 book proper did NOT contain it (spec §6.1 n.2). We represent it at
the **v1549 node**, sourced from the 1550 Ordinal, because:
  (a) it preserves the flagship **1550→1552** revision as `git diff v1549 v1552`
      (removal of the porrection / delivery of instruments; vesture stripped);
  (b) justus itself dates the base text to 1550 and files the pages under `/1549/`
      (`Deacons_1549.htm` etc., titled "The Ordinal from the 1549, 1552 and 1559
      Books of Common Prayer", with the 1550 title page);
  (c) representing it first at 1552 would discard the 1550 witness entirely.
Recorded in NOTICE.md. The v1549 Ordinal is the separately-published 1550 Ordinal.

## DECISION 2 — the Scottish line has NO Ordinal this pass (all absent)
The spec matrix tentatively marks 1637 ✓ and 1929 ✓, but the actual sources say
otherwise:
  - The **1637** Scottish Prayer Book proper (justus `Scotland/BCP_1637.htm`)
    contains **no** Ordinal — Laud's Liturgy omitted the ordination services
    (Scotland used a separate ordination form). Its index lists no ordinal.
  - The only Scottish Ordinal justus serves (`Scotland/Scot_Ordinal.htm`) is the
    **1929** book's ("The Scottish Book of Common Prayer (1929): The Ordinal").
  - This repo's Scottish line is Communion-only after 1637 (1764/1929), exactly as
    MP/EP/Litany/Catechism etc. are.
So: 1637 lists all four `ordinal/*` services in `absent:` (it drops the Ordinal its
1604 parent carries — a historically-accurate clean deletion diff), and 1764/1929
inherit that absence. Do NOT invent a Scottish Ordinal this pass. Recorded in
NOTICE/SOURCES.

## DECISION 3 — the Ordinal Preface is one shared file, printed once
The 1550 Ordinal prints "The Preface" once (before the Deacons form); it is the
preface to the whole Ordinal. Modeled as `ordinal/preface.md`, present wherever the
Ordinal is. Identical across 1549/1552/1559 (the synoptic page shows no variant
marks in the preface) → author once at 1549; 1552/1559 inherit reviewed-unchanged.
The **1662 preface adds the anti-Puritan episcopal-succession paragraph** ("no man
shall be accounted… except… or hath had formerly Episcopal Consecration or
Ordination") — a clean `git diff v1559 v1662` on the preface. American prefaces
differ again (drop the Church-of-England / sovereign framing).

## DECISION 4 — colophons are out of scope
The synoptic Bishops page ends with printer colophons (Grafton 1549 / Whitchurch
1552 / 1559 / Barker 1634). These are book-production imprints, not liturgical
service text — DROPPED (as scan furniture is dropped elsewhere). Noted in SOURCES.

## Presence (corrected against sources; encode in editions.yaml)
Present at: English **1549 1552 1559 1604 1662**, American **1789 1892 1928 1979**.
Absent at: Scottish **1637** (all four in `absent:`), inherited-absent 1764/1929.
  → add the four `ordinal/*` ids to the `present:` of the nine ✓ editions.
  → add the four `ordinal/*` ids to 1637 `absent:`.

## THE FLAGSHIP DIFFS (confirmed against the synoptic pages)
1. **1549(=1550) → 1552 — the Edwardian revision** (`git diff v1549 v1552`):
   - PRIESTS: 1550 delivers "the Bible in the one hande, and the **Chalice or cuppe
     with the breade**, in the other hande" → 1552 "the Bible **in his hande**" only
     (the porrection / delivery of instruments removed). The "playne Albe" vesture
     rubric is 1550-only.
   - BISHOPS: 1550 lays "**the Bible upon hys necke**" AND gives "**the pastorall
     staffe**" (two acts) → 1552 delivers "**the Bible**" only, combined text (staff
     dropped). Surplice/cope/pastoral-staves vesture is 1550-only.
   - DEACONS: 1552 adds "[with the prayers]" to the Litany rubric, expands the
     Litany petitions ([al], [other], lightening[es], tempest[es]), adds duty-of-a-
     deacon clauses; versicle/response reflow.
   - Assorted: "The Lord be with you / And with thy spirite" dropped 1552 (priests &
     bishops); the Bishops "at the last daye" retained (dropped early 1600s → 1604).
2. **1552 → 1559 — the Elizabethan settlement** (`git diff v1552 v1559`):
   - The anti-papal Litany clause "from the tyrannye of the Bysshop of Rome, and al
     hys detestable enormities" is REMOVED in 1559 (mirrors the Litany, Wave 3).
   - The **Oath of the King's Supremacy** (1550/52) is replaced by the **Oath of the
     Queen's Sovereignty** (1559) — different wording ("supreme Governour", "no
     foreign prince, person, prelate…"). Sovereign petition inserted ("EDWARD the
     sixth", changed for Elizabeth/James/Charles as marked).
3. **1559 → 1604 — Jacobean** (`git diff v1559 v1604`, DERIVED, small):
   - The Oath of the Queen's Sovereignty → **King's** (Queen→King, her→his); the
     apparatus explicitly notes "Kings supremacie in 1604" and the bracketed
     [Kings]/[his] readings ARE the 1604 form. Bishops: "at the last daye" → the
     "daye" is dropped early 1600s (→ 1604). Otherwise 1604 = 1559.
4. **1604 → 1662 — the Restoration strengthening** (`git diff v1604 v1662`):
   - The forms of ordination gain the explicit **order-naming** (anti-Puritan /
     anti-Rome): "Receive the Holy Ghost **for the office and work of a Priest** in
     the Church of God…", "…**for the office and work of a Bishop**…". (The 1550-1604
     priest form is just "Receive the holy goste, whose synnes thou doest forgeve…";
     the bishop form "Take the holy gost, and remember that thou stirre up the grace
     of god…".)
   - The **Preface** gains the episcopal-succession paragraph (see Decision 3).
5. **1662 → 1789 — the American recasting** (`git diff v1662 v1789`):
   - Drops the Oath of the King's Supremacy; the sovereign/Church-of-England framing
     becomes "the civil authority" / declaration of conformity. Confirm per source.

## Sources per edition (all confirmed to exist)
### English 1549/1552/1559 — ONE synoptic justus page per order (hand-author all 3)
- Deacons: `1549/Deacons_1549.htm`   spine → ingest/spines-w8/deacons_eng.md
- Priests: `1549/Priests_1549.htm`   spine → ingest/spines-w8/priests_eng.md
- Bishops: `1549/Bishops_1549.htm`   spine → ingest/spines-w8/bishops_eng.md
- Preface: at the top of the Deacons page (same spine).
The single page carries the 1550 base + `[…]* added 1552/1559` inline inserts +
`1550,52:` / `1559:` branch markers + inline editorial notes. Hand-parse into three
faithful editions per order. (justus HTTP only — https 404s. WebFetch fails; use the
scrape cache via ingest/hc_clean.py.)
### English 1604 — DERIVE from 1559 (oath sovereign King/his; bishops "daye" drop)
### English 1662 — CoE website (HTTPS works)
- Preface: `book-common-prayer/preface`
- Deacons: `book-common-prayer/ordaining-and-consecrating-bishops-priests-and-deacons/ordering-deacons`
- Priests: `book-common-prayer/ordaining-and-consecrating-0`
- Bishops: `book-common-prayer/ordaining-and-consecrating-1`
### American 1789 — justus HTML (clean single-edition pages)
- Deacons: `1789/Deacon_1789.htm`    Priests: `1789/Priests_1789.htm`
- Bishops: `1789/Bishops_1789.htm`   (Preface: at the head of the Deacon page — confirm)
- Note: the 1789 Ordinal Litany is a separate page `1789/Ordinal_Litany_1789.htm`
  and there is an `Ordinal_Communion_1789.htm` (the propers). `Consecration_1789.htm`
  is "Consecration of a Church" — a DIFFERENT service, NOT in scope.
### American 1892 — justus `1892/Ordinations_1892.pdf` (or inherits 1789 if identical)
  The 1892 index links Bishops/Priests/Deacons back to the 1789 HTML + serves a PDF.
  Confirm whether 1892 changed the Ordinal; if identical → inherit 1789 reviewed-
  unchanged (like the 1892 Catechism).
### American 1928 — justus `1928/Ordinal.htm` (all three orders on one page + preface)
### American 1979 — PD ASCII e-text `bcpepscl.txt` (Episcopal Services): "The Ordination
  of a Bishop / …a Priest / …a Deacon" + "The Preface" + "The Litany for Ordinations".
  Transform-script it (ingest/transform_1979_ordinal.py; source→script→file).

## Anchor menu — per-order, fixed by the 1549/1552 flagship (see WAVE8_STRUCTURING_GUIDE.md)
Shared vocabulary reused across orders/editions so cross-EDITION diffs read as body
changes. The three orders differ in internal order; each order's menu is fixed by
its own flagship and kept consistent across that order's editions.
