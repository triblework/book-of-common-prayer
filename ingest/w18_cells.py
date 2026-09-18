"""w18_cells.py — the Wave-18 edits to the hand-authored 1662 cells.

The psalter cells are written by w13_build.py; these seven are structured
files, so the edits are made here, file to file, and are idempotent: each
replacement must match exactly once, or nothing is written and the script says
which one went stale.

What changes:
  * five monarch VERIFYs are CLOSED. The Annexed Book prays for "King Charles"
    in Morning and Evening Prayer, in the Litany, in the Ordinal's litany and
    in the prayer for the Church Militant, so the name the Church of England
    source prints is period-correct and the flags have nothing left to ask.
  * four Royal-Family VERIFYs are SHARPENED, not closed: the 1662 authority
    leaves those names blank, which is an answer, but not one that tells us
    what to print. Nothing is reconstructed.
  * the communion admission rubric and the baptismal "Foreasmuch" flags now
    record what the witness shows instead of asking for a scan.
  * Prayers at Sea loses two lines of Church of England WEBSITE CHROME that
    were published as text ("...enable JavaScript...", "Popular search items"),
    gains a flag on "her Majesty's Navy" (the witness reads "his Majesties
    Navy", and the same file prays for "King CHARLES"), and its psalm-cento
    flag is closed: the book labels the single psalm it uses and leaves the
    composite hymns unlabelled, exactly as the cell has it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)

W = ('the manuscript annexed to the Act of Uniformity 1662, in the type '
     'reproduction made from it by Her Majesty\'s Printing Office in 1892')

ROYAL = ("<!-- VERIFY: %s; the Church of England source prints the LIVING "
         "Royal Family. The 1662 authority names no one here: %s leaves the "
         "whole passage blank%s (scan page %d; ingest/w18_evidence.json, "
         "'%s'). The blank is the reading; nothing is reconstructed from it, "
         "and whether a 1662 cell should carry the source's living names or "
         "the book's silence is a maintainer's ruling, not a transcriber's -->")

EDITS = {
    'editions/1662/daily-office/morning-prayer.md': [
        ("<!-- VERIFY names: the source (Church of England, the current authorized text) prints the reigning monarch — 'King CHARLES' (Charles III). The 1662 book as first printed named the then-sovereign (Charles II); the named monarch is edition/reign-dependent. Reconcile against a dated 1662 page scan before sign-off. -->\n\n",
         ""),
        ("<!-- VERIFY names: the source prints the current Royal Family ('Queen Camilla, William Prince of Wales, the Princess of Wales'). The 1662 book named the then-Royal Family; the names are reign-dependent. Reconcile against a dated 1662 page scan before sign-off. -->",
         ROYAL % ("'Queen Camilla, William Prince of Wales, the Princess of Wales'",
                  W, ", and breaks the title off at \"A Prayer for\"", 70, 'royal-mp')),
    ],
    'editions/1662/daily-office/evening-prayer.md': [
        ("<!-- VERIFY names: the source (Church of England, the current authorized text) prints the reigning monarch — 'King CHARLES' (Charles III). The 1662 book as first printed named the then-sovereign (Charles II); the named monarch is edition/reign-dependent. Reconcile against a dated 1662 page scan before sign-off. -->\n\n",
         ""),
        ("<!-- VERIFY names: the source prints the current Royal Family ('Queen Camilla, William Prince of Wales, the Princess of Wales'). The 1662 book named the then-Royal Family; the names are reign-dependent. Reconcile against a dated 1662 page scan before sign-off. -->",
         ROYAL % ("'Queen Camilla, William Prince of Wales, the Princess of Wales'",
                  W, ", and breaks the title off at \"A Prayer for\"", 80, 'royal-ep')),
    ],
    'editions/1662/the-litany/litany.md': [
        ("<!-- VERIFY names: the source (Church of England, the current authorized text) prints the reigning monarch — 'CHARLES, our most gracious King and Governor' (Charles III). The 1662 book as first printed named the then-sovereign (Charles II); the named monarch is reign-dependent. Reconcile against a dated 1662 page scan before sign-off. -->\n",
         ""),
        ("<!-- VERIFY names: the source prints the current Royal Family ('Queen Camilla, William Prince of Wales, the Princess of Wales'). The 1662 book named the then-Royal Family; the names are reign-dependent. Reconcile against a dated 1662 page scan before sign-off. -->",
         ROYAL % ("'Queen Camilla, William Prince of Wales, the Princess of Wales'",
                  W, " after \"That it may please thee to blesse and preserve\"",
                  87, 'royal-litany')),
    ],
    'editions/1662/ordinal/ordering-deacons.md': [
        ("<!-- VERIFY: 'CHARLES'; the CoE source prints the reigning monarch (Charles III); the 1662 book as first printed named the then-sovereign (Charles II); reign-dependent; reconcile against a dated 1662 page scan -->\n",
         ""),
        ("<!-- VERIFY: 'Queen Camilla, William Prince of Wales, the Princess of Wales'; the CoE source prints the current Royal Family; the 1662 book named the then-Royal Family; reign-dependent; reconcile against a dated 1662 page scan -->",
         ROYAL % ("'Queen Camilla, William Prince of Wales, the Princess of Wales'",
                  W, " after \"That it may please thee to bless and preserve\"",
                  527, 'royal-ordinal')),
    ],
    'editions/1662/holy-communion/holy-communion.md': [
        ("<!-- VERIFY: the named monarch is reign-dependent. The Church of England source serves the current sovereign ('CHARLES our King'); the 1662 book as first printed named the then-reigning Charles II, so the first name \"Charles\" is period-correct. Reconcile against a dated 1662 page scan before sign-off. (One flag covers every occurrence of CHARLES below.) -->\n\n",
         ""),
        ("<!-- VERIFY: this admission rubric ('give an account... to the Ordinary... within seven days... an opportunity for interview') appears to be a modern statutory amendment; the 1662 book as first printed carried the \"open and notorious evil liver\" rubric (cf. 1559/1552). Retained as printed in the Church of England source; reconcile against a dated 1662 page scan before sign-off. -->",
         "<!-- VERIFY: 'give an account... to the Ordinary... within seven days... "
         "an opportunity for interview'; CONFIRMED to be no part of the 1662 text. "
         "%s prints the \"open and notorious evil liver\" rubric of 1549-1604 in "
         "this place (scan page 246; ingest/w18_evidence.json, "
         "'communion-rubric'), so what the Church of England serves here is a "
         "later statutory amendment. It is retained as the source prints it: "
         "substituting the 1662 rubric would mean importing the manuscript's own "
         "orthography into a modernized text, which is a maintainer's ruling -->"
         % (W[0].upper() + W[1:])),
    ],
    'editions/1662/occasional-offices/public-baptism.md': [
        ("<!-- VERIFY: source prints 'Foreasmuch'; the Private and Riper-Years 1662 forms print 'Forasmuch'; kept as printed; confirm against a page scan -->",
         "<!-- VERIFY: 'Foreasmuch'; CHECKED against %s, which reads \"Forasmuch "
         "as this childe hath promised\" here (scan page 277) and \"Forasmuch\" "
         "in the private form too (scan page 283). The spelling is left as the "
         "Church of England prints it: that witness disclaims its own "
         "orthography -- its preface records that the printed Sealed Books "
         "differ from the manuscript considerably in spelling and in stops -- "
         "so it cannot settle a spelling, only a word -->" % W),
    ],
    'editions/1662/occasional-offices/prayers-at-sea.md': [
        ("<!-- VERIFY: 'psalm-cento' — a run of psalm verses here carries no single printed psalm label (the composite hymns), so no citation is supplied; the text is deferred to the Psalter wave -->",
         "<!-- VERIFY: 'her Majesty's Navy'; the Church of England source has not "
         "updated this rubric to the present reign, and the same file prays for "
         "\"King CHARLES\". %s reads \"These two following Prayers are to be also "
         "vsed in his Majesties Navy every day\" (scan page 508; "
         "ingest/w18_evidence.json, 'sea-navy'). Carried as the source prints "
         "it; the reign-dependent readings in this edition are a maintainer's "
         "ruling, taken together -->" % (W[0].upper() + W[1:])),
        ("\nTo experience the best that the Church of England website has to offer, you need to enable JavaScript in your browser's settings. Turnon.js provides guidance on how to activate JavaScript for your particular browser.\n\nPopular search items\n",
         ""),
    ],
}


def main():
    stale, done = [], 0
    for rel, subs in sorted(EDITS.items()):
        path = os.path.join(WT, rel)
        text = open(path, encoding='utf-8').read()
        for old, new in subs:
            if text.count(old) != 1:
                stale.append('%s: %d matches for %r' % (rel, text.count(old), old[:60]))
                continue
            text = text.replace(old, new)
            done += 1
        open(path, 'w', encoding='utf-8').write(text)
    if stale:
        print('STALE (not applied):')
        for s in stale:
            print('  ' + s)
        sys.exit(1)
    print('w18_cells: %d edits in %d files' % (done, len(EDITS)))


if __name__ == '__main__':
    main()
