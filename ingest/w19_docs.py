"""w19_docs.py — the Wave-19 edits to the published docs (SOURCES, NOTICE, README).

Rows for the sixteen flags this wave closed are deleted from SOURCES.md's
uncertain-passages tables by line match, and the wave's own section is added.
Every replacement must match exactly once; if one goes stale nothing is
written.
"""
import os
import re
import sys

WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECTION = """### The 1979 text against the publisher's own file (Wave 19)

Every 1979 cell in this repository is transcribed from justus's 1993 ASCII
e-text. Wave 19 read it against **Church Publishing Incorporated's own PDF of
the 1979 book**, from the Episcopal Church — Wikimedia Commons's
`File:Book of common prayer (TEC, 1979).pdf`, 1001 pages with an exact text
layer. The US Book of Common Prayer has never been under copyright, which the
publisher states and the Commons file page records. That is a witness of a
different *class* from a volunteer keying, so where the two disagree the
publisher's file is the book.

**What the witness cannot say.** Its text layer renders the book's small-capital
LORD as "Lord", so no letter-case is taken from it; and it drops the pointing
asterisk in about ten verses where every neighbour keeps it, so **no pointing is
changed on this witness**. Four more verses carry a stray mark that is plainly
an extraction artifact. Those fifteen verses are listed in
`ingest/w19_gates.py` and are the *only* places where the corrected Psalter
still differs from the file.

**The Psalter, collated verse by verse.** All 2,507 verses were parsed out of
the book and compared word for word — the first exact collation in this
repository, since both sides are text. It found **24 verses** whose words
differ, and the e-text is wrong in every one: *you Name* for *your Name*
(8:10), *this throne* for *his throne* (9:7), *the people* for *the peoples*
(9:17), *plowed* for *ploughed* (9:6), a dropped *shall* (22:26) and an extra
*who* (38:13), *to the grave* for *into the grave* (55:16), *to Edom* for
*into Edom* (60:9), *from of the clutches* (71:4), *winge!d* for *wingèd*
(78:27), *The grieved him … they provoked* for *They grieved him … and
provoked* (78:58), *and son of man* for *the son of man* (80:16), *Zee%b* for
*Zeëb* (83:11), *All the nations* for *All nations* (86:9), *in vision* for
*in a vision* (89:19), *the lion and the adder* for *the lion and adder*
(91:13), *Issac* for *Isaac* (105:9), *firstfruits* for *first fruits*
(105:36), *from everlasting to everlasting* for *from everlasting and to
everlasting* (106:48), *Hosanna* for *Hosannah* twice (118:25), *confort* for
*comfort* (119:52), *the kingdoms of Bashan … the kings of Canaan* for *the
king of Bashan … the kingdoms of Canaan* (135:11), and *winge!d* again
(148:10). At the end of Psalm 150 the keying's own end-of-file marker —
`(end of BCPSALTER.TXT)` — had been published as part of the last verse; it is
gone.

**Seventeen Latin incipits and three of Psalm 119's portion headings.** Nine
incipits had been truncated in the keying, each losing the same syllable
(*Laudate Domi*, *Voce mea ad Domi*, *Ad Domi*, *Benedicam Domi*, *Deus
ultio*); those were the nine VERIFYs Wave 13 raised, and all nine are closed.
The rest are the ligature the ASCII e-text could not carry (*Cæli enarrant*,
*Noli æmulari*, *Audite hæc*, *Notus in Judæa*, *Lætatus sum*, *Sæpe
expugnaverunt*, *Adhæsit pavimento*, *Manus tuæ fecerunt me*, *In æternum,
Domine*), one letter (*Misericordiam **et** judicium*) and one lost question
mark (*Deus, quis similis?*).

**Seven dropouts and typos elsewhere**, four of them flagged and three found by
reading the cells against the book: *fulfull* → *fulfill*; *Almighty god* →
*Almighty God*, *payer* → *prayer* and *Pleides* → *Pleiades* in Evening
Prayer; the Fifth Sunday of Easter's contemporary collect, which broke off at
"to be the way, t Amen.", restored in full, and its traditional collect's lost
opening *O*, *god* and *leads* for *leadeth*; both Annunciation collects' lost
stop before *Amen* and *to the glory* for *unto the glory*; the banns of
marriage, which had lost the clause "If any of you know just cause why they may
not be joined together in Holy Matrimony" and printed em dashes where the book
prints blanks to be filled in; the marriage Prayers, where "to which the People
respond, saying, **Amen.**" had collapsed into "saying, Am the ordering of
their common life", swallowing a rubric, the bidding and the first prayer; and
the adoption form, where "here assembled" had become "asbrant", swallowing a
sentence, a rubric, a question and two answers.

**What remains.** A survey of every other 1979 cell against the same file
(`ingest/w19_survey.py`) finds 94% of paragraphs verbatim outside the
lectionary tables — 89% in the propers, 93% in the daily office and holy
communion, 96–98% in the ordinal, the occasional offices and the prayers. The
~110 paragraphs that do not match are the next pass's candidates; some are
re-wrappings rather than defects. The lectionary tables match at 1.5% because
the repository renders them as long-form rows and the book prints them as
tables: comparing those needs a different method, not a closer reading.

---

"""

EDITS = {
    'repo-root/SOURCES.md': [
        ("---\n\n## English line (`main`)", SECTION + "## English line (`main`)"),
    ],
    'repo-root/README.md': [
        ("Progress and per-edition provenance are tracked in `SOURCES.md`.",
         "The 1979 text has been read against Church Publishing's own PDF of "
         "the book: the Psalter was collated verse by verse (24 verses and 20 "
         "Latin headings corrected) and seven dropouts and typos elsewhere "
         "were repaired, including two collects and two passages the 1993 "
         "keying had swallowed.\n\n"
         "Progress and per-edition provenance are tracked in `SOURCES.md`."),
    ],
    'repo-root/NOTICE.md': [
        ("## A note on transcription",
         """- **2026-09-18** — Wave 19: the **1979 text against the publisher's own
  file**. Every 1979 cell here comes from justus's 1993 ASCII e-text; this
  wave read it against Church Publishing Incorporated's own PDF of the book,
  from the Episcopal Church (Wikimedia Commons, 1001 pages with an exact text
  layer; the US Book of Common Prayer has never been under copyright, which
  the publisher states). A publisher's file and a volunteer keying are
  witnesses of different classes, so where they disagree the publisher's file
  is the book.
  - **The Psalter was collated verse by verse** — all 2,507 verses, the first
    exact collation in this repository, both sides being text. Twenty-four
    verses differ, and the keying is wrong in every one (*Issac* for *Isaac*,
    *confort* for *comfort*, *the people* for *the peoples*, a dropped
    *shall*, *winge!d* for *wingèd*, and so on). Seventeen Latin incipits and
    three of Psalm 119's portion headings are corrected too; the nine that had
    been truncated in the keying were Wave 13's nine open flags, and all nine
    are closed.
  - **The keying's own end-of-file marker** had been published as part of the
    last verse of Psalm 150. It is gone.
  - **Seven dropouts and typos elsewhere**, including a collect that broke off
    mid-word, the banns of marriage (which had lost a whole clause), the
    marriage Prayers and the adoption form (each of which had swallowed a
    rubric and more).
  - What the witness cannot settle is recorded: its text layer renders the
    book's small-capital LORD as "Lord" and drops the pointing asterisk in
    about ten verses, so no letter-case and no pointing is taken from it.
  - This changes `texts/original` and `texts/normalized` throughout the 1979
    Psalter and in six other 1979 files.

## A note on transcription"""),
    ],
}

# Rows in the uncertain-passages tables whose flags this wave closed.
DROP_ROWS = [
    '| 1979 Matrimony | `Am the ordering of their common life` |',
    '| 1979 Matrimony | `you are bidden to declare it` |',
    '| 1979 Churching | `asbrant` |',
    '| 1979 Concerning the Service of the Church | `fulfull` |',
    '| 1979 annunciation | `The Annunciation` | the collect under `The Collect` breaks off',
    '| 1979 annunciation | `The Annunciation` | the collect under `The Collect (Contemporary)` breaks off',
    '| 1979 easter-4 | `Fifth Sunday of Easter` | the collect under `The Collect (Contemporary)` breaks off',
    '| 1979 (American) Psalm 34 | `Benedicam Domi` |',
    '| 1979 (American) Psalm 77 | `Voce mea ad Domi` |',
    '| 1979 (American) Psalm 94 | `Deus ultio` |',
    '| 1979 (American) Psalm 117 | `Laudate Domi` |',
    '| 1979 (American) Psalm 120 | `Ad Domi` |',
    '| 1979 (American) Psalm 142 | `Voce mea ad Domi` |',
    '| 1979 (American) Psalm 147 | `Laudate Domi` |',
    '| 1979 (American) Psalm 148 | `Laudate Domi` |',
    '| 1979 (American) Psalm 150 | `Laudate Domi` |',
]


def main():
    stale, done = [], 0
    texts = {rel: open(os.path.join(WT, rel), encoding='utf-8').read()
             for rel in EDITS}
    src = texts['repo-root/SOURCES.md']
    kept = []
    dropped = 0
    for line in src.split('\n'):
        if any(line.startswith(p) for p in DROP_ROWS):
            dropped += 1
            continue
        kept.append(line)
    if dropped != len(DROP_ROWS):
        stale.append('SOURCES.md: dropped %d rows, expected %d'
                     % (dropped, len(DROP_ROWS)))
    texts['repo-root/SOURCES.md'] = '\n'.join(kept)
    done += dropped
    for rel, subs in EDITS.items():
        t = texts[rel]
        for old, new in subs:
            if t.count(old) != 1:
                stale.append('%s: %d matches for %r' % (rel, t.count(old), old[:60]))
                continue
            t = t.replace(old, new)
            done += 1
        texts[rel] = t
    if stale:
        print('STALE (nothing written):')
        for s in stale:
            print('  ' + s)
        sys.exit(1)
    for rel, t in texts.items():
        open(os.path.join(WT, rel), 'w', encoding='utf-8').write(t)
    print('w19_docs: %d edits in %d files' % (done, len(texts)))


if __name__ == '__main__':
    main()
