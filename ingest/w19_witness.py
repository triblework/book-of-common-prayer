"""w19_witness.py — the 1979 text corrected against the publisher's own file.

THE WITNESS. *The Book of Common Prayer* (1979) as Church Publishing
Incorporated's own PDF, from the Episcopal Church, served by Wikimedia Commons
(`File:Book of common prayer (TEC, 1979).pdf`, 1001 pages, 4,911,934 bytes,
sha256 d4552eb3..., producer "Acrobat PDFWriter 3.0f1r8 for Power Macintosh").
The US Book of Common Prayer has never been under copyright; the publisher
says so and the Commons file page records it.

THE CARRIER is justus's 1993 ASCII e-text, which every 1979 cell in this repo
comes from. The witness is therefore of a different CLASS -- the publisher's
own typesetting against a volunteer keying -- so R6 is satisfied, and where
they disagree the publisher's file is the book.

WHAT THE WITNESS CAN AND CANNOT SAY. Its text layer is exact, so unlike Waves
17-18 there is no OCR to doubt: words, spellings and Latin incipits are all
readable. Two things it cannot testify about:
  * SMALL CAPITALS. The book prints the divine Name as LORD in small capitals;
    the text layer renders that as "Lord". No case change is taken from it.
  * THE MEDIANT. The asterisk that divides a pointed verse is dropped by the
    extractor in about ten verses (33:16, 34:3, 40:16, 71:21, 83:16, 83:17,
    105:21, 105:22, 107:28, and 144:15 where it comes out as a dash), while
    every neighbouring verse keeps it. That is extraction noise, not the book
    losing its pointing, so NO pointing is changed on this witness.
Three verses (40:11, 65:11, 119:166) carry a stray "I" in the text layer and
69:18 a stray quotation mark; those are artifacts too, and are ignored.
"""
import re

# --- the Psalter: verse readings ---------------------------------------
# (psalm, verse): (what the e-text prints, what the book prints). Each must
# match exactly once in that verse.
VERSES = {
    (8, 10): ('exalted is you Name in', 'exalted is your Name in'),
    (9, 6): ('their cities plowed under', 'their cities ploughed under'),
    (9, 7): ('set up this throne for', 'set up his throne for'),
    (9, 17): ('all the people that forget', 'all the peoples that forget'),
    (22, 26): ('the nations bow before', 'the nations shall bow before'),
    (38, 13): ('mute and who do not', 'mute and do not'),
    (55, 16): ('down alive to the grave', 'down alive into the grave'),
    (60, 9): ('bring me to Edom', 'bring me into Edom'),
    (71, 4): ('from of the clutches', 'from the clutches'),
    (78, 27): ('and winge!d birds like', 'and wingèd birds like'),
    # the source's own mediant mark is "*"; the cell prints " : " only after
    # w13_render normalizes it, so these fragments carry the asterisk
    (78, 58): ('The grieved him with their hill-altars * they provoked',
               'They grieved him with their hill-altars * and provoked'),
    (80, 16): ('and son of man you', 'the son of man you'),
    (83, 11): ('Oreb and Zee%b', 'Oreb and Zeëb'),
    (86, 9): ('All the nations you have made', 'All nations you have made'),
    (89, 19): ('once in vision and', 'once in a vision and'),
    (91, 13): ('lion and the adder', 'lion and adder'),
    (105, 9): ('swore to Issac', 'swore to Isaac'),
    (105, 36): ('the firstfruits of all', 'the first fruits of all'),
    (106, 48): ('from everlasting to everlasting',
                'from everlasting and to everlasting'),
    (118, 25): ('Hosanna, LORD, hosanna!', 'Hosannah, LORD, hosannah!'),
    (119, 52): ('take great confort', 'take great comfort'),
    (135, 11): ('Og, the kingdoms of Bashan, * and all the kings of Canaan',
                'Og, the king of Bashan, * and all the kingdoms of Canaan'),
    (148, 10): ('things and winge!d birds', 'things and winged birds'),
    # the 1993 keying's own end-of-file marker, published as psalm text
    (150, 6): ('Lord. Hallelujah! '
               '-------------------------(end of BCPSALTER.TXT)----------------',
               'Lord. Hallelujah!'),
}

# --- the Psalter: Latin incipits and Psalm 119's portion headings -------
# Nine incipits were truncated in the 1993 keying, all losing the same
# syllable -- those are the nine VERIFYs Wave 13 raised. The rest are the
# ligature the ASCII e-text could not carry, one letter ("ed" for "et") and
# one lost question mark. Keyed by the exact heading as the e-text prints it,
# with the number of psalms that print it, since four psalms share "Laudate
# Domi" and two share "Voce mea ad Domi". A psalm printed in parts, and Psalm
# 119, carry their headings on the first verse rather than on the psalm, so
# both places are corrected.
HEADINGS = {
    'Caeli enarrant': ('C\u00e6li enarrant', 1),
    'Benedicam Domi': ('Benedicam Dominum', 1),
    'Noli aemulari': ('Noli \u00e6mulari', 1),
    'Audite haec, omnes': ('Audite h\u00e6c, omnes', 1),
    'Notus in Judaea': ('Notus in Jud\u00e6a', 1),
    'Voce mea ad Domi': ('Voce mea ad Dominum', 2),
    'Deus, quis similis': ('Deus, quis similis?', 1),
    'Deus ultio': ('Deus ultionum', 1),
    'Misericordiam ed judicium': ('Misericordiam et judicium', 1),
    'Laudate Domi': ('Laudate Dominum', 4),
    'Ad Domi': ('Ad Dominum', 1),
    'Laetatus sum': ('L\u00e6tatus sum', 1),
    'Saepe expugnaverunt': ('S\u00e6pe expugnaverunt', 1),
    'Adhaesit pavimento': ('Adh\u00e6sit pavimento', 1),
    'Manus tuae fecerunt me': ('Manus tu\u00e6 fecerunt me', 1),
    'In aeternum, Domine': ('In \u00e6ternum, Domine', 1),
}


def apply(psalms, log=None):
    """Correct the parsed 1979 psalter in place. Every correction must fire
    the expected number of times; anything else is a stale reading and stops
    the build."""
    out = []
    for (n, v), (was, now) in sorted(VERSES.items()):
        verses = psalms[n]['verses']
        hits = [i for i, (num, text, _s) in enumerate(verses)
                if num == v and text.count(was) == 1]
        if len(hits) != 1:
            raise SystemExit('w19_witness: stale reading at Psalm %d:%d -- the '
                             'carrier no longer reads %r exactly once'
                             % (n, v, was))
        i = hits[0]
        num, text, sub = verses[i]
        verses[i] = (num, text.replace(was, now), sub)
        out.append(('verse', n, v, now))

    seen = {}
    for n in sorted(psalms):
        p = psalms[n]
        fix = HEADINGS.get((p.get('incipit') or '').strip())
        if fix:
            p['incipit'] = fix[0]
            p.pop('incipit_truncated', None)
            seen[p['incipit']] = seen.get(p['incipit'], 0) + 1
            out.append(('incipit', n, None, fix[0]))
        for i, (num, text, sub) in enumerate(p['verses']):
            if sub is None:
                continue
            subs = [sub] if isinstance(sub, str) else list(sub)
            new = [HEADINGS[s][0] if s in HEADINGS else s for s in subs]
            if new != subs:
                p['verses'][i] = (num, text,
                                  new[0] if isinstance(sub, str) else new)
                for s, t in zip(subs, new):
                    if s != t:
                        seen[t] = seen.get(t, 0) + 1
                        out.append(('heading', n, num, t))
    for was, (now, count) in sorted(HEADINGS.items()):
        if seen.get(now, 0) != count:
            raise SystemExit('w19_witness: expected %d headings reading %r, '
                             'corrected %d' % (count, was, seen.get(now, 0)))
    if log is not None:
        log.extend(out)
    return out


def introduced():
    """The words this wave adds to the 1979 Psalter that the e-text does not
    contain -- every one of them read off Church Publishing's own file and
    evidenced with its page in ingest/w19_evidence.json. w13_fidelity.py
    subtracts these, exactly as it does Wave 17's for 1892."""
    # the same tokenization w13_fidelity uses, so that "Adhæsit" is compared
    # as the two pieces that gate sees rather than as one word
    import w13_fidelity
    tok = lambda s: set(w.lower() for w in w13_fidelity.TOK.findall(s))
    out = set()
    for was, now in VERSES.values():
        out |= tok(now) - tok(was)
    for was, (now, _n) in HEADINGS.items():
        out |= tok(now) - tok(was)
    return out
