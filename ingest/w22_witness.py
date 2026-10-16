#!/usr/bin/env python3
"""w22_witness.py -- the 1892 Psalter's POINTING (and what the eye met beside
it) read against the Standard Book scan. Workstream C; authoring-only.

WITNESS  1892Standard/1892standard.pdf, scan pp. 357-536 (596-page bitonal
         scan of the 1892 Standard Book, subscribers' edition; no text layer).
CELLS    editions/1892/psalter/psalms-*.md at the branch base
         (710f635b7783f1e8188fa334ec75dca3e43a0220).

Every correction here was read by EYE off a 4400px crop (w22_eye.txt,
w22_punct.tsv, w22_words_eye.py); evidence per item in w22_evidence.json. OCR
found the places; it supplied nothing.

THE GROUPS, and the rulings that switch them (RULINGS R20, R21; maintainer
2026-10-16, Workstream C Phase 2):

  POINTING_MOVE  ON   the book's colon falls on a different word (R21; RN-3)
  POINTING_SEMI  ON, SEMI_MODE 'keep' -- the book prints ';' at the cell's
                 mediant and no colon in the verse: the cell keeps ' : ' and an
                 inline flag records the book's mark (R21; RN-2 option a).
                 Other modes, kept for the record: 'semi' -> ';' and no
                 mediant (needs MEDIANT_EXEMPT), 'both' -> '; :'
  WORDS          ON   word forms the book prints differently (RN-6, RN-7 b),
                      including those the eye pass over the unmatched words found
  PUNCT          ON   ordinary stops follow the book (R21; RN-4), keyed in
                      w22_punct_keys.json, plus PUNCT_EXTRA from the Phase-2 passes
  SPACING        ON   a space the cells set before a stop is closed up (R21:
                      only the mediant is spaced)
  FURNITURE      ON   "THE END OF THE PSALTER" deleted from 150:6 (R20)
  CASE_LORD      OFF  letter case -- NOT RULED (Phase 2 by-catch, RN-9):
  CASE_OPENING   OFF    small capitals LORD/GOD; the verse-1 opening's capitals;
  CASE_CAPS      OFF    other initial capitals. Keyed in w22_case_keys.json

Application (apply_text): every key is checked against the ORIGINAL verse --
it must occur there exactly once, else nothing is written for that verse and
the build stops -- and the edit is only the span where key and replacement
differ; all edits of a verse are applied together, right to left, and two
edits may not overlap. Nothing is ever replaced as a bare substring elsewhere.

NOT wired into w13_build_1892.py (Phase 2, after the rulings).
"""
from __future__ import annotations
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_EV = os.path.join(HERE, 'w22_evidence.json')
EVIDENCE = json.load(open(_EV, encoding='utf-8')) if os.path.exists(_EV) else {}

GROUPS = {'POINTING_MOVE': True, 'POINTING_SEMI': True, 'WORDS': True,
          'PUNCT': True, 'SPACING': True, 'FURNITURE': True,
          'CASE_LORD': False, 'CASE_OPENING': False, 'CASE_CAPS': False}
SEMI_MODE = 'keep'
MEDIANT_EXEMPT = set()        # (psalm, verse) printed with no mediant (SEMI_MODE 'semi')

# The book's colon on another word. (psalm, verse, [(key, replacement), ...])
POINTING_MOVE = [
    (39, 14, [('thee : and a sojourner, as', 'thee, and a sojourner : as')]),
    (100, 2, [('God : it is', 'God; it is'), ('ourselves; we', 'ourselves : we')]),
]

# ';' where the cell's mediant is, and no colon anywhere in the verse.
POINTING_SEMI = [
    (107, 1, 'gracious : and'),
    (139, 7, 'there : if'),
]
SEMI_NEW = {'keep': lambda k: k,
            'semi': lambda k: k.replace(' : ', '; '),
            'both': lambda k: k.replace(' : ', '; : ')}

# Word forms. (psalm, verse, key, replacement) -- the key is the cell's words.
WORDS = [
    (18, 15, 'springs of water', 'springs of waters'),
    (22, 18, 'casts lots', 'cast lots'),
    (23, 4, 'Yea, thou I', 'Yea, though I'),
    (32, 3, 'For while', 'For whilst'),
    (38, 16, 'foot slipped', 'foot slipt'),
    (48, 10, 'the daughters of', 'the daughter of'),
    (50, 20, 'Thou satest', 'Thou sattest'),
    (52, 3, 'sharp rasor', 'sharp razor'),
    (52, 4, 'more then', 'more than'),
    (71, 2, 'strong hold', 'stronghold'),
    (71, 20, 'of musick', 'of music'),
    (74, 9, 'make havock', 'make havoc'),
    (78, 21, 'the waters gushed', 'the water gushed'),
    (86, 9, 'thou hadst made', 'thou hast made'),
    (89, 39, 'strong holds', 'strongholds'),
    (91, 2, 'strong hold', 'stronghold'),
    (99, 1, 'so unpatient', 'so impatient'),
    (106, 10, 'the adversaries’ hand', 'the adversary’s hand'),
    (107, 28, 'when thy cry', 'when they cry'),
    (107, 40, 'evil intreated', 'evil entreated'),
    (109, 18, 'the cloke', 'the cloak'),
    (109, 28, 'a cloke', 'a cloak'),
    (112, 8, 'is established', 'is stablished'),
    (124, 2, 'when thy were', 'when they were'),
    (136, 12, 'stretched out arm', 'stretched-out arm'),
    (139, 15, 'being unperfect', 'being imperfect'),
    (144, 9, 'ten- stringed', 'ten-stringed'),
    # Phase 2: the eye pass over the words the alignment left unmatched
    (22, 7, 'shoot our their', 'shoot out their'),
    (68, 31, 'stretch our her', 'stretch out her'),
    (75, 9, 'full mixed', 'full mixt'),
    (106, 37, 'they had offered', 'they offered'),
    (109, 4, 'good will', 'goodwill'),
]

# Stops: generated by w22_punct_keys.py from the eye reads (w22_punct.tsv).
PUNCT = [(k['psalm'], k['verse'], k['old'], k['new'], k['id'])
         for k in json.load(open(os.path.join(HERE, 'w22_punct_keys.json'), encoding='utf-8'))]
# Phase 2: stops the eye passes found that no OCR flag had raised (id = the
# unmatched-word run whose crop showed it)
PUNCT_EXTRA = [
    (20, 9, 'LORD, and', 'LORD; and', 'U072'),
    (30, 1, 'LORD, for', 'LORD; for', 'U108'),
    (71, 1, 'rid me and', 'rid me, and', 'U279'),
    (81, 12, 'obey me.', 'obey me;', 'U327'),
]
PUNCT = PUNCT + PUNCT_EXTRA

# ' ;' set with a space in the cells (the carrier's, and Wave 17's 77:18).
SPACING = [
    # Phase 2: ' ,' and ' .' the cells carry from the carrier (um_fix_00), and
    # one missing space after a comma (139:1, um_24)
    (9, 8, 'people .', 'people.'),
    (12, 4, 'speak , who', 'speak, who'),
    (28, 10, 'them , and', 'them, and'),
    (31, 10, 'LORD , for', 'LORD, for'),
    (45, 5, 'truth , of', 'truth, of'),
    (55, 16, 'them , and', 'them, and'),
    (71, 1, 'THEE ,O', 'THEE, O'),
    (118, 26, 'luck , ye', 'luck, ye'),
    (124, 6, 'delivered .', 'delivered.'),
    (137, 8, 'Babylon , wasted', 'Babylon, wasted'),
    (139, 1, 'LORD,thou', 'LORD, thou'),
    (27, 1, 'salvation ; whom', 'salvation; whom'),
    (27, 16, 'heart ; and', 'heart; and'),
    (77, 2, 'season ; my', 'season; my'),
    (77, 18, 'ground ; the', 'ground; the'),
    (107, 10, 'iron ;', 'iron;'),
    (143, 12, 'soul ; for', 'soul; for'),
]

# R20: book furniture fused into the last verse by the carrier.
FURNITURE = [
    (150, 6, ' THE END OF THE PSALTER', ''),
]

# Letter case (NOT RULED; groups off): generated by w22_case_keys.py.
CASE = [(k['psalm'], k['verse'], k['old'], k['new'], k['id'], k['group'])
        for k in json.load(open(os.path.join(HERE, 'w22_case_keys.json'), encoding='utf-8'))]

# Not corrected, carried as inline flags (the coordinator generates provenance).
# One per verse; w13_build_1892 sets them under the verse, as Wave 17's.
VERIFY = {
    (1, 3): ('water-side',
             "the 1892 Standard Book scan breaks this word across a line "
             "(\"water-\" / \"side\", scan p. 357), and a search of all 596 scan "
             "pages finds no other occurrence, so the book cannot say whether the word "
             "is hyphenated; the book hyphenates the other water- compounds it sets "
             "mid-line, which is analogy, not proof; the Standard Book's keyed text "
             "breaks the word at the same line end, it does not print \"waterside\". "
             "Carried as the carrier prints it"),
    (107, 1): ('gracious :',
               "the 1892 Standard Book (scan p. 487) prints a semicolon after "
               "\"gracious\" and no colon anywhere in this verse; the cell keeps the "
               "repo's one mediant \" : \" there (R21)"),
    (139, 7): ('there :',
               "the 1892 Standard Book (scan p. 525) prints a semicolon after the first "
               "\"there\" and no colon anywhere in this verse; the cell keeps the "
               "repo's one mediant \" : \" there (R21)"),
    (139, 11): ('with thee,',
                "the stop after \"with thee\" (1892 Standard Book, scan p. 525, last "
                "line) is damaged type; read at 3x as a comma, as the cell prints it, "
                "but it could be a semicolon"),
}


def edits_for(psalm, verse, groups=None, semi_mode=None):
    """-> [(group, tag, key, replacement)] for one verse, enabled groups only."""
    g = GROUPS if groups is None else groups
    mode = SEMI_MODE if semi_mode is None else semi_mode
    out = []
    if g.get('POINTING_MOVE'):
        for p, v, pairs in POINTING_MOVE:
            if (p, v) == (psalm, verse):
                out += [('POINTING_MOVE', '%d:%d:mediant' % (p, v), a, b) for a, b in pairs]
    if g.get('POINTING_SEMI') and mode != 'keep':
        for p, v, k in POINTING_SEMI:
            if (p, v) == (psalm, verse):
                out.append(('POINTING_SEMI', '%d:%d:mediant' % (p, v), k, SEMI_NEW[mode](k)))
    if g.get('WORDS'):
        out += [('WORDS', '%d:%d:word:%s' % (p, v, a), a, b)
                for p, v, a, b in WORDS if (p, v) == (psalm, verse)]
    if g.get('PUNCT'):
        out += [('PUNCT', '%d:%d:punct:%s' % (p, v, i), a, b)
                for p, v, a, b, i in PUNCT if (p, v) == (psalm, verse)]
    if g.get('SPACING'):
        out += [('SPACING', '%d:%d:spacing:%s' % (p, v, a), a, b)
                for p, v, a, b in SPACING if (p, v) == (psalm, verse)]
    if g.get('FURNITURE'):
        out += [('FURNITURE', '%d:%d:furniture' % (p, v), a, b)
                for p, v, a, b in FURNITURE if (p, v) == (psalm, verse)]
    for grp in ('CASE_LORD', 'CASE_OPENING', 'CASE_CAPS'):
        if g.get(grp):
            out += [(grp, '%d:%d:case:%s' % (p, v, i), a, b)
                    for p, v, a, b, i, gg in CASE if gg == grp and (p, v) == (psalm, verse)]
    return out


def _span(a, b):
    """The minimal differing span: a[i:len(a)-j] -> b[i:len(b)-j]."""
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    j = 0
    while j < min(len(a), len(b)) - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return i, len(a) - j, b[i:len(b) - j]


def apply_text(text, psalm, verse, log, groups=None, semi_mode=None):
    """Apply every enabled correction to one verse body (no verse number).
    Stale check: each key must occur EXACTLY ONCE in the original verse."""
    eds = edits_for(psalm, verse, groups, semi_mode)
    if not eds:
        return text, False
    spans = []
    for grp, tag, key, new in eds:
        n = text.count(key)
        if n != 1:
            raise SystemExit('w22 stale key %d:%d [%s] %r occurs %d times'
                             % (psalm, verse, grp, key, n))
        at = text.index(key)
        i, j, rep = _span(key, new)
        spans.append((at + i, at + j, rep, grp, tag, key))
    spans.sort()
    for a, b in zip(spans, spans[1:]):
        if b[0] < a[1] or (b[0] == a[0] and b[1] == a[1]):
            raise SystemExit('wxc overlapping edits %d:%d: %r / %r'
                             % (psalm, verse, a[5], b[5]))
    out = text
    for s, e, rep, grp, tag, key in sorted(spans, reverse=True):
        out = out[:s] + rep + out[e:]
        log.append((grp, psalm, verse, tag))
    return out, out != text


def apply(psalms, groups=None, semi_mode=None):
    """Patch parsed 1892 psalms in place (w13_1892.parse() shape); -> log.
    Unwired until the rulings (Phase 2)."""
    log = []
    for n, p in psalms.items():
        for i, v in enumerate(p['verses']):
            new, changed = apply_text(v[1], n, v[0], log, groups, semi_mode)
            if changed:
                p['verses'][i] = [v[0], new, v[2]]
    return log


def all_keys():
    """Every keyed correction in every group (switched on or not)."""
    on = {k: True for k in GROUPS}
    seen = set()
    for p, v, *_ in (POINTING_MOVE + [(a, b, c) for a, b, c in POINTING_SEMI] + WORDS
                     + PUNCT + SPACING + FURNITURE + CASE):
        if (p, v) not in seen:
            seen.add((p, v))
            for e in edits_for(p, v, on, 'both'):
                yield p, v, e


def introduced(_cache={}):
    """Lower-case words the ENABLED corrections add to the 1892 cells --
    computed by applying them to the carrier parse (after Wave 17's) and diffing
    the word sets, so the list cannot drift from what the builder does. These
    words are attested by the SCAN (every one is checked by w22_gates.py
    against the scan's OCR or an eye read), not by the carrier PDF."""
    if 'w' not in _cache:
        import re
        import w13_1892
        import w17_witness
        ps = w13_1892.parse()
        w17_witness.apply(ps)
        words = lambda: {w.lower() for p in ps.values() for v in p['verses']
                         for w in re.findall(r"[A-Za-z]+", v[1])}
        before = words()
        apply(ps)
        _cache['w'] = words() - before
    return set(_cache['w'])
