"""w22_align.py -- place every 1892 cell verse, and its mediant, on the scan.

Workstream C (the full 1892 pointing collation). Wave 18's skeleton/anchor
alignment (w18_psalter.py), pointed at the 1892 cells and the 4400px Psalter
record (w22_scan.py), and taken down to the WORD: every cell word is mapped to
a page word, so the word the cell's mediant follows (the PIVOT) has a pixel
box on a page, and a crop can be cut around it for the eye.

The skeleton exists only to find the place. No reading is taken from it, and
no reading is taken from the OCR's punctuation: page OCR cannot tell ':' from
';' (Wave 17). The OCR mark is recorded only to CLASSIFY verses for the eye
(w22_classify.py).

Streams:
  cell     editions/1892/psalter (the branch-base cells), words in order; the
           ' : ' mediant and every other stop attach to the word before them.
  witness  the page OCR, rows rebuilt from y (Vision sometimes splits one
           printed line into two observations), words in reading order; a
           punctuation-only token attaches to the word before it; a word
           hyphenated at a line end is joined to the next row's first word for
           ALIGNMENT only, and remembered as a line-break hyphen.

Method: unique 4-gram anchors on skeletons, chained by longest increasing
subsequence (w18_psalter.anchors), then every gap between anchors is aligned
word by word with difflib, then fuzzy-matched (OCR damage) in order.

Output: <render>/w22_align.json (large, regenerated; not committed) -- one
record per verse with the page, the pivot's word box, the OCR mark there, and
the OCR marks on the verse's other words beside the cell's.

    python3 ingest/w22_align.py
"""
import bisect, difflib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w22_render as R
from w22_scan import eff_h
from w18_psalter import anchors

WORDS = os.path.join(R.OUT, 'w22_words.json')
OUT = os.path.join(R.OUT, 'w22_align.json')
MARKS = ':;.,!?'


def skel(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    w = w.replace('v', 'u').replace('j', 'i').replace('y', 'i')
    w = re.sub(r'(.)\1+', r'\1', w)
    return re.sub(r'e$', '', w)


def split_tok(t):
    """'together:' -> ('together', ':'); ':' -> ('', ':'); "Lord's," -> ("Lord's", ',')."""
    m = re.match(r"^(.*?)([%s\"'’)\]]*)$" % re.escape(MARKS), t)
    core, tail = m.group(1), m.group(2)
    mark = ''.join(c for c in tail if c in MARKS)
    return core, mark


# ---------------------------------------------------------------- witness

def rows_of(page):
    """Vision observations -> printed rows (merge observations whose vertical
    centres are within 40% of a line height), each row's words left to right."""
    # a tall observation (a verse-1 drop capital inside the box) counts as the
    # row at its top (w22_scan.eff_h)
    obs = sorted(page['lines'], key=lambda l: l['y'] + eff_h(l) / 2.0)
    rows = []
    for l in obs:
        c = l['y'] + eff_h(l) / 2.0
        if rows and abs(c - rows[-1]['c']) < 0.4 * max(40, eff_h(l)):
            r = rows[-1]
            r['obs'].append(l)
            r['c'] = (r['c'] + c) / 2.0
        else:
            rows.append({'c': c, 'obs': [l]})
    out = []
    for r in rows:
        ws = []
        for l in sorted(r['obs'], key=lambda l: l['x']):
            ws.extend(l['words'])
        ws.sort(key=lambda w: w[1])
        x0 = min(l['x'] for l in r['obs'])
        x1 = max(l['x'] + l['w'] for l in r['obs'])
        y0 = min(l['y'] for l in r['obs'])
        # the row box is the FULL extent: a crop of a drop-capital row then
        # shows both rows beside the capital, rather than cutting the row
        y1 = max(l['y'] + l['h'] for l in r['obs'])
        out.append({'box': [x0, y0, x1 - x0, y1 - y0], 'words': ws,
                    'text': ' '.join(w[0] for w in ws)})
    return out


HEAD = re.compile(r'P\s*S\s*A\s*L\s*T|\bDA[A-Z]\s*\d', re.I)


def witness():
    """-> list of tokens: {t, core, mark, page, row, box, mbox, eol, hy}.
    Dropped before alignment: the running head (the page's top row when it
    reads as 'THE PSALTER' / 'DAY n'), and border ornament Vision reads as
    letters (any token wholly outside the page's text column)."""
    pages = json.load(open(WORDS))
    toks = []
    for n in sorted(pages, key=int):
        rows = rows_of(pages[n])
        if rows and HEAD.search(rows[0]['text']):
            rows = rows[1:]
        long_rows = [r for r in rows if len(r['words']) >= 6]
        if long_rows:
            lefts = sorted(r['words'][0][1] for r in long_rows)
            rights = sorted(r['words'][-1][1] + r['words'][-1][3] for r in long_rows)
            col_l, col_r = lefts[len(lefts) // 10], rights[-max(1, len(rights) // 10)]
        else:
            col_l, col_r = 0, 10 ** 6
        for ri, row in enumerate(rows):
            ws = [w for w in row['words']
                  if w[1] < col_r + 40 and w[1] + w[3] > col_l - 40]
            for wi, (t, x, y, w, h) in enumerate(ws):
                core, mark = split_tok(t)
                if not re.search(r'[A-Za-z]', core):
                    # punctuation-only token: attach to the previous word
                    pm = ''.join(c for c in t if c in MARKS)
                    if pm and toks and toks[-1]['page'] == int(n) and toks[-1]['row'] == ri:
                        toks[-1]['mark'] += pm
                        toks[-1]['mbox'] = [x, y, w, h]
                    continue
                toks.append({'t': t, 'core': core, 'mark': mark, 'page': int(n),
                             'row': ri, 'box': [x, y, w, h], 'rowbox': row['box'],
                             'mbox': None, 'eol': False, 'hy': False})
            if toks and toks[-1]['page'] == int(n) and toks[-1]['row'] == ri:
                toks[-1]['eol'] = True
    # a word hyphenated at a line end: join it to the next row's first word for
    # alignment (the original token is kept; 'hy' records the break)
    out, k = [], 0
    while k < len(toks):
        t = toks[k]
        if (t['eol'] and t['core'].endswith('-') and k + 1 < len(toks)
                and re.match(r'^[a-z]', toks[k + 1]['core'])
                and (toks[k + 1]['page'], toks[k + 1]['row']) != (t['page'], t['row'])):
            nx = dict(toks[k + 1])
            nx['core'] = t['core'][:-1] + nx['core']
            nx['hy'] = True
            nx['hy_from'] = {'page': t['page'], 'row': t['row'], 'box': t['box'],
                             'rowbox': t['rowbox'], 't': t['t']}
            out.append(nx)
            k += 2
            continue
        out.append(t)
        k += 1
    return out


# ---------------------------------------------------------------- cell

def cell_words():
    """-> verses [(psalm, verse, text)], words [{core, mark, v}] with the
    mediant ':' and every other stop attached to the word before it."""
    cells = w17_cells.cells('1892')
    verses, words = [], []
    for ps in sorted(cells):
        for v in sorted(cells[ps]):
            text = cells[ps][v]
            verses.append((ps, v, text))
            for t in text.split():
                core, mark = split_tok(t)
                if not re.search(r'[A-Za-z]', core):
                    if words and words[-1]['v'] == len(verses) - 1:
                        words[-1]['mark'] += ''.join(c for c in t if c in MARKS)
                        if t == ':':
                            words[-1]['mediant'] = True
                    continue
                words.append({'core': core, 'mark': mark, 'v': len(verses) - 1})
    return verses, words


# ---------------------------------------------------------------- alignment

def align(a_sk, b_sk):
    """-> m[i] = j (cell word i -> witness token j) or None, and kind[i]."""
    chain = anchors(a_sk, b_sk)
    m, kind = [None] * len(a_sk), [None] * len(a_sk)
    for i, j in chain:
        for d in range(4):                       # the anchor 4-gram itself
            if i + d < len(a_sk) and j + d < len(b_sk) and a_sk[i + d] == b_sk[j + d]:
                m[i + d], kind[i + d] = j + d, 'anchor'
    pts = [(-1, -1)] + [(i, m[i]) for i in range(len(a_sk)) if m[i] is not None] \
        + [(len(a_sk), len(b_sk))]
    for (i0, j0), (i1, j1) in zip(pts, pts[1:]):
        if i1 - i0 <= 1 or j1 - j0 <= 1:
            continue
        A, B = a_sk[i0 + 1:i1], b_sk[j0 + 1:j1]
        if len(A) > 400 or len(B) > 400:
            continue
        sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
        for op, a0, a1, b0, b1 in sm.get_opcodes():
            if op == 'equal':
                for d in range(a1 - a0):
                    m[i0 + 1 + a0 + d], kind[i0 + 1 + a0 + d] = j0 + 1 + b0 + d, 'exact'
            elif op == 'replace':
                # OCR damage: pair in order where the skeletons are close
                bb = b0
                for aa in range(a0, a1):
                    for cand in range(bb, b1):
                        r = difflib.SequenceMatcher(None, A[aa], B[cand]).ratio()
                        if r >= 0.67 and len(A[aa]) >= 2:
                            m[i0 + 1 + aa], kind[i0 + 1 + aa] = j0 + 1 + cand, 'fuzzy'
                            bb = cand + 1
                            break
    return m, kind, chain


def main():
    W = witness()
    verses, words = cell_words()
    a_sk = [skel(w['core']) for w in words]
    b_sk = [skel(t['core']) for t in W]
    m, kind, chain = align(a_sk, b_sk)
    by_v = {}
    for i, w in enumerate(words):
        by_v.setdefault(w['v'], []).append(i)
    recs = []
    for vi, (ps, v, text) in enumerate(verses):
        idx = by_v.get(vi, [])
        got = [i for i in idx if m[i] is not None]
        piv = next((i for i in idx if words[i].get('mediant')), None)
        rec = {'psalm': ps, 'verse': v, 'n_words': len(idx),
               'n_matched': len(got), 'placed': len(got) >= max(2, 0.5 * len(idx))}
        if got:
            js = [m[i] for i in got]
            rec['pages'] = sorted({W[j]['page'] for j in js})
            rec['page'] = W[js[0]]['page']
            # every printed row the verse occupies (for a whole-verse crop):
            # from its first matched word's row to its last's, on each page
            rows = {}
            for j in js:
                t = W[j]
                rows[(t['page'], t['row'])] = t['rowbox']
                if t.get('hy_from'):
                    h = t['hy_from']
                    rows[(h['page'], h['row'])] = h['rowbox']
            rec['rows'] = [[pg, ri, bx] for (pg, ri), bx in sorted(rows.items())]
        # the pivot: matched directly, or bracketed by matched neighbours
        jp, how = None, None
        if piv is not None:
            if m[piv] is not None:
                jp, how = m[piv], kind[piv]
            else:
                a = piv - 1 if piv - 1 in idx and m[piv - 1] is not None else None
                b = piv + 1 if piv + 1 in idx and m[piv + 1] is not None else None
                if a is not None and b is not None and m[b] - m[a] == 2:
                    jp, how = m[a] + 1, 'between'
            rec['pivot'] = {'word': words[piv]['core'], 'cell_mark': words[piv]['mark'],
                            'offset': idx.index(piv), 'how': how}
        if jp is not None:
            t = W[jp]
            nxt = W[jp + 1] if jp + 1 < len(W) else None
            prv = W[jp - 1] if jp > 0 else None
            rec['pivot'].update({
                'ocr': t['t'], 'ocr_mark': t['mark'], 'page': t['page'],
                'box': t['box'], 'mbox': t['mbox'], 'rowbox': t['rowbox'],
                'eol': t['eol'], 'hy': t['hy'], 'hy_from': t.get('hy_from'),
                'prev': prv and prv['page'] == t['page'] and prv['row'] == t['row']
                and prv['box'],
                'next': nxt and {'t': nxt['t'], 'page': nxt['page'], 'box': nxt['box'],
                                 'same_row': nxt['page'] == t['page'] and nxt['row'] == t['row']}})
        # every other word: the cell's mark beside the OCR's
        other = []
        for i in got:
            if i == piv:
                continue
            t = W[m[i]]
            cm, om = words[i]['mark'], t['mark']
            if cm != om:
                other.append({'off': idx.index(i), 'word': words[i]['core'],
                              'cell': cm, 'ocr': om, 'page': t['page'],
                              'box': t['box'], 'mbox': t['mbox'], 'rowbox': t['rowbox'],
                              'eol': t['eol'], 'last': i == idx[-1], 'how': kind[i]})
        rec['other'] = other
        recs.append(rec)
    # the confusion of the cell's stop against the OCR's, over every matched
    # word -- the measure of how far the OCR's punctuation can be trusted to
    # FIND anything (it supplies nothing)
    conf = {}
    for i, w in enumerate(words):
        if m[i] is None:
            continue
        last = i + 1 == len(words) or words[i + 1]['v'] != w['v']
        k = '%s|%s|%s' % (w['mark'] or '-', W[m[i]]['mark'] or '-',
                          'end' if last else 'in')
        conf[k] = conf.get(k, 0) + 1
    json.dump(conf, open(OUT.replace('.json', '_conf.json'), 'w'), indent=0, sort_keys=True)
    json.dump(recs, open(OUT, 'w'), separators=(',', ':'))
    placed = sum(r['placed'] for r in recs)
    pv = sum(1 for r in recs if r.get('pivot', {}).get('box'))
    print('witness tokens %d; cell words %d; anchors %d; matched %d (%.1f%%)'
          % (len(W), len(words), len(chain), sum(x is not None for x in m),
             100.0 * sum(x is not None for x in m) / len(words)))
    print('verses %d: placed %d, unplaced %d; pivot located %d, not %d'
          % (len(recs), placed, len(recs) - placed, pv, len(recs) - pv))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
