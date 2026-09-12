#!/usr/bin/env python3
"""w17_witness.py — the 1892 Psalter read against the Standard Book scan.

Authoring-only; NOT published. See ingest/WAVE17_GUIDE.md.

CARRIER   1892/Psalms.pdf, the page Wave 13 built the cells from.
WITNESS   1892Standard/1892standard.pdf -- a 596-page SCAN (bitonal page
          images, no text layer) of the 1892 Standard Book, subscribers'
          edition. The Psalter is scan pages 357-536.

Wave 13 could not decide fourteen readings and said so: "only a page scan can
say which". The scan says, and it says the same thing every time -- the
carrier is not the 1892 text in these places. It reads *show* where the
carrier reads *shew* (no instance of "shew" occurs on any of the 180 pages),
*judgment* for *judgement*, and it points six verses the carrier leaves
unpointed.

Each correction below is evidenced in ingest/w17_evidence.json, which records
for every instance the scan page, and either a second OCR of that line cropped
from a 4400px render (`auto`) or the reading taken by eye from the page image
(`eye`). Nothing here is computed from another edition.
"""
from __future__ import annotations
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = json.load(open(os.path.join(HERE, 'w17_evidence.json'), encoding='utf-8'))

# 1. Spelling classes. The carrier's forms; the scan's forms carried.
SPELLING = [
    (re.compile(r'\bShew(\w*)'), r'Show\1'),
    (re.compile(r'\bshew(\w*)'), r'show\1'),
    (re.compile(r'\bjudgement(s?)\b'), r'judgment\1'),
]

# 2. Hyphenation, word by word (the book is not uniform: it closes
# "hailstones" and "lawgiver" but keeps "wash-pot" and "blood-thirsty",
# and it moves the hyphen in "southwest-wind").
HYPHENS = {
    'hail-stones': 'hailstones', 'first-born': 'firstborn', 'eye-lids': 'eyelids',
    'eye-sight': 'eyesight', 'needle-work': 'needlework', 'house-top': 'housetop',
    'house-tops': 'housetops', 'law-giver': 'lawgiver', 'over-past': 'overpast',
    'spear-men': 'spearmen', 'night-season': 'night season',
    'night-watches': 'night watches', 'evil-doers': 'evil doers',
    'north-side': 'north side', 'new-moon': 'new moon', 'wrong-doer': 'wrong doer',
    'south-west wind': 'southwest-wind',
}

# 3. Single readings -- the words Wave 13 flagged, each now read off the page.
WORDS = [
    (18, 10, 'cherubins', 'Cherubim'),
    (42, 9, 'the water-pipes', 'thy water-pipes'),
    (50, 17, 'and has cast', 'and hast cast'),
    (68, 27, 'Zebulon', 'Zabulon'),
    (68, 31, 'Eqypt', 'Egypt'),
    (83, 9, 'Madianites', 'Madianites'),          # carrier "Midianites"
    (83, 9, 'Midianites', 'Madianites'),
    (102, 4, 'withered liked grass', 'withered like grass'),
]

# 4. Pointing. The carrier loses the mediant in six verses and prints a colon
# for a semicolon in one. `old`/`new` are the exact strings.
POINTING = [
    (10, 4, 'not for God ; neither', 'not for God : neither'),
    (14, 7, 'not known ; there', 'not known : there'),
    (17, 3, 'wickedness in me; for', 'wickedness in me : for'),
    (35, 20, 'not for peace; but', 'not for peace : but'),
    (45, 11, 'thine ear ; forget', 'thine ear : forget'),
    (77, 18, 'upon the ground : the earth', 'upon the ground ; the earth'),
    (115, 8, 'unto them ; and so', 'unto them : and so'),
]

# The one reading the scan cannot settle: the carrier's "water-side" falls at
# a line break in the scan ("water-" / "side"), so the hyphen there is the
# printer's, not the word's. Carried as the carrier prints it, flagged.
VERIFY = {
    (1, 3): ('water-side',
             "the 1892 Standard Book scan breaks this word across a line "
             "(\"water-\" / \"side\"), so the page cannot say whether the word "
             "is hyphenated; the Standard Book's keyed text prints "
             "\"waterside\". Carried as the carrier prints it"),
}


def apply_text(text, psalm, verse, log):
    """Apply every correction to one verse; append (kind, before, after)."""
    before = text
    for rx, repl in SPELLING:
        for m in rx.finditer(text):
            log.append(('spelling', psalm, verse, m.group(0)))
        text = rx.sub(repl, text)
    for a, b in sorted(HYPHENS.items(), key=lambda kv: -len(kv[0])):
        if a in text:
            text = text.replace(a, b)
            log.append(('hyphen', psalm, verse, a))
    for p, v, a, b in WORDS:
        if (p, v) == (psalm, verse) and a in text and a != b:
            text = text.replace(a, b)
            log.append(('word', psalm, verse, a))
    for p, v, a, b in POINTING:
        if (p, v) == (psalm, verse):
            if a not in text:
                raise SystemExit('w17 pointing %d:%d: %r not in %r'
                                 % (psalm, verse, a, text[:90]))
            text = text.replace(a, b)
            log.append(('pointing', psalm, verse, a))
    return text, text != before


def apply(psalms):
    """Patch the parsed 1892 psalms in place; -> the log of corrections."""
    log = []
    for n, p in psalms.items():
        for i, v in enumerate(p['verses']):
            new, changed = apply_text(v[1], n, v[0], log)
            if changed:
                p['verses'][i] = [v[0], new, v[2]]
    return log


def introduced(_cache={}):
    """Lower-case words these corrections ADD to the 1892 cells -- computed by
    applying them to the carrier and diffing the word sets, so the list can
    never drift from what the builder does. These are the words attested by
    the SCAN rather than by the carrier PDF; w17_gates.py checks each one."""
    if 'w' not in _cache:
        import w13_1892
        ps = w13_1892.parse()
        before = set()
        for p in ps.values():
            for v in p['verses']:
                before |= {w.lower() for w in re.findall(r"[A-Za-z]+", v[1])}
        apply(ps)
        after = set()
        for p in ps.values():
            for v in p['verses']:
                after |= {w.lower() for w in re.findall(r"[A-Za-z]+", v[1])}
        _cache['w'] = after - before
    return set(_cache['w'])
