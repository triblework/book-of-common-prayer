"""w22_eye_cmp.py -- compare the Phase-1b whole-verse eye reads with the cells.

Workstream C. For every verse read whole by eye (w22_eye_1b.MEDIANT, the
flagged/other queues; w22_eye_1b.CONTROL, the seeded Q1 sample) the eye
recorded the mark after the cell's pivot word and EVERY other colon-class mark
(':' or ';') in the verse. Here those are set against the cell (the branch-base
cells, editions/1892/psalter), giving per verse:

  pivot      the book's mark after the pivot, if not ':'
  book+      a colon-class mark the book prints on a word where the cell prints
             a weaker stop or none (word, cell mark, book mark)
  class      both print a colon-class mark there but a different one
  cell+      the cell prints ':'/';' (other than its mediant) on a word where the
             eye saw no colon-class mark -- the book prints something weaker

    python3 ingest/w22_eye_cmp.py           # summary
    python3 ingest/w22_eye_cmp.py --list    # every disagreement
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w22_eye_1b as E

COL = set(':;')


def cell_tokens(text):
    """-> [(word, mark, is_mediant)] with stops attached to the word before."""
    out = []
    for t in text.split():
        m = re.match(r"^(.*?)([:;.,!?]*)$", t)
        core, mark = m.group(1), m.group(2)
        if not re.search(r'[A-Za-z]', core):
            if out:
                w, mk, med = out[-1]
                out[-1] = (w, mk + mark, med or t == ':')
            continue
        out.append((core, mark, False))
    return out


def parse_eye(s):
    piv, rest = s.split('|', 1)
    marks = []
    for tok in rest.split():
        w, mk = tok[:-1], tok[-1]
        n = 1
        if '#' in w:
            w, n = w.split('#'); n = int(n)
        marks.append((w, n, mk))
    return piv, marks


def compare(ref, eye, cells):
    ps, v = map(int, ref.split(':'))
    toks = cell_tokens(cells[ps][v])
    piv, marks = parse_eye(eye)
    out = []
    if piv != ':':
        mi = next(i for i, t in enumerate(toks) if t[2])
        out.append(('pivot', toks[mi][0], ':', piv))
    # index cell words by (lower word, occurrence)
    occ, idx = {}, {}
    for i, (w, mk, med) in enumerate(toks):
        k = w.lower()
        occ[k] = occ.get(k, 0) + 1
        idx[(k, occ[k])] = i
    seen = set()
    for w, n, mk in marks:
        i = idx.get((w.lower(), n))
        if i is None:
            out.append(('unmatched', w, '?', mk))
            continue
        seen.add(i)
        cw, cm, med = toks[i]
        cmark = cm.replace(':', '') if med else cm      # the mediant is not this mark
        cc = set(cmark) & COL
        if not cc:
            out.append(('book+', cw, cmark or '-', mk, i == len(toks) - 1))
        elif mk not in cc:
            out.append(('class', cw, cmark, mk, i == len(toks) - 1))
    for i, (cw, cm, med) in enumerate(toks):
        cmark = cm.replace(':', '') if med else cm
        if i not in seen and set(cmark) & COL:
            out.append(('cell+', cw, cmark, '?', i == len(toks) - 1))
    return out


def main():
    cells = w17_cells.cells('1892')
    show = '--list' in sys.argv
    for name, book in (('MEDIANT queue (Q2+Q3)', E.MEDIANT), ('CONTROL (Q1 sample)', E.CONTROL)):
        tally, verses = {}, {}
        for ref in sorted(book, key=lambda r: tuple(map(int, r.split(':')))):
            d = compare(ref, book[ref], cells)
            for x in d:
                tally[x[0]] = tally.get(x[0], 0) + 1
                verses.setdefault(x[0], set()).add(ref)
                if show:
                    print('  %-8s %-7s %s' % (name.split()[0], ref, x))
        print('%s: %d verses read; %s; verses with any: %d' % (
            name, len(book), ', '.join('%s %d (%d verses)' % (k, tally[k], len(verses[k]))
                                       for k in sorted(tally)),
            len(set().union(*verses.values())) if verses else 0))


if __name__ == '__main__':
    main()
