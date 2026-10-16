"""w21_psalter.py -- align the 1928 Psalter cells against a scan's page OCR
(Workstream B; w18_psalter's method, read-only).

The cells (editions/1928/psalter, via w17_cells) and a scan record
(ingest/w21_<pdf>_ocr.json, w21_scan.py) are the same text in the same order
and, unlike 1662, the same modern spelling. So the alignment SKELETON is just
the lower-case letters of a word (hyphens and stops dropped); it exists only
to find the place on the page -- every reading is taken from the image.

Witness stream: the Psalter's book pages (pp. 345-525) in printed order, each
page's lines top to bottom BY PIXEL BOX (w21_scan), with the furniture left
out -- running head (a page's first line), folio (last line), psalm, day,
Book and Psalm-119 section headings. A word broken at a line end ("water-" /
"side") is joined into one token flagged `lb`: whether its hyphen is the
word's or the compositor's is something that page cannot say. Verse numbers
are kept aside (`num`), not aligned. A mark that follows a word (`*`, and the
glyphs Vision reads for a small raised asterisk: " ' bullet and curly
quotes) sets that word's `mark`.

Method (w18_psalter): unique 4-gram skeleton anchors common to both streams,
chained by longest increasing subsequence; between consecutive anchors the
two short segments are diffed word by word (difflib), which gives every cell
word a witness partner or none. A verse is PLACED when at least 60% of its words have
an EQUAL witness partner and its witness span is 0.6-1.8x its length (an
anchor inside is not required: repeated refrains -- 8:9, 24:7, 24:9 -- have
no unique 4-gram, and the diff places them exactly).

    python3 ingest/w21_psalter.py 1929        # -> <render>/align/w21_align_1929.json
    python3 ingest/w21_psalter.py 1952
"""
import bisect, difflib, json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w21_render
from w21_ocrstats import book_page, FIRST_PAGE, LAST_PAGE

N = 4
ALIGN_DIR = os.path.join(w21_render.OUT_ROOT, 'align')
MARKS = '*"\'•’“”·'
HEADS = re.compile(
    r"^(Psalms?\s*[\dIlOoS]{1,3}\s*[.,:]|Psalm\s*\d|The \w+ Day\b|THE \w+ DAY\b|"
    r"Morning Prayer\.?$|Evening Prayer\.?$|BOOK [IVX]+\.?$|The Psalter$|"
    r"or Psalms of David|The End of the Psalter|[IVXL]{1,7}\.\s+[A-Z][a-z]+.*[.?]$)")


def form(w):
    """A word as compared: lower case, curly apostrophe straightened, edge
    punctuation off, internal hyphens and apostrophes kept."""
    w = w.replace('’', "'").replace('‘', "'").lower()
    return re.sub(r"^[^a-z]+|[^a-z]+$", '', w)


def skel(w):
    return re.sub(r'[^a-z]', '', w.lower())


def is_head(k, n_lines, text):
    t = text.strip()
    if k == 0 and ('Psalter' in t or re.match(r'(D?ay|Psalms?)\b', t)):
        return 'runninghead'
    if k == n_lines - 1 and re.fullmatch(r'[\dIlOoS]{3}', t.replace(' ', '')):
        return 'folio'
    if HEADS.match(t):
        return 'heading'
    return None


def witness_tokens(which):
    """-> list of dicts {t, f, sk, scan, side, book, line, lb, mark, num}."""
    rec = json.load(open(os.path.join(HERE, 'w21_%s_ocr.json' % which)))
    out, heads = [], []
    for n in sorted(rec, key=int):
        for side in 'LR':
            bp = book_page(which, n, side)
            if not FIRST_PAGE <= bp <= LAST_PAGE:
                continue
            lines = rec[n][side]
            for k, (t, x, y, w, h) in enumerate(lines):
                kind = is_head(k, len(lines), t)
                if kind:
                    heads.append((which, int(n), side, bp, k, kind, t))
                    continue
                raw = re.sub(r'\*', ' * ', t).split()
                for j, tok in enumerate(raw):
                    if not re.search(r'[A-Za-z]', tok):
                        if out and re.fullmatch('[%s,.;:!?]+' % re.escape(MARKS), tok) \
                                and re.search('[%s]' % re.escape(MARKS), tok):
                            out[-1]['mark'] = True
                        elif re.fullmatch(r'[\d]+[.,]?', tok) and j == 0:
                            out.append({'num': int(re.sub(r'\D', '', tok)), 'scan': int(n),
                                        'side': side, 'book': bp, 'line': k})
                        continue
                    if j == 0 and re.fullmatch(r'[\dIlO]{1,3}', tok) and re.search(r'\d', tok):
                        continue                    # a misread verse number ("I0")
                    mark = bool(re.search('[%s]$' % re.escape(MARKS), tok.rstrip(',.;:!?'))
                                or re.search('[%s][,.;:!?]*$' % re.escape(MARKS), tok)) \
                        and not tok.endswith("'s")
                    out.append({'t': tok, 'f': form(tok), 'sk': skel(tok), 'scan': int(n),
                                'side': side, 'book': bp, 'line': k, 'lb': False,
                                'mark': mark})
            # join a word broken at a line end with the next line's first word
    words = []
    for tk in out:
        if 'num' in tk:
            words.append(tk); continue
        prev = next((p for p in reversed(words) if 'num' not in p), None)
        if (prev is not None and prev['t'].endswith('-') and not prev['lb']
                and (prev['line'], prev['book']) != (tk['line'], tk['book'])):
            prev['t'] = prev['t'] + tk['t']
            a = form(prev['t'])
            prev.update(f=a, sk=skel(prev['t']), lb=True, lb_alt=a.replace('-', '', 1),
                        mark=tk['mark'], line2=tk['line'], book2=tk['book'],
                        scan2=tk['scan'], side2=tk['side'])
            continue
        words.append(tk)
    return words, heads


def carrier_tokens():
    """-> verses [(psalm, verse, text)], tokens [{t, f, sk, vi, med}] where
    `med` marks the word the cell's mediant (' : ') follows."""
    cells = w17_cells.cells('1928')
    verses = [(ps, v, cells[ps][v]) for ps in sorted(cells) for v in sorted(cells[ps])]
    toks = []
    for vi, (_ps, _v, text) in enumerate(verses):
        parts = text.split()
        for j, p in enumerate(parts):
            if not re.search(r'[A-Za-z]', p):
                continue
            med = j + 1 < len(parts) and parts[j + 1] == ':'
            toks.append({'t': p, 'f': form(p), 'sk': skel(p), 'vi': vi, 'med': med})
    return verses, toks


def anchors(a, b):
    ia, ib = defaultdict(list), defaultdict(list)
    for i in range(len(a) - N + 1):
        ia[tuple(a[i:i + N])].append(i)
    for i in range(len(b) - N + 1):
        ib[tuple(b[i:i + N])].append(i)
    pairs = sorted((v[0], ib[k][0]) for k, v in ia.items()
                   if len(v) == 1 and len(ib.get(k, [])) == 1)
    tails, back, idx = [], [None] * len(pairs), []
    for n, (_, j) in enumerate(pairs):
        p = bisect.bisect_left(tails, j)
        if p == len(tails):
            tails.append(j); idx.append(n)
        else:
            tails[p] = j; idx[p] = n
        back[n] = idx[p - 1] if p else None
    chain, n = [], (idx[-1] if idx else None)
    while n is not None:
        chain.append(pairs[n]); n = back[n]
    chain = chain[::-1]
    # drop overlapping anchors so segments between them are well defined
    out = []
    for c in chain:
        if not out or (c[0] >= out[-1][0] + N and c[1] >= out[-1][1] + N):
            out.append(c)
    return out


def word_map(ctoks, wtoks, chain):
    """Carrier index -> witness index (or None), diffing between anchors."""
    m = [None] * len(ctoks)
    ops = []                                   # (tag, c_lo, c_hi, w_lo, w_hi)
    a = [t['sk'] for t in ctoks]
    b = [t['sk'] for t in wtoks]
    bounds = [(-N, -N)] + chain + [(len(a), len(b))]
    for (c0, w0), (c1, w1) in zip(bounds, bounds[1:]):
        if c0 >= 0:
            for k in range(N):
                m[c0 + k] = w0 + k
        lo_c, lo_w = c0 + N, w0 + N
        sm = difflib.SequenceMatcher(None, a[lo_c:c1], b[lo_w:w1], autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    m[lo_c + i1 + k] = lo_w + j1 + k
            else:
                ops.append((tag, lo_c + i1, lo_c + i2, lo_w + j1, lo_w + j2))
                if tag == 'replace' and i2 - i1 == j2 - j1:
                    for k in range(i2 - i1):       # one-for-one: a partner, unequal
                        m[lo_c + i1 + k] = lo_w + j1 + k
    return m, ops


def build(which):
    verses, ctoks = carrier_tokens()
    allw, heads = witness_tokens(which)
    wtoks = [t for t in allw if 'num' not in t]
    nums = [t for t in allw if 'num' in t]
    chain = anchors([t['sk'] for t in ctoks], [t['sk'] for t in wtoks])
    m, ops = word_map(ctoks, wtoks, chain)
    xs = [c[0] for c in chain]
    starts = defaultdict(list)
    for i, t in enumerate(ctoks):
        starts[t['vi']].append(i)
    rows = []
    for vi, (ps, v, text) in enumerate(verses):
        idx = starts[vi]
        lo, hi = idx[0], idx[-1] + 1
        k = bisect.bisect_left(xs, lo)
        anchored = k < len(xs) and xs[k] < hi
        ws = [m[i] for i in idx if m[i] is not None]
        if ws:
            wlo, whi = min(ws), max(ws) + 1
        else:
            wlo = whi = None
        ratio = round((whi - wlo) / float(hi - lo), 2) if ws else 0
        pages = sorted({(wtoks[j]['scan'], wtoks[j]['side'], wtoks[j]['book'])
                        for j in range(wlo, whi)}) if ws else []
        eq = sum(1 for i in idx if m[i] is not None and wtoks[m[i]]['sk'] == ctoks[i]['sk'])
        rows.append({'psalm': ps, 'verse': v, 'c_lo': lo, 'c_hi': hi,
                     'w_lo': wlo, 'w_hi': whi, 'ratio': ratio, 'anchored': anchored,
                     'equal': eq,
                     'placed': bool(ws and eq >= 0.6 * (hi - lo) and 0.6 <= ratio <= 1.8),
                     'pages': pages,
                     'witness': ' '.join(wtoks[j]['t'] for j in range(wlo, whi)) if ws else ''})
    return {'which': which, 'verses': verses, 'ctoks': ctoks, 'wtoks': wtoks,
            'nums': nums, 'heads': heads, 'chain': chain, 'map': m, 'ops': ops,
            'rows': rows}


def main(which):
    A = build(which)
    os.makedirs(ALIGN_DIR, exist_ok=True)
    path = os.path.join(ALIGN_DIR, 'w21_align_%s.json' % which)
    json.dump({k: A[k] for k in ('which', 'rows', 'chain', 'map', 'ops', 'ctoks',
                                 'wtoks', 'heads')}, open(path, 'w'))
    rows = A['rows']
    placed = sum(r['placed'] for r in rows)
    mapped = sum(1 for x in A['map'] if x is not None)
    print('%s: witness tokens %d (lb joins %d, verse numbers %d, heading lines %d); '
          'cell tokens %d; anchors %d' % (
              which, len(A['wtoks']), sum(t['lb'] for t in A['wtoks']), len(A['nums']),
              len(A['heads']), len(A['ctoks']), len(A['chain'])))
    print('   verses %d: placed %d, unplaced %d (verses with no anchor inside %d, of '
          'them placed by the diff %d); cell words with a witness partner %d of %d, '
          'equal %d' % (
              len(rows), placed, len(rows) - placed,
              sum(1 for r in rows if not r['anchored']),
              sum(1 for r in rows if not r['anchored'] and r['placed']),
              mapped, len(A['ctoks']), sum(r['equal'] for r in rows)))
    print('   ->', path)
    return A


if __name__ == '__main__':
    for w in sys.argv[1:] or ['1929', '1952']:
        main(w)
