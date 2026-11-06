"""w25_apostrophes.py -- the apostrophe survey (Wave 25; authoring-only).

Two characters stand for the one printed apostrophe in the cells: U+0027 (')
and U+2019 (’). Both are encodings of the same mark -- no book prints a
typewriter apostrophe -- so a cell that mixes them, or two editions that
encode one word differently, show a false word change in every diff the repo
exists to show (the viewer's Compare tokenizes on whitespace).

Counts, per edition and per cell, outside <!-- --> comments (whose single
quotes delimit VERIFY keys):

    apostrophe   between two letters, or after a letter before a non-letter
                 (a plural possessive: Apostles’ Creed)
    other        anything else (a quotation mark: 1979's 'Lord, open ...')

and the false word pairs between same-path cells of the editions the corpus
descends through (a word one cell spells with ' and the other with ’).

    python3 ingest/w25_apostrophes.py [--root DIR] [--json OUT]
"""
import collections, glob, json, os, re, sys

APOS = {"'": 'straight', '’': 'curly'}
PAIRS = [('1549', '1552'), ('1552', '1559'), ('1559', '1604'), ('1604', '1637'), ('1604', '1662'),
         ('1662', '1764'), ('1662', '1789'), ('1764', '1789'), ('1764', '1929'), ('1789', '1892'),
         ('1892', '1928'), ('1928', '1979')]


def body(text):
    return re.sub(r'<!--.*?-->', '', text, flags=re.S)


def marks(text):
    """-> Counter of (form, kind) over the cell's text outside comments."""
    t = body(text)
    c = collections.Counter()
    for m in re.finditer(r"['’‘]", t):
        a = t[m.start() - 1] if m.start() else ' '
        b = t[m.end()] if m.end() < len(t) else ' '
        form = {"'": 'straight', '’': 'curly', '‘': 'left'}[m.group(0)]
        kind = 'apostrophe' if a.isalpha() and (b.isalpha() or not b.isalnum()) and form != 'left' else 'other'
        c[(form, kind)] += 1
    return c


def cells(root):
    for p in sorted(glob.glob(os.path.join(root, 'editions', '*', '**', '*.md'), recursive=True)):
        rel = os.path.relpath(p, os.path.join(root, 'editions'))
        yield rel.split('/', 1)[0], rel, open(p, encoding='utf-8').read()


def false_pairs(root):
    def toks(t):
        return collections.Counter(w for w in body(t).split() if "'" in w or '’' in w)
    out = {}
    for a, b in PAIRS:
        n, files = 0, 0
        for pa in glob.glob(os.path.join(root, 'editions', a, '**', '*.md'), recursive=True):
            pb = pa.replace('/editions/%s/' % a, '/editions/%s/' % b, 1)
            if not os.path.exists(pb):
                continue
            A, B = toks(open(pa, encoding='utf-8').read()), toks(open(pb, encoding='utf-8').read())
            k = 0
            for w, v in A.items():
                w2 = w.replace('’', "'") if '’' in w else w.replace("'", '’')
                if w2 != w:
                    k += min(v, B.get(w2, 0))
            n += k
            files += bool(k)
        out['%s-%s' % (a, b)] = [n, files]
    return out


def survey(root):
    ed = collections.defaultdict(collections.Counter)
    mixed, curly_cells = [], []
    for e, rel, t in cells(root):
        c = marks(t)
        ed[e].update(c)
        ed[e]['cells'] += 1
        s, k = c[('straight', 'apostrophe')], c[('curly', 'apostrophe')] + c[('curly', 'other')]
        if k:
            curly_cells.append(rel)
        if s and k:
            mixed.append([rel, s, k])
    return ed, mixed, curly_cells


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jout = None
    args = sys.argv[1:]
    while args:
        a = args.pop(0)
        if a == '--root':
            root = args.pop(0)
        elif a == '--json':
            jout = args.pop(0)
    ed, mixed, curly_cells = survey(root)
    print('%-5s %5s %9s %9s %9s %9s %5s' % ('ed', 'cells', "' apos", "' other", '’ apos', '’ other', '‘'))
    for e in sorted(ed):
        c = ed[e]
        print('%-5s %5d %9d %9d %9d %9d %5d' % (e, c['cells'], c[('straight', 'apostrophe')],
              c[('straight', 'other')], c[('curly', 'apostrophe')], c[('curly', 'other')],
              c[('left', 'other')]))
    print('cells with a curly apostrophe: %d; mixed cells: %d' % (len(curly_cells), len(mixed)))
    for m in mixed:
        print('  mixed  %-50s straight %3d  curly %3d' % tuple(m))
    fp = false_pairs(root)
    print('false word pairs between same-path cells (apostrophe form only):')
    for k, (n, f) in fp.items():
        if n:
            print('  %-10s %4d words in %d cells' % (k, n, f))
    if jout:
        json.dump({'editions': {e: {'%s/%s' % k if isinstance(k, tuple) else k: v
                                    for k, v in c.items()} for e, c in ed.items()},
                   'mixed': mixed, 'curly_cells': curly_cells, 'false_pairs': fp},
                  open(jout, 'w'), indent=1)


if __name__ == '__main__':
    main()
