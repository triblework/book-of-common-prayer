# Wave 7 — the Catechism: confirmed source map

One service, one file: `occasional-offices/catechism.md`.

Path decision: the Catechism is historically bundled with Confirmation (its full
title is "A Catechism, that is to say, an Instruction to be learned of every
person before he be brought to be Confirmed by the Bishop"), and this repo already
groups Confirmation under `occasional-offices/`. So the Catechism lives at
`occasional-offices/catechism.md`, a sibling of `confirmation.md`.

## SCOPE decision (documented once — keep consistent across editions)
`catechism.md` = the catechism **title** + the **Question-and-Answer body**
(from "What is your name?" through the final answer). The framing/catechizing
rubrics that surround the catechism in the printed book — the Confirmation
preface, "So soon as the children can say…", and "The Curate of every parish
shall diligently … instruct and examine … in some part of this Catechism" — are
**Confirmation-office rubrics** and already live in `confirmation.md` (Wave 5).
Do NOT duplicate them here. This keeps a clean catechism-vs-confirmation split and
means the catechism diffs read as pure doctrinal-text diffs.

## Presence (confirmed against sources; encode in editions.yaml)
Catechism is present at the **ten daily-office editions**:
English 1549 1552 1559 1604 1662, Scottish 1637, American 1789 1892 1928 1979.
ABSENT at 1764 (Communion-only "Wee Bookie"); **1929 inherited-absent** (this
repo's Scottish line is Communion-only after 1637 — represented exactly as
MP/EP/Baptism/Matrimony are, i.e. the drop is inherited from 1764; do NOT expand
the 1929 line for the Catechism this pass).
  → add `occasional-offices/catechism` to the `present:` of those ten editions.
  → add `occasional-offices/catechism` to 1764 `absent:`; 1929 inherits the drop.

## THE FLAGSHIP DIFF — the Catechism GROWS
1. **1549 → 1552** (this pair fixes the canonical anchor menu): 1552 expands the
   Decalogue to its **full scriptural form** and adds the **Exodus preamble**
   ("I am the Lord thy God which have brought thee out of the land of Egypt, out
   of the house of bondage"). 1549 gives only the short commandment forms
   ("Thou shalt have none other Gods but me", etc.). Diff: `git diff v1549 v1552`.
2. **1559 → 1604** (the famous one): 1604 adds the entire **sacraments section**
   ("How many Sacraments hath Christ ordained in his Church?" → Baptism → the
   Lord's Supper), drafted by John Overall and authorized at Hampton Court. The
   pre-1604 catechism ends at the Lord's-Prayer exposition ("…And therefore I say,
   Amen. So be it."). Diff: `git diff v1559 v1604 -- texts/normalized/occasional-offices/catechism.md`
   reads as a clean `## The Sacraments` insert.

## Canonical anchor menu (established by the 1549+1552 flagship — reuse for ALL editions)
The catechism is continuous Q&A in the source (no printed section headings); these
`##` anchors are our editorial structure, chosen as the four classic divisions
plus the 1604 sacraments insert, so a section's presence/absence is the diff:
```
## The Baptismal Covenant   (Name / Who gave you this name / What did your Godfathers promise / Dost thou not think thou art bound)
## The Creed                (Rehearse the Articles of thy Belief + "What dost thou chiefly learn in these Articles")
## The Ten Commandments     (how many / which be they [+ Exodus preamble 1552+] / the Decalogue / "what dost thou chiefly learn" → duty to God, duty to neighbour)
## The Lord's Prayer        ("My good child, know this…" → say the Lord's Prayer + "What desirest thou of God in this Prayer")
## The Sacraments           (1604+ ONLY — "How many Sacraments…" / word Sacrament / parts / Baptism q&a / Lord's Supper q&a)
```
Labels: `**Question.**` / `**Aunswere.**` / `**Answere.**` / `**Answer.**` /
`**Catechist.**` — use the designation AS PRINTED in that edition (1662 uses
"Catechist." for "Rehearse the Articles" and "My good child").

## Sources per edition
- 1549  justus 1549/Confirmation_1549.htm — Catechism BUNDLED on the Confirmation
        page. Spine: `ingest/spines-confirmation/1549.md` (Wave 5 fetch). No sacraments.
- 1552  justus 1552/Confirmation_1552.htm — bundled. Spine: `…/1552.md`. No sacraments.
        (title source prints "THAT IS TO SAVE" = OCR for "saye" → VERIFY.)
- 1559  justus 1559/Confirmation_1559.htm — bundled. Spine: `…/1559.md`.
        The justus 1559 page ALSO appends the 1604 sacraments block under the caption
        "Page from the 1604 Book of Common Prayer showing the Catechism with additional
        questions" + a trailing note "The following questions & answers were added in
        1604". So the 1559 catechism proper ENDS at the Lord's-Prayer exposition; the
        appended block is the 1604 material (see below). No sacraments in 1559.
- 1604  DERIVE from 1559 = 1559 body + the 1604 sacraments section (the justus-1559
        page's appended, captioned "added in 1604" block). No 1604 justus page.
- 1662  CoE  book-common-prayer/catechism  (slug confirmed; 551K page, catechism-only,
        ends at "…be in charity with all men"). Spine: `ingest/spines-w7/1662.md`.
- 1637  justus Scotland/Confirmation_1637.htm — bundled. Spine: `…/1637.md`. Post-1604
        → HAS the sacraments section. (Scottish; period spelling of its own.)
- 1789  justus 1789/Catechism.htm (HTML) / Catechism_1789.pdf — STANDALONE catechism
        (NOT bundled on Confirmation_1789.htm, which is office-only). *** BLOCKED:
        justus.anglican.org is having a live TLS/availability outage (WebFetch →
        SSL UNSUPPORTED_PROTOCOL; urllib → 404 even on justus root; CoE fetched fine).
        The 1789 Confirmation spine confirms the catechism is separate. Retry justus. ***
- 1892  justus 1892/Catechism&Confirm_1892.pdf — STANDALONE (justus HTML index links
        the 1892 catechism back to ../1789/Catechism.htm and serves a 1892 PDF, as with
        the other 1892 offices). *** BLOCKED on the same justus outage — retry. ***
- 1928  justus 1928/Confirnation.htm (source filename typo) — the Catechism was recast
        as the **"Offices of Instruction"** (two Offices, Q&A). Spine:
        `ingest/spines-confirmation/1928.md` (Wave 5 fetch). DECISION: represent the
        1928 form under catechism.md as its lineal replacement (the recasting is the
        meaningful diff), NOT a rename to a new file — same treatment as churching→1979
        "Thanksgiving for the Birth". Note the transformation once in provenance/SOURCES.
- 1979  bcpprayr.txt (Prayers and Thanksgivings, Catechism, Historical Documents,
        Tables) — "An Outline of the Faith, commonly called the Catechism".
        Cached: `scrape-cache/…bcpprayr.txt….html`. Transform-script it
        (`ingest/transform_1979_catechism.py`).

## justus outage note (2026-08-13)
At Wave-7 start justus.anglican.org is unreachable (TLS handshake fails for modern
clients; root returns 404). Everything else is sourced from cache (Wave-5 confirmation
spines) or CoE (1662) or the cached 1979 e-text. Only **1789 and 1892** need a fresh
justus fetch (their standalone catechism pages). Retry justus before publishing; do
NOT derive the American catechisms from 1662 or from memory — source them from their
own witnesses when justus returns.
