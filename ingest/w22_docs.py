"""w22_docs.py -- Wave 22's edits to the published SOURCES.md, NOTICE.md and
README.md. Idempotent (each edit checks for its own marker); every exact
replacement must match exactly once or nothing is written. Run after
w13_build_1892.py and gen_wave22_provenance.py."""
import os, re, sys
WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WT, 'ingest'))
import w22_witness as W


def edit(rel, pairs):
    p = os.path.join(WT, rel)
    s = open(p, encoding='utf-8').read()
    for old, new, marker in pairs:
        if marker in s or (new == '' and old not in s):
            continue
        assert s.count(old) == 1, (rel, old[:70], s.count(old))
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)


SECTION = '''### The 1892 Psalter: the full pointing and punctuation collation (Wave 22)

Wave 17 read the 1892 Psalter against the Standard Book scan for its words and
spellings, and checked the pointing only where Wave 13's mediant gate had
flagged an anomaly, because page OCR cannot tell `:` from `;`. Wave 22 is the
pass Wave 17 said it could not make: **every mediant in all 2,508 verses has
been read by eye**, off 4400px crops of the pivot word stacked into labelled
strips (about 150 strips in all). The machine found the places and classed
each verse; a 150-verse random control (seed 20261016) disagreed with the
machine in 0 of 150 at the mediant, and the full pass over the 2,051 verses
the machine called clean found no further difference. Rulings R20 and R21 in
`RULINGS.md`.

**Pointing: four verses differ.** At 39:14 and 100:2 the book sets the colon on
a different word (*sojourner*, *ourselves*) and the mediant moves there. At
107:1 and 139:7 the book sets a semicolon where the mediant stands and no
colon anywhere in the verse; the cell keeps the repository's one structural
mediant ` : ` there and a flag records the book's mark. Every verse still
carries exactly one mediant.

**Punctuation: the carrier was keyed over the 1662 Psalter and carried its
stops.** 440 places where the page OCR and the cell disagreed were read by
eye; 328 were real differences, and ordinary punctuation now follows the book
(114 commas the book adds, 64 it lacks, 80 verse-final `:` or `;` where the
cell had `.`, 52 `;` for `,`, 14 other mid-verse marks, 3 capitals after a new
full stop). Non-mediant `:` and `;` are set closed up, as every other stop is;
only the mediant is spaced. One damaged stop (139:11) is flagged.

**Word forms and spacing.** An eye pass over the 725 words the alignment could
not match found 32 word forms Wave 17 had missed — carrier slips (*thou I
walk* 23:4, *more then* 52:4, *our* for *out* 22:7 and 68:31, *thy* for *they*
107:28 and 124:2, a *had* the book does not print 106:37) and 1662 spellings
where the book is modern (*rasor*, *musick*, *havock*, *cloke*, *intreated*,
*unperfect*, *unpatient*, *slipt*, *stablished*, and *strong hold* for the
book's *stronghold*, three times) — and 17 spacing slips. "THE END OF THE
PSALTER", which the carrier had fused into 150:6, is deleted as book
furniture (R20), as the 1928 and 1979 keyings' end markers were.

In all, 378 edits in 315 verses, every one an eye read with its scan page
(`ingest/w22_evidence.json`, 477 records; the eye record is
`ingest/w22_eye.txt`). The independent change log still agrees 55 of 55.

**Not taken, and recorded.** Letter case: the book and the cells differ in 94
places (small-capital LORD printed "Lord" sixteen times in Psalms 139–143;
the book capitalizing only the first word of a verse 1; *Most High*, *anointed*,
*Red Sea* and the like). They are eye-read, keyed and switched off pending a
ruling (`RULINGS.md`, open questions). The hyphen at 1:3 *water-side* stays
flagged: the book breaks the word at a line end, and a search of all 596 pages
finds no other occurrence.

---

'''

NOTICE = '''- **2026-10-16** — Wave 22: the **1892 Psalter, every mediant read by eye**.
  Wave 17 had checked the pointing only where a gate flagged it, because page
  OCR cannot tell `:` from `;`. This wave read the mediant of all 2,508 verses
  by eye off crops of the Standard Book scan, and the ordinary punctuation and
  unmatched words with it.
  - **Pointing**: four verses differ from the book; two mediants move to the
    book's word, two keep the repository's mark with a flag recording the
    book's semicolon (`RULINGS.md` R21).
  - **Punctuation**: the keyed carrier had carried the 1662 Psalter's stops;
    328 places now follow the book (commas, verse-final marks, `;` for `,`).
  - **Words**: 32 forms Wave 17 missed (*thou I walk*, *more then*, *our* for
    *out*, *rasor*, *cloke*, *strong hold* …) and 17 spacing slips; the closing
    line the keying had fused into 150:6 is deleted as furniture.
  - 378 edits in 315 verses, each an eye read with its page; 3 flags opened,
    none closed; letter case (94 differences) recorded and not changed, pending
    a ruling.
  - This changes `texts/original` and `texts/normalized` only at `v1892`
    (three files).

'''

ROWS = []
for (n, v), (key, note) in sorted(W.VERIFY.items()):
    ROWS.append((n, '| 1892 (American) Psalm %d | `%s` | %s |\n' % (n, key, note)))

EDITS = {
    'repo-root/SOURCES.md': [
        ("---\n\n## English line (`main`)", SECTION + "## English line (`main`)",
         '### The 1892 Psalter: the full pointing and punctuation collation (Wave 22)'),
        ("- **Not good:** punctuation at page-OCR resolution. `:` and `;` are not\n  reliably distinguished, so all seven pointing corrections were read by eye,\n  and **no** claim is made about the pointing of verses Wave 13's mediant gate\n  did not flag.",
         "- **Not good:** punctuation at page-OCR resolution. `:` and `;` are not\n  reliably distinguished, so all seven pointing corrections were read by eye,\n  and **no** claim was made about the pointing of verses Wave 13's mediant gate\n  did not flag — until Wave 22 read every mediant by eye (below).",
         "until Wave 22 read every mediant by eye"),
    ],
    'repo-root/NOTICE.md': [
        ("## A note on transcription", NOTICE + "## A note on transcription", "Wave 22: the **1892 Psalter, every mediant"),
    ],
    'repo-root/README.md': [
        ("The 1928 Psalter has been read against justus's scan of the original 1928 printing,",
         "The 1892 Psalter's pointing has been read in full: every one of its 2,508 mediants was read by eye off the Standard Book scan (four differ from the book), and the keying's borrowed 1662 punctuation now follows the book. "
         "The 1928 Psalter has been read against justus's scan of the original 1928 printing,",
         "The 1892 Psalter's pointing has been read in full"),
    ],
}


def main():
    for rel, pairs in EDITS.items():
        if rel == 'repo-root/SOURCES.md':
            p = os.path.join(WT, rel)
            s = open(p, encoding='utf-8').read()
            # the Wave-17 section's own caveat, if its exact text differs, is left alone
            pairs = [x for x in pairs if x[2] != "until Wave 22 read every mediant by eye" or s.count(x[0]) == 1]
        edit(rel, pairs)
    p = os.path.join(WT, 'repo-root/SOURCES.md')
    s = open(p, encoding='utf-8').read()
    if '| 1892 (American) Psalm 107 | `gracious :`' not in s:
        # replace the water-side row with the corrected note and add the three new rows after it
        m = re.search(r'^\| 1892 \(American\) Psalm 1 \| `water-side` \|.*\n', s, re.M)
        assert m, 'water-side row not found'
        s = s[:m.start()] + ''.join(r for _n, r in ROWS) + s[m.end():]
        open(p, 'w', encoding='utf-8').write(s)
    print('w22 docs: ok')


if __name__ == '__main__':
    main()
