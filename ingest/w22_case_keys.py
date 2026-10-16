"""w22_case_keys.py -- turn the eye-read LETTER-CASE differences
(w22_eye_2.CASE) into keyed corrections, file -> file.

For each (verse, cell word, occurrence, book form): the key is the cell's own
text around that whole-word occurrence, widened a word at a time until it
occurs exactly once in the verse; the replacement changes that word's letters'
case and nothing else (checked here: the two differ only in case).

    python3 ingest/w22_case_keys.py   # -> ingest/w22_case_keys.json
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w22_eye_2 as E

OUT = os.path.join(HERE, 'w22_case_keys.json')
GROUP = {'lord': 'CASE_LORD', 'opening': 'CASE_OPENING', 'caps': 'CASE_CAPS'}


def key_at(text, start, end, new):
    """Widen [start, end) to whole tokens until the span is unique in text."""
    lo, hi = start, end
    while True:
        old = text[lo:hi]
        if text.count(old) == 1:
            return old, text[lo:start] + new + text[end:hi]
        # widen by one token on the left, then on the right
        nlo = text.rfind(' ', 0, max(0, lo - 1))
        nlo = 0 if nlo < 0 else nlo + 1
        nhi = text.find(' ', hi + 1)
        nhi = len(text) if nhi < 0 else nhi
        if nlo < lo:
            lo = nlo
        elif nhi > hi:
            hi = nhi
        else:
            raise SystemExit('cannot make a unique key in %r' % text[:40])


def main():
    cells = w17_cells.cells('1892')
    keys = []
    for ref, word, occ, book, kind, strip in E.CASE:
        ps, v = map(int, ref.split(':'))
        text = cells[ps][v]
        hits = [m for m in re.finditer(r'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(word), text)]
        if not hits:
            raise SystemExit('case %s: %r not in verse' % (ref, word))
        pick = hits if occ == 'all' else [hits[occ - 1]]
        for k, m in enumerate(pick):
            if book.lower() != word.lower() or book == word:
                raise SystemExit('case %s: %r -> %r is not a case change' % (ref, word, book))
            old, new = key_at(text, m.start(), m.end(), book)
            if old.lower() != new.lower():
                raise SystemExit('case %s: key changes more than case' % ref)
            n = hits.index(m) + 1
            keys.append({'id': '%s:%s#%d' % (ref, word, n), 'psalm': ps, 'verse': v,
                         'old': old, 'new': new, 'group': GROUP[kind], 'kind': kind,
                         'cell': word, 'book': book, 'strip': strip})
    json.dump(keys, open(OUT, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
    import collections
    print('%d case keys -> %s %s' % (len(keys), OUT, dict(collections.Counter(k['group'] for k in keys))))


if __name__ == '__main__':
    main()
