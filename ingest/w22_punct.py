"""w22_punct.py -- the ordinary punctuation of the 1892 cells against the scan.

Workstream C, Phase 1b. Every place the page OCR's stop disagrees with the
cell's (away from the cell's mediant; w22_align 'other', 439 positions) was
read by EYE off a crop that names only the verse and the word
(w22_punct_strips.py; reads keyed in w22_punct_eye.py). Places the eye found
on whole-verse crops that the OCR did not flag (w22_eye_1b, via w22_eye_cmp)
are added with source 'verse'.

Each place is classed:
  noise          the eye reads what the cell prints -- the OCR was wrong
  final          a different stop on the verse's last word
  semi-comma     mid-verse: the cell prints ',' and the book ';', or the reverse
  comma-added    mid-verse: the book prints ',' where the cell prints nothing
  comma-missing  mid-verse: the cell prints ',' where the book prints nothing
  other-mid      any other mid-verse difference (';' vs ':', ',' vs '.', '!' ...)
  word           a word-division difference (the book prints one word)
  uncertain      the eye could not settle the mark (damaged type)

Writes ingest/w22_punct.tsv and prints the counts.
"""
import collections, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w22_punct_eye as P
import w22_punct_strips as S
import w22_eye_1b as E
import w22_eye_cmp as K

OUT = os.path.join(HERE, 'w22_punct.tsv')
SYM = {'Q': '?'}


def fragment(text, k, before=3, after=2):
    """<= 8 words of the cell around its k-th word (0-based, stops attached)."""
    toks = [t for t in text.split() if t != ':' or True]
    words, idx = [], []
    for i, t in enumerate(toks):
        if re.search(r'[A-Za-z]', t):
            idx.append(i)
    i = idx[k]
    lo = max(0, i - before)
    hi = min(len(toks), i + after + 1)
    return ' '.join(toks[lo:hi])


def classify(cell, book, last, note=''):
    c = cell.replace(':', '') if False else cell
    if book == 'W':
        return 'word'
    if 'uncertain' in note:
        return 'uncertain'
    if book == c or (book == '-' and c == ''):
        return 'noise'
    if last:
        return 'final'
    cc = c or '-'
    if {cc, book} == {',', ';'}:
        return 'semi-comma'
    if cc == '-' and book == ',':
        return 'comma-added'
    if cc == ',' and book == '-':
        return 'comma-missing'
    return 'other-mid'


def _pages():
    import w22_crops as C
    recs, by = C.load()
    return {'%d:%d' % k: (r.get('pivot') or {}).get('page') or r.get('page') for k, r in by.items()}


def main():
    global E_PAGE
    E_PAGE = _pages()
    cells = w17_cells.cells('1892')
    seq = ''.join(P.STRIPS[k] for k in sorted(P.STRIPS))
    pos = S.positions()
    assert len(seq) == len(pos), (len(seq), len(pos))
    rows, seen = [], set()
    for n, ((r, o), ch) in enumerate(zip(pos, seq), 1):
        note = ''
        if n in P.FIX:
            ch, note = P.FIX[n]
        note = '; '.join(x for x in (note, P.NOTE.get(n, '')) if x)
        book = SYM.get(ch, ch)
        cell = o['cell']
        ref = '%d:%d' % (r['psalm'], r['verse'])
        cls = classify(cell, book, o['last'], note)
        frag = fragment(cells[r['psalm']][r['verse']], o['off'])
        rows.append((n, ref, o['page'], o['word'], cell or '-', book, o['ocr'] or '-',
                     'end' if o['last'] else 'in', cls, 'ocr', frag, note, o['off']))
        seen.add((ref, o['word'].lower()))
    # places found only on whole-verse crops
    extra = 0
    for book_reads in (E.MEDIANT, E.CONTROL):
        for ref in sorted(book_reads, key=lambda s: tuple(map(int, s.split(':')))):
            for d in K.compare(ref, book_reads[ref], cells):
                if d[0] not in ('book+', 'class', 'cell+'):
                    continue
                w = d[1]
                if (ref, w.lower()) in seen:
                    continue
                ps, v = map(int, ref.split(':'))
                toks = K.cell_tokens(cells[ps][v])
                k = next(i for i, t in enumerate(toks) if t[0] == w)
                book = d[3] if d[3] != '?' else ''
                note = E.NOTES.get(ref, '')
                if d[0] == 'cell+':
                    # the eye saw no colon-class mark there; what it is was
                    # recorded in NOTES where read
                    m = re.search(r"'%s([,.;:!?]?)" % re.escape(w), note)
                    book = (m.group(1) or '-') if m else '?'
                last = d[4]
                cls = classify(d[2].strip(':') if d[2] != ':' else d[2], book, last, note)
                if book == '?':
                    cls = 'uncertain'
                frag = fragment(cells[ps][v], k)
                pg = E_PAGE.get(ref, '')
                rows.append(('V%02d' % (extra + 1), ref, pg, w, d[2] or '-', book, '-',
                             'end' if last else 'in', cls, 'verse', frag, note, k))
                seen.add((ref, w.lower()))
                extra += 1
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('# w22_punct.tsv -- 1892 cell stops vs the Standard Book scan, read by eye.\n'
                 '# id\tverse\tscan page\tword\tcell mark\tbook mark (eye)\tOCR mark\t'
                 'position\tclass\tsource\tcell fragment (<=8 words)\tnote\tword index\n')
        for row in rows:
            fh.write('\t'.join(str(x) for x in row) + '\n')
    c = collections.Counter(r[8] for r in rows)
    print('places %d (%d OCR-flagged, %d found on whole-verse crops)' % (len(rows), len(pos), extra))
    print('classes: ' + ', '.join('%s %d' % kv for kv in c.most_common()))
    real = [r for r in rows if r[8] not in ('noise',)]
    print('differences (not OCR noise): %d' % len(real))
    fin = collections.Counter('%s>%s' % (r[4], r[5]) for r in rows if r[8] == 'final')
    print('final, cell>book: %s' % dict(fin.most_common()))
    sc = collections.Counter('%s>%s' % (r[4], r[5]) for r in rows if r[8] == 'semi-comma')
    print('semi-comma, cell>book: %s' % dict(sc))
    om = collections.Counter('%s>%s' % (r[4], r[5]) for r in rows if r[8] == 'other-mid')
    print('other-mid, cell>book: %s' % dict(om))


if __name__ == '__main__':
    main()
