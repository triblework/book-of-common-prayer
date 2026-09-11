# Wave 13 — build guide: the Psalter

Rulings taken from the maintainer 2026-09-02 on `WAVE13_SCOPING.md`. **LOCKED.**

- **A — three files of fifty.** `psalter/psalms-1-50.md`, `psalms-51-100.md`,
  `psalms-101-150.md`; `## Psalm N` anchors within, in order.
- **B (revised §4) — every edition from its own source; no backward
  derivation.** 1662 CoE · 1892 `1892/Psalms.pdf` (whitespace repair, gated) ·
  1928 justus width-400 text column, sidebar NOT applied · 1979 e-text.
  1789, 1549–1604 and the Scottish line are RECORDED GAPS (present, inherit,
  `inherited-unreviewed`), never `absent:`.
- **C — the mediant is normalized to ` : `** in every edition (spec §4: pointing
  is typography). NOTICE.md records that 1789 printed no breath-mark, 1892 a
  musical colon and 1928 an asterisk.
- **D — two extras in scope:** `psalter/selections.md` (the 1789 Selections of
  Psalms) and `tables/proper-psalms.md` (the Tables of Proper Psalms, closing a
  Wave-14 recorded gap).

## Cell format

    # The Psalter

    ## Psalm 1

    > Beatus vir qui non abiit, &c.

    Blessed is the man that hath not walked in the counsel of the ungodly, ... : and hath not sat in the seat of the scornful.

    2 But his delight is in the law of the Lord : and in his law will he exercise himself day and night.

- One verse per line, blank line between (the rendered convention the published
  canticles already use).
- **Printed verse numbering is kept** (spec §10), including the book's own
  convention of leaving verse 1 unnumbered. The number is written `N ` — never
  `N.` as 1892 prints it, because a digit + period + space + capital is a
  sentence boundary to `sentence_split.py` and would split the number off the
  verse (the Wave-14 trailing-period trap).
- The Latin incipit is a `> ` line under the anchor, as the canticles render it.
- Psalm 119's twenty-two portions each keep their own incipit line inside
  `## Psalm 119`; its verse numbering runs 1–176 unbroken.
- **Omitted, deliberately:** the thirty-day course headings ("Day 1. Morning
  Prayer"), 1928's division into Books, and 1928's blank-line divisions of long
  psalms. They are course apparatus rather than psalm text, and the CoE renders
  its day headings in a web-edited form ("Day 1.") that would put a spurious diff
  on every day boundary. Recorded in NOTICE.md.

## Gates

1. **Verse runs.** Every psalm's verses must be the consecutive run 1..N, and
   the parser ABORTS otherwise.
2. **Cross-edition verse counts.** 1662, 1892 and 1928 all number Coverdale the
   same way, so each psalm's verse count must agree across the three; a
   disagreement is either a genuine renumbering (exempted with a reason) or a
   dropped verse. 1979 is checked for completeness only — it is a new
   translation with its own verse divisions.
3. **150 psalms per edition.** A count is the cheapest detector of a lost page.
4. **Fidelity** (w13_fidelity.py) and **audit** (w13_audit.py), both, every pass.
