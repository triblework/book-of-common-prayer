"""w18_witness.py — what the Annexed Book shows, and the two corrections it warrants.

THE WITNESS. *The Book of Common Prayer ... from the original manuscript
attached to the Act of Uniformity of 1662*, Her Majesty's Printing Office,
September 1892: the manuscript annexed to the Act of Uniformity -- the book the
Convocations signed on 20 December 1661 and the legal standard of the 1662
text -- reproduced in type, "verbatim et literatim", after a word-by-word,
stop-by-stop comparison with the photographs from which the 1891 House of Lords
facsimile was made. Scanned by Google Books, served by Wikimedia Commons as
PD-US, 577 page images with an unusable text layer (it drops the spaces between
words and loses whole passages).

WHAT IT IS NOT. It is not one of the printed Sealed Books, and its own preface
says so plainly: the earliest printed copies "are found to differ considerably
from that original standard in various details of orthography and punctuation",
and the printers conclude that the MS was "intended to be a record of the
language only ... and not to be a standard of orthography". The carrier here is
a third thing again: the Church of England's currently authorized 1662 text, in
modern spelling. So this wave collates SUBSTANCE and STRUCTURE only. Spelling
is not collated in either direction -- the witness reads `vngodly`, `ioy`,
`shew`, `soveraign`, and Psalm 90:1 opens "O Lord thou hast been our refuge"
where the carrier has "Lord, thou hast been our refuge". Those are differences
between two printings, not errors in one of them, and NOTHING here rewrites the
carrier's orthography from the manuscript's.

WHAT IS CORRECTED. Two verses, both flagged by Wave 13 as open questions and
both settled: the carrier drops a mediant the 1662 text prints. The mediant is
a structural mark of the pointed Psalter, printed " : " in both books, so
restoring it imports no orthography.

WHAT THE RULING WAS. The Annexed Book names the King ("our most gracious
soveraign Lord King Charles") and leaves EVERY OTHER royal name a blank -- in
Morning Prayer, in Evening Prayer, in the Litany and in the Ordinal's litany,
with the title itself unfinished ("A Prayer for"). The carrier fills those
blanks with the living Royal Family. The maintainer ruled: print what the
original copies print, and where the original leaves a space, SHOW the space,
as a modern book does when it prints "N. ________". So the living names are
gone and the blank is set as "________" (w18_cells.py); nothing is
reconstructed into it, because what the printed Sealed Books named there is
unknown -- no scan of one is available on an allow-listed host. Under the same
ruling the Sea rubric's "her Majesty's Navy" becomes "his Majesty's Navy": the
book reads "also vsed in his Majesties Navy every day", and that is a word,
not a spelling.

WHAT IS STILL RECORDED AND NOT CHANGED. The communion admission rubric. What
the carrier prints there (an account to the Ordinary, seven days, an
opportunity for interview) is no part of the 1662 text -- the book prints the
"open and notorious evil liver" rubric of 1549-1604 -- but substituting it
would mean setting a paragraph of the manuscript's own orthography inside a
modernized cell, which is a different decision from showing a blank. Flagged
with what the page shows.
"""
import re

# --- the two corrections ------------------------------------------------
# (psalm, verse): (what the carrier prints, what it becomes). The witness
# prints a mediant at this point; the carrier prints none. Applied exactly
# once each, with a stale check -- if the carrier stops reading as recorded,
# the build fails rather than silently doing nothing.
POINTING = {
    (2, 12): ('from the right way, if his wrath',
              'from the right way : if his wrath'),
    (68, 1): ('be scattered let them also',
              'be scattered : let them also'),
}

# --- the readings this wave took, and what they settle -------------------
# kind:  'read'  a line read twice by machine and once by eye
#        'blank' the page leaves a blank where the carrier prints names
# `expect` must appear in the second read; for 'blank' items it must NOT.
ITEMS = [
    dict(id='ps-2-12', page=346, kind='read',
         needle='Kiss the son lest he be angry and so ye perish from the',
         expect='way :', span=3,
         says='Psalm 2:12 is pointed: "from the [right] way : if his wrath be '
              'kindled". The carrier prints no mediant here.'),
    dict(id='ps-68-1', page=413, kind='read',
         needle='Let God arise and let his enemies be scattered let them also',
         expect='scattered :', span=2,
         says='Psalm 68:1 is pointed: "let his enemies be scattered : let them '
              'also that hate him flee before him". The carrier prints no '
              'mediant here.'),
    dict(id='ps-89-50', page=443, kind='read',
         needle='Wherewith thine enemies have blasphemed thee and slandered the footsteps',
         expect='anointed : praised be the Lord for evermore', span=5,
         says='The doxology that closes Book III stands INSIDE verse 50, after '
              'a single mediant, and Psalm 90 follows at once: there is no '
              'verse 51. The carrier is right and Wave 13\'s doubt is closed.'),
    dict(id='king-mp', page=70, kind='read',
         needle='favour to behold our most gracious soveraign Lord King Charles',
         expect='King Charles', box=(890, 380, 620, 1720),
         says='Morning Prayer prays for "our most gracious soveraign Lord King '
              'Charles": the first name the carrier prints is period-correct.'),
    dict(id='king-litany', page=86, kind='read',
         needle='in the true worshipping of thee in righteousnes and holines of life',
         expect='thy servant Charles', span=3,
         says='The Litany prays for "thy servant Charles our most gracious King '
              'and Governour".'),
    dict(id='king-communion', page=254, kind='read',
         needle='and specially thy servant Charles our King that under him we may be',
         expect='thy servant Charles our King', span=2,
         says='The prayer for the Church Militant prays for "thy servant '
              'Charles our King".'),
    dict(id='king-ordinal', page=526, kind='read',
         needle='in the true worshipping of thee in righteousnes and holinesse of life',
         expect='Charles', box=(2830, 380, 330, 1700),
         says='The Ordinal\'s litany prays for "thy servant Charles our most '
              'gratious King and Governour".'),
    dict(id='royal-mp', page=70, kind='blank',
         needle='Almighty God the fountain of all goodnes we humbly beseech thee to bless',
         expect='Royal', span=3,
         says='Morning Prayer: the title reads "A Prayer for" and stops, and '
              'the prayer reads "we humbly beseech thee to bless" and stops. '
              'Two blank lines follow before "Indue them with thy holy '
              'spirit". No royal person but the King is named.'),
    dict(id='royal-ep', page=80, kind='blank',
         needle='Almighty God the fountaine of all goodness we humbly beseech thee to bless',
         expect='Royal', span=3,
         says='Evening Prayer prints the same unfinished title and the same '
              'blank after "to bless".'),
    dict(id='royal-litany', page=87, kind='blank',
         needle='That it may please thee to blesse and preserve',
         expect='Queen', span=2,
         says='The Litany petition reads "That it may please thee to blesse '
              'and preserve" and stops; the response follows after a blank.'),
    dict(id='royal-ordinal', page=527, kind='blank',
         needle='That it may please thee to bless and preserve',
         expect='Queen', span=2,
         says='The Ordinal\'s litany prints the same petition and the same '
              'blank.'),
    dict(id='communion-rubric', page=246, kind='read',
         needle='And if any of those be an open and notorious evil liver or have done any wrong',
         expect='notorious evil', span=3,
         says='The 1662 admission rubric is the "open and notorious evil liver" '
              'rubric of 1549-1604. The rubric the carrier prints -- an account '
              'to the Ordinary, an opportunity for interview, seven days -- is '
              'not in the Annexed Book at all; it is a later amendment.'),
    dict(id='baptism-forasmuch', page=277, kind='read',
         needle='Forasmuch as this childe hath promised by you his sureties to renounce',
         expect='Forasmuch as this', span=2,
         says='The exhortation to the Godfathers reads "Forasmuch as this '
              'childe hath promised"; the private form on page 283 reads '
              '"Forasmuch as this child", and the opening exhortation on page '
              '271 "Dearly beloved, forasmuch as all men are conceived". The '
              'carrier\'s "Foreasmuch" is an orthographic difference of exactly '
              'the kind the witness\'s own preface disclaims -- the MS "is not '
              'to be a standard of orthography" and the printed books differ '
              'from it -- so it is left as the Church of England prints it, '
              'and the flag now records what was checked instead of asking for '
              'a scan.'),
    dict(id='sea-psalm-107', page=513, kind='read',
         needle='Let them give thanks whom the Lord hath redeemed and delivered from the hand',
         expect='thanks', span=2,
         says='At Sea, where one psalm is used the book labels it in the '
              'margin -- "Confitemini Domino. Psal. 107." -- and where the '
              'office uses a cento ("A Hymn of praise and thanksgiving after a '
              'dangerous tempest", page 517) it prints no psalm label at all. '
              'The carrier\'s missing citation is the book\'s own silence.'),
    dict(id='sea-navy', page=508, kind='read',
         needle='following Prayers are to be also used in His Majesties Navy every day',
         expect='Majesties Navy', box=(1270, 540, 320, 1540),
         says='The rubric reads "in his Majesties Navy". The carrier prints '
              '"her Majesty\'s Navy" -- a reign-dependency the Church of '
              'England source has not updated, in the same file that prays for '
              '"King CHARLES".'),
]


def apply(psalms, log=None):
    """Insert the two attested mediants into the parsed 1662 psalter.

    `psalms` is w13_1662.parse()'s structure: {n: {"verses": [(num, text,
    sub), ...]}}. Each correction must fire exactly once; anything else is a
    stale reading and stops the build rather than silently doing nothing.
    """
    out = []
    for (n, v), (was, now) in sorted(POINTING.items()):
        verses = psalms[n]['verses']
        hits = [i for i, (num, text, _sub) in enumerate(verses)
                if num == v and text.count(was) == 1]
        if len(hits) != 1:
            raise SystemExit(
                'w18_witness: stale reading at Psalm %d:%d -- the carrier no '
                'longer reads %r exactly once' % (n, v, was))
        i = hits[0]
        num, text, sub = verses[i]
        verses[i] = (num, text.replace(was, now), sub)
        out.append(('pointing', n, v, now))
    if log is not None:
        log.extend(out)
    return out


def introduced():
    """The words this wave adds to the carrier: none. The corrections insert a
    mediant and its spaces, so the fidelity gate needs no exemption."""
    added = set()
    for was, now in POINTING.values():
        added |= (set(re.findall(r"[A-Za-z']+", now))
                  - set(re.findall(r"[A-Za-z']+", was)))
    return added
