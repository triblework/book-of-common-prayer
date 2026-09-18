"""w18_docs.py — the Wave-18 edits to the published docs (SOURCES, NOTICE, README).

Every replacement must match exactly once; if one goes stale nothing is
written. Run after w18_cells.py and gen_wave18_provenance.py.
"""
import os
import re
import sys

WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECTION = """### The 1662 text against the Annexed Book (Wave 18)

The 1662 node is transcribed from the Church of England's currently authorized
text (see the 1662 sourcing note below). Wave 18 read it against a **1662
authority**: *The Book of Common Prayer ... from the original manuscript
attached to the Act of Uniformity of 1662* (Her Majesty's Printing Office,
September 1892) — the **Annexed Book**, the manuscript the Convocations
subscribed on 20 December 1661, set in type "verbatim et literatim" and
compared word by word and stop by stop with the photographs from which the 1891
House of Lords facsimile was made. The scan is Wikimedia Commons's
`File:The_Book_of_Common_Prayer.pdf` (PD-US, 577 page images), read with the
Wave-17 pipeline.

**What the witness may be used for.** Its own preface records that the earliest
printed copies — the Sealed Books — "differ considerably from that original
standard in various details of orthography and punctuation", and that the
manuscript was "not to be a standard of orthography". So this pass collates
substance and structure only. The witness reads *vngodly*, *ioy*, *shew*,
*soveraign*, and opens Psalm 90:1 "O Lord thou hast been our refuge" where the
carrier has "Lord, thou hast been our refuge": differences between printings,
not errors, and none of them was imported.

**Two corrections, both in the Psalter.** The whole Psalter was aligned verse
by verse against scan pages 345–507. Only two of the 2,508 verses carried no
mediant in the carrier, and the book points both:

| Verse | The Church of England text | The Annexed Book |
|---|---|---|
| Psalm 2:12 | …from the right way, if his wrath… | …from the [right] way **:** if his wrath… (p. 346) |
| Psalm 68:1 | …be scattered let them also… | …be scattered **:** let them also… (p. 413) |

Every one of the 2,508 verses now carries exactly one mediant. Elsewhere the
page OCR corroborated the carrier's mediant at its own pivot word in 1,561 of
the 1,893 verses whose alignment is sound; the rest are OCR damage, not
absence — thirty of them re-read line by line at 4400px showed the mediant
legible, and in the same place, in twenty-five.

**Eight flags closed.** Psalm 89:50 is confirmed as printed: the doxology that
closes Book III stands inside verse 50 after a single mediant, with no verse 51
(p. 443). The five reign-dependent flags on the monarch's name are answered —
the book prays for **King Charles** in Morning Prayer (p. 70), Evening Prayer
(p. 80), the Litany (p. 86), the Ordinal's litany (p. 526) and the prayer for
the Church Militant (p. 254) — so the name the source prints is period-correct.
And the psalm-cento flag in the Forms of Prayer to be used at Sea is answered:
the book labels the one psalm it uses ("Confitemini Domino. Psal. 107.",
p. 513) and prints no psalm label over the composite hymns (p. 517), which is
what the file reflects.

**The royal names are gone, and the book's blank is shown.** The Annexed Book
names the King and leaves **every other royal name a blank** — in Morning and
Evening Prayer the title itself breaks off at "A Prayer for" and the prayer at
"we humbly beseech thee to bless"; in the Litany and the Ordinal the petition
breaks off after "bless and preserve". The Church of England source fills those
blanks with the living Royal Family (Queen Camilla, William Prince of Wales,
the Princess of Wales). Those names are not the 1662 reading, so they are
removed and the space the book leaves is set visibly as `________`, the way a
modern book prints "N. ________" for a name to be supplied. **Nothing is
reconstructed into it.** What the printed Sealed Books named there is unknown —
no scan of one is available on an allow-listed host — and that remains flagged.
On the same ruling, the Sea rubric now reads "his Majesty's Navy", which the
book has ("also vsed in his Majesties Navy every day", p. 508) and which the
source had left unrevised in the same file that prays for "King CHARLES": that
is a word, not a spelling, so the witness settles it.

**Two lines of website chrome removed.** `occasional-offices/prayers-at-sea.md`
had published two lines of Church of England site furniture as text ("To
experience the best that the Church of England website has to offer, you need
to enable JavaScript…" and "Popular search items"). They are deleted, and a
gate now refuses that furniture anywhere in the corpus.

**What is recorded and NOT changed.** The communion **admission rubric** the
carrier prints (an account to the Ordinary, seven days, an opportunity for
interview) is no part of the 1662 text — the Annexed Book prints the "open and
notorious evil liver" rubric of 1549–1604 (p. 246). Substituting it would mean
setting a paragraph of the manuscript's own orthography inside a modernized
cell, which is a different decision from showing a blank; it is flagged with
what the page shows.

**What this does not claim.** Nothing here is a collation of the 1662 spelling
or of its ordinary punctuation, which this witness is explicitly unfit to
settle. The 1928 and 1979 Psalters remain unread against any scan.

---

"""

ROYAL_NOTE = ("The CoE source serves the LIVING Royal Family. The Annexed Book "
              "(HMSO 1892) prints no name here: it leaves the passage blank, "
              "and in the daily offices breaks the title off at `A Prayer "
              "for`. The living names are therefore removed and the blank is "
              "set as `________`. What the printed 1662 books named in that "
              "space is unknown — no scan of a Sealed Book is available on an "
              "allow-listed host — so nothing is reconstructed into it.")

EDITS = {
    'repo-root/SOURCES.md': [
        # the new section
        ("---\n\n## English line (`main`)", SECTION + "## English line (`main`)"),
        # the sourcing note gains the witness
        ("Reproduced with the required\nCrown-copyright acknowledgment: **BCP 1662** (see `NOTICE.md`).",
         "Reproduced with the required\nCrown-copyright acknowledgment: **BCP 1662** (see `NOTICE.md`).\n"
         "Wave 18 read this text against a 1662 authority — the Annexed Book, in\n"
         "HMSO's 1892 type-reproduction (Wikimedia Commons, PD-US) — for substance\n"
         "and structure; see *The 1662 text against the Annexed Book* above."),
        # rows closed
        ("| 1662 Morning Prayer (Prayer for the King's Majesty) | `King CHARLES` | The CoE source serves the reigning monarch (Charles III); the 1662 book as first printed named the then-sovereign (Charles II). Reign-dependent; reconcile against a dated 1662 scan. |\n", ""),
        ("| 1662 Litany (King) | `CHARLES, our most gracious King and Governor` | The CoE source names the reigning monarch (Charles III); the 1662 book named the then-sovereign (Charles II). Reign-dependent; reconcile against a dated 1662 scan. |\n", ""),
        ("| 1662 Communion (Collect for the King) | `CHARLES our King` | The CoE source serves the reigning monarch (Charles III); the 1662 book named Charles II. Reign-dependent. |\n", ""),
        ("| 1662 Ordering of Deacons | `CHARLES` | 'CHARLES'; the CoE source prints the reigning monarch (Charles III); the 1662 book as first printed named the then-sovereign (Charles II); reign-dependent; reconcile against a dated 1662 page scan |\n", ""),
        ("| 1662 Psalm 2 | `no mediant` | the CoE text prints this verse without a mediant; the 1928 page prints one. Carried as the CoE prints it -- the 1662 pointing is not imported from another edition. Confirm against a 1662 scan |\n", ""),
        ("| 1662 Psalm 68 | `no mediant` | the CoE text prints this verse without a mediant; the 1928 page prints one. Carried as the CoE prints it. Confirm against a 1662 scan |\n", ""),
        ("| 1662 Psalm 89 | `Praised be the Lord for evermore` | the CoE prints the doxology that closes Book III INSIDE verse 50, with a single mediant placed before it, where the 1928 book prints it as a separate verse 51. It reads like two verses run together; carried as printed. Confirm against a 1662 scan |\n", ""),
        # rows rewritten
        ("| 1662 Morning Prayer (Prayer for the Royal Family) | `Queen Camilla, William Prince of Wales, the Princess of Wales` | The CoE source serves the current Royal Family; the 1662 book named the then-Royal Family. Reign-dependent; reconcile against a dated 1662 scan. |",
         "| 1662 Morning / Evening Prayer, Litany, Ordinal (Prayer for the Royal Family) | `Queen Camilla, William Prince of Wales, the Princess of Wales` | " + ROYAL_NOTE + " |"),
        ("| 1662 Ordering of Deacons | `Queen Camilla, William Prince of Wales, the Princess of Wales` | 'Queen Camilla, William Prince of Wales, the Princess of Wales'; the CoE source prints the current Royal Family; the 1662 book named the then-Royal Family; reign-dependent; reconcile against a dated 1662 page scan |",
         "| 1662 Ordering of Deacons | `Queen Camilla, William Prince of Wales, the Princess of Wales` | " + ROYAL_NOTE + " (Annexed Book p. 527.) |"),
        ("| 1662 Communion (admission rubric) | `give an account to the Ordinary within seven days an opportunity for interview` | The CoE admission rubric adds administrative wording that reads like a modern statutory amendment; the 1662 book carried the `open and notorious evil liver` rubric. |",
         "| 1662 Communion (admission rubric) | `give an account to the Ordinary within seven days an opportunity for interview` | CONFIRMED to be no part of the 1662 text: the Annexed Book prints the `open and notorious evil liver` rubric of 1549-1604 in this place (p. 246). A later statutory amendment, retained as the CoE prints it. |"),
        ("| 1662 Public Baptism (The Final Exhortation) | `Foreasmuch` | source prints 'Foreasmuch'; the Private and Riper-Years 1662 forms print 'Forasmuch'; kept as printed; confirm against a page scan |",
         "| 1662 Public Baptism (The Final Exhortation) | `Foreasmuch` | CHECKED: the Annexed Book reads `Forasmuch as this childe hath promised` (p. 277), and `Forasmuch` in the private form (p. 283). Kept as the CoE prints it — that witness disclaims its own orthography, so it can settle a word but not a spelling. |"),
        ("| `occasional-offices/prayers-at-sea.md` (1662) | `psalm-cento` | Two runs of psalm verses in the Sea forms (the composite \"Hymn of Praise and Thanksgiving\" after a tempest, and the one after victory) carry no single printed psalm label, so no citation is supplied for them. The verses are deferred to the Psalter wave along with the labelled psalms. Confirm against a page scan whether the book names a source for either hymn. |",
         ""),
    ],
    'repo-root/README.md': [
        ("pointing of seven verses — the musical colon that divides a verse for\nchanting.",
         "pointing of seven verses — the musical colon that divides a verse for\nchanting. The 1662 Psalter has been read against the Annexed Book — the\nmanuscript annexed to the Act of Uniformity 1662, in HMSO's 1892\ntype-reproduction — which restored the mediant in two verses and confirmed a\nthird reading; all 2,508 of its verses now carry exactly one mediant."),
    ],
    'repo-root/NOTICE.md': [
        ("## A note on transcription\n\nThese transcriptions follow public-domain source transcriptions (principally\nCharles Wohlers' collection at the Society of Archbishop Justus) cross-checked,\nwhere practical, against public-domain page scans.",
         """- **2026-09-18** — Wave 18: the **1662 text against the Annexed Book**. The
  1662 node is transcribed from the Church of England's currently authorized
  text; this wave read it against a 1662 authority — the manuscript annexed to
  the Act of Uniformity, which the Convocations subscribed on 20 December 1661,
  in the type reproduction Her Majesty's Printing Office made from it in 1892
  after a word-by-word comparison with photographs of the manuscript (Wikimedia
  Commons, public domain in the US, 577 page images).
  - **The witness is unfit to settle spelling, and says so.** Its preface
    records that the printed Sealed Books "differ considerably from that
    original standard in various details of orthography and punctuation", and
    that the manuscript was "not to be a standard of orthography". Only
    substance and structure were collated; no spelling was imported.
  - **Two corrections, both in the Psalter.** All 2,508 verses were aligned
    against the scan. Only two carried no mediant — the musical colon that
    divides a verse for chanting — and the book points both: Psalm 2:12 and
    Psalm 68:1. Every verse of the 1662 Psalter now carries exactly one.
  - **Eight flags closed.** Psalm 89:50 is confirmed as printed (the doxology
    that closes Book III stands inside verse 50, with no verse 51). The book
    prays for **King Charles** in Morning and Evening Prayer, the Litany, the
    Ordinal's litany and the prayer for the Church Militant, so the name the
    source prints is period-correct. At sea, the book labels the single psalm
    it uses and leaves the composite hymns unlabelled, as the file has it.
  - **Two lines of website chrome deleted** from the Forms of Prayer to be used
    at Sea, where they had been published as text; a gate now refuses scraped
    site furniture anywhere in the corpus.
  - **The royal names now follow the book.** The Annexed Book names the King
    and leaves every other royal name a blank; the Church of England source
    fills those blanks with the living Royal Family. On the maintainer's
    ruling — print what the original copies print, and show the space where
    they leave one — the living names are removed from Morning and Evening
    Prayer, the Litany and the Ordinal, and the blank is set visibly as
    `________`. Nothing is reconstructed into it: what the printed Sealed
    Books named there is unknown, and stays flagged. On the same ruling the
    Sea rubric now reads "his Majesty's Navy", as the book does.
  - Recorded, not changed: the communion admission rubric the source prints is
    no part of the 1662 text (the book has the "open and notorious evil liver"
    rubric); replacing it would mean setting the manuscript's own orthography
    inside a modernized text. Flagged with what the page shows.
  - This changes `texts/original` and `texts/normalized` in two verses of the
    1662 Psalter, in four prayers for the Royal Family and in one rubric, and
    removes two non-liturgical lines from one 1662 file.

## A note on transcription

These transcriptions follow public-domain source transcriptions (principally
Charles Wohlers' collection at the Society of Archbishop Justus, with page
scans from Wikimedia Commons) cross-checked, where practical, against
public-domain page scans."""),
    ],
}


def main():
    stale, done = [], 0
    for rel, subs in EDITS.items():
        path = os.path.join(WT, rel)
        text = open(path, encoding='utf-8').read()
        for old, new in subs:
            if text.count(old) != 1:
                stale.append('%s: %d matches for %r' % (rel, text.count(old), old[:70]))
                continue
            text = text.replace(old, new)
            done += 1
        if not stale:
            open(path, 'w', encoding='utf-8').write(text)
    if stale:
        print('STALE (nothing written):')
        for s in stale:
            print('  ' + s)
        sys.exit(1)
    print('w18_docs: %d edits in %d files' % (done, len(EDITS)))


if __name__ == '__main__':
    main()
