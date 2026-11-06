"""w22_case_keys.py -- turn the eye-read LETTER-CASE differences
(w22_eye_2.CASE) into keyed corrections, file -> file.

For each (verse, cell word, occurrence, book form): the key is the cell's own
text around that whole-word occurrence, widened a word at a time until it
occurs exactly once in the verse; the replacement changes that word's letters'
case and nothing else (checked here: the two differ only in case).

The cells are read at Wave 22's branch base (BASE, by full SHA, as
w22_gates.py does), because w22_witness applies every key to the verse as the
builder hands it over -- after Wave 17's corrections, before Wave 22's. Wave 22
read them from the work tree while it still equalled BASE; since the Wave 22
publish the work tree carries Wave 22's stops, so reading it would re-key.
(Wave 24 made the change; the 94 Wave-22 keys regenerate byte-identical.)

    python3 ingest/w22_case_keys.py   # -> ingest/w22_case_keys.json
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import subprocess
import w22_eye_2 as E

OUT = os.path.join(HERE, 'w22_case_keys.json')
BASE = '710f635b7783f1e8188fa334ec75dca3e43a0220'      # = w22_gates.BASE
GROUP = {'lord': 'CASE_LORD', 'opening': 'CASE_OPENING', 'caps': 'CASE_CAPS',
         'possessive': 'CASE_POSSESSIVE'}


def base_cells():
    """{psalm: {verse: text}} of the 1892 Psalter at BASE -- w17_cells.cells()'s
    parse, over the committed files."""
    out = {}
    for f in ('psalms-1-50', 'psalms-51-100', 'psalms-101-150'):
        text = subprocess.run(['git', 'show', '%s:editions/1892/psalter/%s.md' % (BASE, f)],
                              cwd=HERE, capture_output=True, text=True, check=True).stdout
        ps = None
        for line in text.split('\n'):
            m = re.match(r'^## Psalm (\d+)', line)
            if m:
                ps = int(m.group(1)); out[ps] = {}; continue
            if ps is None or not line.strip() or line.startswith(('>', '<!--', '#')):
                continue
            m = re.match(r'^(\d+) (.*)$', line)
            if m:
                out[ps][int(m.group(1))] = m.group(2)
            else:
                out[ps][1] = line          # verse 1 carries no number
    return out


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
    cells = base_cells()
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
