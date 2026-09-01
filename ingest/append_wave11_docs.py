#!/usr/bin/env python3
"""Wave 11 — add SOURCES.md rows for the wave's VERIFY items and its scope note."""
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
S = WT / 'repo-root' / 'SOURCES.md'

ROWS = [
 ("`prayers-and-thanksgivings/for-the-clergy-and-people.md` (1559, 1604)", "untitled",
  "The source prints this prayer with no title of its own — it follows the preceding "
  "prayer directly, opening with a drop capital. The bracketed heading is editorial; "
  "confirm against a page scan."),
 ("`prayers-and-thanksgivings/prayer-after-the-former.md` (1604, 1637)", "untitled",
  "Printed without a title in these editions (1662 heads it \"A Prayer that may be said "
  "after any of the former\"). The bracketed heading is editorial. The 1559 page's note "
  "\"This prayer added in 1604\" sits immediately after this text, but the spine has lost "
  "the page's visual association of note to referent — confirm the attribution."),
 ("`prayers-and-thanksgivings/for-the-sovereign.md` (1604)", "Quene Elizabeth",
  "RECORDED GAP, not a reading. The 1559 page's apparatus says this prayer was "
  "\"Replaced by a prayer for the King in 1604\" and gives the style \"Sovereign Lord "
  "King James\", but attests neither the pronouns nor the spellings the 1604 book "
  "printed. The attested 1559 wording is retained rather than reconstructing a text no "
  "allow-listed source supports; resolve from a 1604 facsimile."),
]

SCOPE = """
### Prayers and Thanksgivings upon several Occasions (Wave 11)

One file per prayer under `prayers-and-thanksgivings/`, for every edition that
carries the block. 1552–1637 print these prayers **inline after the Litany
suffrages**; 1662 and the American line print them as a separate section. The
repo gives them their own family throughout so each prayer has a single stable
path and its own per-edition diff; the earlier books' inline placement is a
book-order fact recorded in `NOTICE.md`, not a text difference.

Two relocations are recorded rather than shown as deletions: the **state
prayers** (sovereign, royal family, clergy) move from this block into Morning
and Evening Prayer at 1662, and **A Prayer for all Conditions of Men** and the
**General Thanksgiving** move into Morning and Evening Prayer in the American
line from 1789. Both texts continue in `daily-office/`.

Excluded from this wave, each its own section of the book: the 1662 *Forms of
Prayer to be used at Sea*, the 1892/1928 *Penitential Office*, *Family Prayer*,
and the 1789 *Prayer and Thanksgiving to Almighty God*.

The 1789 *Prayer to be used at the Meetings of Convention* is **not** carried at
1789: the source page's own apparatus records it as added in 1845.
"""


def main():
    t = S.read_text(encoding='utf-8')
    # append rows to the uncertain-passages table
    marker = '## Uncertain passages'
    i = t.index(marker)
    j = t.index('\n\n', t.index('|----------------|', i))
    rows = ''.join(f"\n| {f} | `{r}` | {n} |" for f, r, n in ROWS)
    t = t[:j] + rows + t[j:]
    # scope section
    if 'Prayers and Thanksgivings upon several Occasions (Wave 11)' not in t:
        t = t[:i] + SCOPE.lstrip('\n') + '\n' + t[i:]
    S.write_text(t, encoding='utf-8')
    print(f"SOURCES.md: +{len(ROWS)} rows, scope section added")


if __name__ == '__main__':
    main()
