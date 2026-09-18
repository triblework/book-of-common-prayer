"""w18_psalter.py — align the 1662 Psalter cell against the Annexed-Book scan.

The carrier (the Church of England's current authorized 1662 text) and the
witness (the 1892 type-reproduction of the manuscript annexed to the Act of
Uniformity, read by Vision OCR) are the same text in the same order, but in
different orthography: `ungodly`/`vngodly`, `rejoice`/`rejoyce`, `joy`/`ioy`.
Alignment therefore runs on a SKELETON of each word (u=v, i=j=y, doubled
letters collapsed, final -e dropped). The skeleton exists only to find the
place on the page; every reading is taken from the image (w18_read.py).

Method: unique 4-gram anchors common to both streams, chained into a monotone
backbone (longest increasing subsequence), then each verse is placed by local
search between its neighbouring anchors. That survives the ~5% of lines Vision
still drops at 4400px, which a greedy forward scan did not.

What the alignment is used for, and only this:
  * verse count and verse numbering per psalm;
  * whether a mediant is printed in a verse the carrier leaves unpointed.
Spelling and ordinary punctuation are NOT collated: the witness's own preface
states that the MS is not a standard of orthography and that the printed Sealed
Books differ from it considerably in spelling and in stops.
"""
import bisect, json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells

FIRST, LAST = 345, 507          # PDF pages of the Psalter in the witness
REC = os.path.join(HERE, 'w18_psalter_ocr.json')
N = 4


def skel(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    w = w.replace('v', 'u').replace('j', 'i').replace('y', 'i')
    w = re.sub(r'(.)\1+', r'\1', w)
    return re.sub(r'e$', '', w)


def witness_tokens():
    """-> [(token, page)] over the Psalter pages, in printed order."""
    rec = json.load(open(REC))
    out = []
    for n in range(FIRST, LAST + 1):
        for line in rec.get(str(n), []):
            for tok in line.split():
                out.append((tok, n))
    return out


def carrier_verses():
    """-> [(psalm, verse, text)] in printed order."""
    cells = w17_cells.cells('1662')
    return [(ps, v, cells[ps][v]) for ps in sorted(cells)
            for v in sorted(cells[ps])]


def anchors(a, b):
    """Unique-in-both N-gram matches, chained monotonically. -> [(ia, ib)]"""
    ia, ib = defaultdict(list), defaultdict(list)
    for i in range(len(a) - N + 1):
        ia[tuple(a[i:i + N])].append(i)
    for i in range(len(b) - N + 1):
        ib[tuple(b[i:i + N])].append(i)
    pairs = sorted((v[0], ib[k][0]) for k, v in ia.items()
                   if len(v) == 1 and len(ib.get(k, [])) == 1)
    # longest increasing subsequence on the witness index
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
    return chain[::-1]


def mapper(chain, n_a, n_b):
    """Carrier token index -> witness token index, by interpolation between
    anchors. The anchors are dense (roughly one every three words), so this is
    accurate to a word or two even where Vision dropped a line."""
    xs = [c[0] for c in chain] or [0]
    ys = [c[1] for c in chain] or [0]

    def f(x):
        k = bisect.bisect_left(xs, x)
        if k == 0:
            return max(0, ys[0] - (xs[0] - x))
        if k == len(xs):
            return min(n_b, ys[-1] + (x - xs[-1]))
        x0, x1, y0, y1 = xs[k - 1], xs[k], ys[k - 1], ys[k]
        if x1 == x0:
            return y0
        return int(round(y0 + (y1 - y0) * (x - x0) / float(x1 - x0)))
    return f


def anchored(chain, lo, hi):
    """True when at least one anchor falls inside [lo, hi) of the carrier."""
    xs = [c[0] for c in chain]
    k = bisect.bisect_left(xs, lo)
    return k < len(xs) and xs[k] < hi


def build(margin=3):
    tokens = witness_tokens()
    verses = carrier_verses()
    b_sk = [skel(t) for t, _ in tokens]
    a_words, starts = [], []
    for _, _, text in verses:
        starts.append(len(a_words))
        a_words.extend(text.split())
    a_sk = [skel(w) for w in a_words]
    chain = anchors(a_sk, b_sk)
    f = mapper(chain, len(a_sk), len(b_sk))
    rows = []
    for k, (ps, v, text) in enumerate(verses):
        lo = starts[k]
        hi = starts[k + 1] if k + 1 < len(starts) else len(a_words)
        i, j = f(lo), f(hi)
        i, j = max(0, i - margin), min(len(tokens), j + margin)
        if j <= i:
            j = min(len(tokens), i + 1)
        rows.append({'psalm': ps, 'verse': v,
                     'page': tokens[min(i, len(tokens) - 1)][1],
                     'carrier': text,
                     'witness': ' '.join(t for t, _ in tokens[i:j]),
                     'ratio': round((j - i) / float(max(1, hi - lo)), 2),
                     'anchored': anchored(chain, lo, hi)})
    return rows, chain, tokens, verses


def main():
    rows, chain, tokens, verses = build()
    json.dump(rows, open(os.path.join(HERE, 'w18_align.json'), 'w'), indent=0)
    loose = [r for r in rows if not r['anchored'] or not 0.6 <= r['ratio'] <= 1.8]
    print('witness tokens %d; carrier verses %d; anchors %d; loose spans %d'
          % (len(tokens), len(verses), len(chain), len(loose)))
    mism = [r for r in rows if r not in loose and
            (' : ' in r['carrier']) != bool(re.search(r'[:;]', r['witness']))]
    print('mediant-presence mismatches (in well-anchored verses): %d' % len(mism))
    for r in mism[:30]:
        print('  %3d:%-3d p%-4d carrier-mediant=%-5s | %s'
              % (r['psalm'], r['verse'], r['page'], ' : ' in r['carrier'],
                 r['witness'][:95]))


if __name__ == '__main__':
    main()
