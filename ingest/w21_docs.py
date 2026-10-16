"""w21_docs.py -- Wave 21's edits to the published SOURCES.md, NOTICE.md and
README.md. Idempotent (each edit checks for its own marker); every
replacement must match exactly once or nothing is written. Run after
w13_build.py and gen_wave21_provenance.py."""
import os, re, sys
WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WT, 'ingest'))
import w21_witness as W


def edit(rel, pairs):
    p = os.path.join(WT, rel)
    s = open(p, encoding='utf-8').read()
    for old, new, marker in pairs:
        if marker in s or (new == '' and old not in s):
            continue
        assert s.count(old) == 1, (rel, old[:70], s.count(old))
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)


SECTION = '''### The 1928 Psalter against the original printing (Wave 21)

Wave 13 transcribed the 1928 Psalter from justus's `1928/Psalms{1,2,3}.htm`
(a keying). Wave 21 read it against **two page scans**, and the rulings that
govern which is the witness are R19 and R20 in `RULINGS.md`:

- **The witness: `1928/BCP1929.pdf`** — the "Cambridge Edition" (The Old
  Corner Book Store, Boston), certified in 1929 by the Custodian of the
  Standard Book against a certified copy of it: the original 1928 printing,
  with the original pagination (Calendar at p. xxix). 319 two-page JPX
  spreads; the Psalter is book pp. 345–525.
- **A second witness within limits: `1928Standard/1952std.pdf`** — justus's
  "complete 1952 facsimile edition". Its own front matter (read first, R7)
  shows what it is: Seabury Press, 1952, a Meriden Gravure facsimile of
  Updike's Standard Book, certified by the Custodian as conforming to the
  Standard Book "as amended by subsequent actions of General Conventions". It
  carries the 1945 lectionary and the 1936 pagination after the Psalter, and
  on the page before the Psalter prints Good Friday 22:1–19 where the original
  prints 1–9. So it is the Standard Book as amended to 1952, independently
  typeset, and it cannot by itself say what 1928 printed. It **corroborates**
  where both printings agree, and it **settles a compound the 1929 printing
  breaks at a line end** (1:3 *water-side*, 80:10 *cedar-trees*, 104:17
  *fir-trees*, 139:1 *up-rising*); where the printings disagree, the cell
  keeps the Standard Book reading and the difference is recorded, never
  imported.
- `1928Standard/bcp1928std.pdf` is a 2005 InDesign re-setting in Kis BT: a
  keying, not a witness.

**Method.** Every page of the Psalter in both scans was rendered at 4400px and
read with macOS Vision, each book page of a spread cropped and read on its
own; every verse was aligned to both scans on a skeleton of its words (2,477
of 2,508 placed on the 1929 scan, 2,443 on the facsimile; the rest were
drop-capital openings, cropped whole and read); every mediant was resolved on
both scans; and every cell word the page OCR did not attest, and every scan
word the cell lacked, was read twice by machine and, where that did not settle
it, by eye off the crop (323 eye readings on 268 places,
`ingest/w21_eye.txt`, `ingest/w21_evidence.json`).

**Seventeen corrections**: the three verses Wave 13 flagged as unpointed are
pointed in both printings (18:28, 109:21 — where the keying's `~` stood for
the asterisk — and 119:1), so those three flags are closed; `LORDd` (29:4) and
two missing spaces (12:1, 20:9) are keying slips; ten compounds the keying
closes are hyphenated by the book within a line (*cheek-bone*, *us-ward*,
*by-word*, *out-goings*, *mercy-seat*, *day-time*, *seven-fold*,
*loving-kindness*, *hoar-frost*, *up-rising*); and "The End of the Psalter.",
which the keying had fused into 150:6, is deleted as book furniture (R20), as
the 1979 keying's end-of-file marker was in Wave 19.

**The two printings differ in ten places, and the keyed carrier agrees with
the 1952 Standard Book in all ten** — so justus's text was keyed from a
Standard-conformant printing, not from the 1929 one (as Wave 15 found for the
tables). Seven are plain slips of the 1929 printing (*being* for *bring*
37:38, *thanskgiving* 69:31 and 116:15, a dropped letter after a drop capital
119:25, and three missing asterisks, 18:10, 73:20, 123:2); one is a comma
(37:20); two are readings — *while* for *whilst* (32:3) and *old* for *own*
(55:14) — and those two are flagged inline. A single printing's slip is not
the edition's reading (R19). Five compounds broken at a line end in **both**
printings keep the carrier's form and are flagged (35:13, 50:9, 78:27, 81:17,
103:8).

**What this does not claim.** Ordinary punctuation was not collated (page OCR
cannot tell `:` from `;`); no reading depends on the scans' own OCR layers;
and the 1979 Psalter, read against the publisher's text in Wave 19, is the
only American psalter not read against a page scan.

---

'''

ROWS = {}
for n, v, key, note in W.NEW_VERIFIES:
    ROWS[key] = '| 1928 (American) Psalm %d | `%s` | %s |\n' % (n, key, note)

OLD_ROWS = [
    "| 1928 (American) Psalm 18 | `no mediant` | the justus 1928 text prints this verse without its asterisk; the 1662 text has a mediant here. Carried as justus prints it. Confirm against a 1928 scan |\n",
    "| 1928 (American) Psalm 109 | `no mediant` | the justus 1928 text prints this verse without its asterisk; the 1662 text has a mediant here. Carried as printed. Confirm against a 1928 scan |\n",
    "| 1928 (American) Psalm 119 | `no mediant` | the justus 1928 text prints the first verse of Psalm 119 without its asterisk; the 1662 text has a mediant here. Carried as printed. Confirm against a 1928 scan |\n",
]

NOTICE = '''- **2026-10-16** — Wave 21: the **1928 Psalter, read against the original
  printing**. Wave 13 transcribed it from a keying; this wave read every verse
  against justus's scan of the 1928 book as first printed (`1928/BCP1929.pdf`,
  the Cambridge Edition certified against the Standard Book), with the 1952
  facsimile of the Standard Book as a second witness within limits — its own
  certificate shows it to be the text *as amended* to 1952, so it corroborates
  and settles line-end hyphens but never overrules (`RULINGS.md` R19).
  - **Seventeen corrections** in three files: the mediant restored in the three
    verses Wave 13 had flagged (both printings point them), a keying slip
    (`LORDd`), two missing spaces, ten compounds the book hyphenates
    (*cheek-bone*, *loving-kindness*, …), and "The End of the Psalter." deleted
    from the last verse, where the keying had fused it.
  - **Ten printing differences recorded, none imported**: the keyed text
    agrees with the 1952 Standard Book in all ten, so it was keyed from a
    Standard-conformant printing; two real readings (*whilst*/*while* 32:3,
    *own*/*old* 55:14) are flagged inline, the rest are slips of the 1929
    printing and are noted in `SOURCES.md`.
  - Flags: 3 closed, 7 opened (the two readings above and five compounds broken
    at a line end in both printings). Every verse still carries exactly one
    mediant.
  - This changes `texts/original` and `texts/normalized` only at `v1928`
    (three files).

'''

EDITS = {
    'repo-root/SOURCES.md': [
        ("---\n\n## English line (`main`)", SECTION + "## English line (`main`)",
         '### The 1928 Psalter against the original printing (Wave 21)'),
        ("settle. The 1928 and 1979 Psalters remain unread against any scan.",
         "settle. The 1979 Psalter remains unread against any page scan; the 1928\nPsalter was read against two in Wave 21 (below).",
         "the 1928\nPsalter was read against two in Wave 21"),
        # the 1929 Scottish row named the wrong file (found by the Wave-21 justus survey)
        ("The justus full-book PDF (`Scottish_BCP1929.pdf`) is an image/OCR scan and was **not** used for text.",
         "The justus full-book PDF (`Scotland/BCP1929.pdf`, PDF graphics of a c.1950 printing) was **not** used for text; `Scottish_BCP1929.pdf`, linked beside it, is A. C. Don's short history of the book, not the book.",
         "A. C. Don's short history"),
    ] + [(r, '', 'WAVE21-REMOVED') for r in OLD_ROWS],
    'repo-root/NOTICE.md': [
        ("## A note on transcription", NOTICE + "## A note on transcription", "Wave 21: the **1928 Psalter"),
    ],
    'repo-root/README.md': [
        ("The 1979 text has been read against Church Publishing's own PDF of the book:",
         "The 1928 Psalter has been read against justus's scan of the original 1928 printing, with the 1952 facsimile of the Standard Book as a second witness: the three verses the keying left unpointed are pointed in both, ten compounds take the book's hyphen, and the two places where the printings really differ are flagged rather than chosen. "
         "The 1979 text has been read against Church Publishing's own PDF of the book:",
         "The 1928 Psalter has been read against justus's scan"),
    ],
}


def main():
    for rel, pairs in EDITS.items():
        edit(rel, pairs)
    # the seven new verify rows go where the three old 1928 rows stood
    p = os.path.join(WT, 'repo-root/SOURCES.md')
    s = open(p, encoding='utf-8').read()
    if '| 1928 (American) Psalm 32 | `whilst`' not in s:
        anchor = "| 1979 (American) Eucharistic Lectionary | `Luke 12:13-21` |"
        i = s.index(anchor)
        j = s.index('\n', i) + 1
        order = [32, 35, 50, 55, 78, 81, 103]
        rows = ''.join(ROWS[k] for n in order for (pn, v, k, _n) in W.NEW_VERIFIES if pn == n)
        s = s[:j] + rows + s[j:]
        open(p, 'w', encoding='utf-8').write(s)
    print('w21 docs: ok')


if __name__ == '__main__':
    main()
