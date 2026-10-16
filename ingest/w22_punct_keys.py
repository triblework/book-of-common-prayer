"""w22_punct_keys.py -- turn the eye-read punctuation differences into KEYED
corrections (file -> file; no verse text passes through anyone's tokens).

Workstream C, Phase 1b. For every row of ingest/w22_punct.tsv whose class is a
real difference (final, semi-comma, comma-added, comma-missing, other-mid), the
key is the cell's own words around the place -- the word with its stop plus the
next word (the word before, for a verse-final stop), widened one word at a time
until it occurs exactly once in that verse -- and the replacement is the same
words with the book's stop. The replacement changes ONLY the stop (and, where
the book starts a sentence there, the next word's capital, CASE below).

Excluded, because another group owns the place: the two verses whose mediant
moves (39:14 'sojourner', 100:2 'ourselves' -- POINTING_MOVE), the 150:6
colophon (a ruling), and the one uncertain read (139:11).

A non-mediant colon or semicolon is written closed up ('Anointed:'), as R16
closes the 1892 compositor's space and as the cells already print 'thee:'
(40:6) -- RN-4's sub-question; flip CLOSE to False to keep the book's space.

    python3 ingest/w22_punct_keys.py     # -> ingest/w22_punct_keys.json
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells

TSV = os.path.join(HERE, 'w22_punct.tsv')
OUT = os.path.join(HERE, 'w22_punct_keys.json')
REAL = {'final', 'semi-comma', 'comma-added', 'comma-missing', 'other-mid'}
EXCLUDE = {('39:14', 'sojourner'), ('100:2', 'ourselves'), ('150:6', 'PSALTER'),
           ('139:11', 'thee')}
CASE = {'43', '224', '319'}     # the book's full stop is followed by a capital
CLOSE = True
STOPS = ':;.,!?'


def units(text):
    """-> tokens, and for each alpha word (in order) the token span [j, k)
    holding the word and any stop tokens set apart after it."""
    toks = text.split(' ')
    spans, j = [], 0
    while j < len(toks):
        if re.search(r'[A-Za-z]', toks[j]):
            k = j + 1
            while k < len(toks) and toks[k] and all(c in STOPS for c in toks[k]) and toks[k] != ':':
                k += 1
            spans.append((j, k))
            j = k
        else:
            j += 1
    return toks, spans


def key_for(text, off, book, last, case):
    toks, spans = units(text)
    j, k = spans[off]
    core = re.sub(r'[%s]+$' % re.escape(STOPS), '', toks[j])
    mark = '' if book == '-' else book
    unit_new = core + mark
    if last:
        lo, hi = j - 1, k
        while True:
            old = ' '.join(toks[lo:hi])
            new = ' '.join(toks[lo:j] + [unit_new])
            if text.endswith(old) and text.count(old) == 1:
                return old, new, True
            lo -= 1
    lo, hi = j, k + 1
    while True:
        old = ' '.join(toks[lo:hi])
        nxt = toks[k] if k < len(toks) else ''
        if case and nxt:
            nxt = nxt[0].upper() + nxt[1:]
        new = ' '.join(toks[lo:j] + [unit_new] + ([nxt] if nxt else []) + toks[k + 1:hi])
        if text.count(old) == 1:
            return old, new, False
        if lo > 0:
            lo -= 1
        else:
            hi += 1


def main():
    cells = w17_cells.cells('1892')
    keys = []
    for line in open(TSV, encoding='utf-8'):
        if line.startswith('#'):
            continue
        f = line.rstrip('\n').split('\t')
        pid, ref, page, word, cell, book, ocr, pos, cls, src, frag, note, off = f
        if cls not in REAL or (ref, word) in EXCLUDE:
            continue
        ps, v = map(int, ref.split(':'))
        old, new, fin = key_for(cells[ps][v], int(off), book, pos == 'end', pid in CASE)
        keys.append({'id': pid, 'psalm': ps, 'verse': v, 'old': old, 'new': new,
                     'class': cls, 'page': int(page) if page else None,
                     'cell': cell, 'book': book, 'end': fin})
    json.dump(keys, open(OUT, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
    print('%d keyed punctuation corrections -> %s' % (len(keys), OUT))


if __name__ == '__main__':
    main()
