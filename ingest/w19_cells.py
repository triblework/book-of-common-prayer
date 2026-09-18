"""w19_cells.py — the Wave-19 edits to the hand-authored 1979 cells.

The Psalter is written by w13_build_1979.py (which applies w19_witness); these
six cells are structured files, so their corrections are made here, file to
file, and each replacement must match exactly once or nothing is written.

Everything here is a defect in justus's 1993 ASCII keying, read against Church
Publishing's own PDF of the book (w19_witness_text.py). Four of them were
already flagged; the other three were found by reading the cells against the
book:

  concerning-the-service  "fulfull"      -> "fulfill"            (flagged)
  evening-prayer          "Almighty god" -> "Almighty God", "payer" ->
                          "prayer", "Pleides" -> "Pleiades"      (found)
  easter-4                the contemporary collect breaks off at "to be the
                          way, t Amen." -- the rest is restored  (flagged);
                          and its traditional collect loses the opening "O",
                          reads "god", and has "leads" for "leadeth" (found)
  annunciation            both collects lose the stop before "Amen", and the
                          traditional one reads "to the glory" for "unto the
                          glory"                                 (flagged)
  matrimony               the banns lose the clause "If any of you know just
                          cause why they may not be joined together in Holy
                          Matrimony", and print em dashes where the book
                          prints blanks to be filled in            (flagged);
                          and The Prayers lose a rubric, the bidding and the
                          first prayer, collapsing "saying, Amen." into
                          "saying, Am the ordering of their common life"
                                                                   (flagged)
  churching               the adoption form loses a sentence, a rubric, a
                          question and two answers, collapsing "here
                          assembled" into "asbrant"; and "wwe" for "we"
                                                                  (flagged)

The restored passages are set in the book's own spacing (one space after a
stop), not the e-text's two, and follow the repo's conventions for rubrics
(`> `) and speaker labels (`**Label.**`).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)

EASTER4_TRAD_OLD = (
    'Almighty god, whom truly to know is everlasting life: Grant us so '
    'perfectly to know thy Son Jesus Christ to be the way, the truth, and the '
    'life, that we may steadfastly follow his steps in the way that leads to '
    'eternal life; through the same thy Son Jesus Christ our Lord, who liveth '
    'and reigneth with thee, in the unity of the Holy Spirit, one God, for '
    'ever and ever. Amen.')
EASTER4_TRAD_NEW = (
    'O Almighty God, whom truly to know is everlasting life: Grant us so '
    'perfectly to know thy Son Jesus Christ to be the way, the truth, and the '
    'life, that we may steadfastly follow his steps in the way that leadeth '
    'to eternal life; through the same thy Son Jesus Christ our Lord, who '
    'liveth and reigneth with thee, in the unity of the Holy Spirit, one God, '
    'for ever and ever. Amen.')
EASTER4_CONT_OLD = (
    'Almighty god, whom truly to know is everlasting life: Grant us so '
    'perfectly to know your Son Jesus Christ to be the way, t Amen.')
EASTER4_CONT_NEW = (
    'Almighty God, whom truly to know is everlasting life: Grant us so '
    'perfectly to know your Son Jesus Christ to be the way, the truth, and '
    'the life, that we may steadfastly follow his steps in the way that leads '
    'to eternal life; through Jesus Christ your Son our Lord, who lives and '
    'reigns with you, in the unity of the Holy Spirit, one God, for ever and '
    'ever. Amen.')

BANNS_OLD = ('I publish the Banns of Marriage between N. N.. of — and '
             'N. N.. of — in Holy Matrimony, you are bidden to declare '
             'it.  This is the first (or second, or third) time of asking.')
BANNS_NEW = ('I publish the Banns of Marriage between N.N. of ____________ '
             'and N. N. of ___________ . If any of you know just cause why '
             'they may not be joined together in Holy Matrimony, you are '
             'bidden to declare it. This is the first (or second, or third) '
             'time of asking.')

PRAYERS_OLD = (
    'The Deacon or other person appointed reads the following prayers, to '
    'which the People respond, saying, Am the ordering of their common life, '
    'that each may be to the other a strength in need, a counselor in '
    'perplexity, a comfort in sorrow, and a companion in joy.  Amen.')
PRAYERS_NEW = (
    '> The Deacon or other person appointed reads the following prayers, to '
    'which the People respond, saying, Amen.\n'
    '\n'
    '> If there is not to be a Communion, one or more of the prayers may be '
    'omitted.\n'
    '\n'
    'Let us pray.\n'
    '\n'
    'Eternal God, creator and preserver of all life, author of salvation, and '
    'giver of all grace: Look with favor upon the world you have made, and '
    'for which your Son gave his life, and especially upon this man and this '
    'woman whom you make one flesh in Holy Matrimony. Amen.\n'
    '\n'
    'Give them wisdom and devotion in the ordering of their common life, that '
    'each may be to the other a strength in need, a counselor in perplexity, '
    'a comfort in sorrow, and a companion in joy. Amen.\n')


ADOPTION_OLD = (
    'member of their family.  But first, our friends wish us, here asbrant, '
    'holding or taking the child by the hand, gives the child to the mother '
    'or father, saying')
ADOPTION_NEW = (
    'member of their family.  But first, our friends wish us, here assembled, '
    'to witness the inauguration of this new relationship.\n'
    '\n'
    '> The Celebrant asks the parent or parents\n'
    '\n'
    'N. [and N.], do you take this child for your own?\n'
    '\n'
    '**Parent(s).** I do.\n'
    '\n'
    '> Then if the child is old enough to answer, the Celebrant asks\n'
    '\n'
    'N., do you take this woman as your mother?\n'
    '\n'
    '**Child.** I do.\n'
    '\n'
    '**Celebrant.** Do you take this man as your father?\n'
    '\n'
    '**Child.** I do.\n'
    '\n'
    '> Then the Celebrant, holding or taking the child by the hand, gives the '
    'child to the mother or father, saying\n')

# VERIFY comments to delete, named by a phrase that occurs in exactly one of
# them, so the wording of the flag never has to be transcribed here.
DROP = [
    ('editions/1979/front-matter/concerning-the-service.md', "'fulfull'"),
    ('editions/1979/collects-epistles-gospels/easter-4.md',
     'breaks off mid-sentence'),
    ('editions/1979/collects-epistles-gospels/annunciation.md',
     'under `The Collect` breaks off'),
    ('editions/1979/collects-epistles-gospels/annunciation.md',
     'under `The Collect (Contemporary)` breaks off'),
    ('editions/1979/occasional-offices/matrimony.md',
     "'you are bidden to declare it'"),
    ('editions/1979/occasional-offices/matrimony.md',
     "'Am the ordering of their common life'"),
    ('editions/1979/occasional-offices/churching.md', "'asbrant'"),
]

EDITS = {
    'editions/1979/front-matter/concerning-the-service.md': [
        ('deacons, fulfull the functions', 'deacons, fulfill the functions'),
    ],
    'editions/1979/daily-office/evening-prayer.md': [
        ('presence of Almighty god our heavenly Father',
         'presence of Almighty God our heavenly Father'),
        ('Let my payer be set forth', 'Let my prayer be set forth'),
        ('made the Pleides and Orion', 'made the Pleiades and Orion'),
    ],
    'editions/1979/collects-epistles-gospels/easter-4.md': [
        (EASTER4_TRAD_OLD, EASTER4_TRAD_NEW),
        (EASTER4_CONT_OLD, EASTER4_CONT_NEW),
    ],
    'editions/1979/collects-epistles-gospels/annunciation.md': [
        ('passion be brought to the glory of his resurrection; who liveth',
         'passion be brought unto the glory of his resurrection; who liveth'),
        ('one God, now and for ever Amen.\n\n## The Collect (Contemporary)',
         'one God, now and for ever. Amen.\n\n## The Collect (Contemporary)'),
        ('who lives and reigns with you, in the unity of the Holy Spirit, one '
         'God, now and for ever Amen.',
         'who lives and reigns with you, in the unity of the Holy Spirit, one '
         'God, now and for ever. Amen.'),
    ],
    'editions/1979/occasional-offices/matrimony.md': [
        (BANNS_OLD, BANNS_NEW),
        (PRAYERS_OLD, PRAYERS_NEW),
    ],
    'editions/1979/occasional-offices/churching.md': [
        (ADOPTION_OLD, ADOPTION_NEW),
        ('that wwe may live together', 'that we may live together'),
    ],
}


VERIFY_RE = None


def drop_flag(text, phrase):
    """Delete the one VERIFY comment containing `phrase`, and the blank line
    that follows it."""
    import re
    hits = [m for m in re.finditer(r'<!-- VERIFY.*?-->\n?\n?', text, re.S)
            if phrase in m.group(0)]
    if len(hits) != 1:
        return None
    m = hits[0]
    return text[:m.start()] + text[m.end():]


def main():
    stale, done = [], 0
    files = {rel: open(os.path.join(WT, rel), encoding='utf-8').read()
             for rel in set(list(EDITS) + [r for r, _ in DROP])}
    for rel, phrase in DROP:
        got = drop_flag(files[rel], phrase)
        if got is None:
            stale.append('%s: not exactly one VERIFY containing %r'
                         % (rel, phrase))
        else:
            files[rel] = got
            done += 1
    for rel, subs in sorted(EDITS.items()):
        text = files[rel]
        for old, new in subs:
            if text.count(old) != 1:
                stale.append('%s: %d matches for %r'
                             % (rel, text.count(old), old[:70]))
                continue
            text = text.replace(old, new)
            done += 1
        files[rel] = text
    if not stale:
        for rel, text in files.items():
            open(os.path.join(WT, rel), 'w', encoding='utf-8').write(text)
    if stale:
        print('STALE (nothing written):')
        for s in stale:
            print('  ' + s)
        sys.exit(1)
    print('w19_cells: %d edits in %d files' % (done, len(files)))


if __name__ == '__main__':
    main()
