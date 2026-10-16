"""w22_crops.py -- crops around the cell's mediant, stacked into strips for the eye.

Workstream C. For each verse, w22_align.py has located the PIVOT (the word the
cell's mediant follows) on a 4400px page render. This cuts a tight crop around
the pivot, the mark after it and the next word, with the word before for
context, and stacks a run of them into ONE labelled strip (bin/w22_strip), so
the pointing of many verses can be read by eye in one look. A grey caret
under each crop marks where the cell puts its mediant; nothing is drawn over
the type. (Each crop is labelled with the verse, the page, and the two words
the mark falls between; no caret is drawn, because Vision's word boxes are
estimated within a line and run 30-70px off.) The same machinery crops any other word of a verse (e.g. its last
word, for the verse-final mark).

    python3 ingest/w22_crops.py psalm 1 23 78 [--per=25] [--cols=2]
    python3 ingest/w22_crops.py verses 2:2 2:5 --final [--name=NAME]
    python3 ingest/w22_crops.py verses 10:1 22:5 [--name=NAME]
    python3 ingest/w22_crops.py verses 39:14 100:2 --whole [--name=NAME]
    python3 ingest/w22_crops.py queue      # Phase 1b: all Q2+Q3 verses whole -> mq_NN
    python3 ingest/w22_crops.py q1rest     # Phase 2: the rest of Q1, pivot crops -> q1_NN
Strips go to <render>/strips/.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_render as R

ALIGN = os.path.join(R.OUT, 'w22_align.json')
STRIPS = os.path.join(R.OUT, 'strips')
BIN = os.path.join(HERE, 'bin', 'w22_strip')
PADY, PADX, MINW = 3, 30, 640


def page_png(n):
    return R.page_png(n, 4400)


def rect_around(box, rowbox, prev=None, nxt=None, mbox=None, right_limit=None):
    """A crop: the row's height plus padding; from the word before (or a
    margin) to the word after (or past the mark at a line end)."""
    x, y, w, h = box
    top = rowbox[1] - PADY
    bot = rowbox[1] + rowbox[3] + PADY
    left = (prev[0] if prev else x) - PADX
    end = x + w
    if mbox:
        end = max(end, mbox[0] + mbox[2])
    right = (nxt[0] + nxt[2] if nxt else end + 120) + PADX
    if right_limit:
        right = min(right, right_limit + PADX)
    if right - left < MINW:                       # widen symmetrically
        extra = MINW - (right - left)
        left -= extra // 2
        right += extra - extra // 2
    left = max(0, left)
    return [int(left), int(max(0, top)), int(right - left), int(bot - top)]


def pivot_item(rec, tag=''):
    p = rec['pivot']
    nxt = p['next']['box'] if p.get('next') and p['next'].get('same_row') else None
    row_right = p['rowbox'][0] + p['rowbox'][2]
    rect = rect_around(p['box'], p['rowbox'], p.get('prev') or None, nxt,
                       p.get('mbox'), None if nxt else row_right + 60)
    nw = p['next']['t'] if p.get('next') else ''
    return {'label': '%d:%d p%d%s\n%s | %s' % (rec['psalm'], rec['verse'], p['page'], tag,
                                               p['word'], strip_marks(nw)),
            'png': page_png(p['page']), 'rect': rect}


def word_item(rec, o, tag=''):
    """A crop around one of the verse's other words (from rec['other'])."""
    rect = rect_around(o['box'], o['rowbox'], None, None, o.get('mbox'),
                       o['rowbox'][0] + o['rowbox'][2] + 60)
    return {'label': '%d:%d p%d%s\n%s |' % (rec['psalm'], rec['verse'], o['page'], tag,
                                            o['word']),
            'png': page_png(o['page']), 'rect': rect}


def strip_marks(t):
    return t.strip(':;.,!?')


def whole_items(rec, tag=''):
    """The whole verse: every row it occupies, one crop per page, full column
    width -- for reading where the BOOK puts its marks, not only at the pivot.
    A verse 1 is extended one row upward on its first page, because the row
    beside the drop capital is the one Vision reads worst and the alignment
    may not have matched it."""
    out = []
    pages = sorted({pg for pg, _, _ in rec.get('rows', [])})
    piv = (rec.get('pivot') or {}).get('word', '?')
    for k, pg in enumerate(pages):
        rows = [(ri, bx) for p, ri, bx in rec['rows'] if p == pg]
        top = min(bx[1] for _, bx in rows) - PADY - 4
        bot = max(bx[1] + bx[3] for _, bx in rows) + PADY + 4
        if rec['verse'] == 1 and k == 0:
            top -= 100
        left = min(bx[0] for _, bx in rows) - 80
        right = max(bx[0] + bx[2] for _, bx in rows) + 40
        out.append({'label': '%d:%d p%d%s\npivot: %s' % (rec['psalm'], rec['verse'], pg, tag, piv),
                    'png': page_png(pg),
                    'rect': [int(max(0, left)), int(max(0, top)), int(right - left),
                             int(bot - top)]})
    return out


def strip(items, name, scale=1.0, cols=1):
    os.makedirs(STRIPS, exist_ok=True)
    spec = os.path.join(STRIPS, name + '.json')
    out = os.path.join(STRIPS, name + '.png')
    json.dump(items, open(spec, 'w'))
    subprocess.run([BIN, out, spec, str(scale), str(cols)], check=True)
    return out


def load():
    recs = json.load(open(ALIGN))
    return recs, {(r['psalm'], r['verse']): r for r in recs}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opts = dict(a[2:].split('=', 1) if '=' in a else (a[2:], '1')
                for a in sys.argv[1:] if a.startswith('--'))
    per = int(opts.get('per', 25))
    cols = int(opts.get('cols', 1))
    recs, by = load()
    mode, rest = args[0], args[1:]
    if mode == 'psalm':
        for ps in map(int, rest):
            vs = [r for r in recs if r['psalm'] == ps and r.get('pivot', {}).get('box')]
            miss = [r['verse'] for r in recs if r['psalm'] == ps
                    and not r.get('pivot', {}).get('box')]
            for k in range(0, len(vs), per):
                part = vs[k:k + per]
                name = 'ps%03d_%03d-%03d' % (ps, part[0]['verse'], part[-1]['verse'])
                print(strip([pivot_item(r) for r in part], name, cols=cols),
                      ('(pivot not located: %s)' % miss) if miss else '')
    elif mode == 'queue':
        # Phase 1b: every Q2+Q3 verse (w22_firstpass.tsv), whole-verse crops,
        # packed into strips of at most ~2300px -> mq_NN.png + mq_index.txt
        refs = [l.split('\t')[0] for l in open(os.path.join(HERE, 'w22_firstpass.tsv'))
                if not l.startswith('#') and l.split('\t')[2] in ('Q2', 'Q3')]
        groups, cur = [], []
        for ref in refs:
            it = whole_items(by[tuple(map(int, ref.split(':')))])
            if cur and sum(i['rect'][3] for i in cur) + sum(i['rect'][3] for i in it) > 2300:
                groups.append(cur); cur = []
            cur.extend(it)
        if cur:
            groups.append(cur)
        for k, g in enumerate(groups):
            strip(g, 'mq_%02d' % k)
        open(os.path.join(STRIPS, 'mq_index.txt'), 'w').write('\n'.join(
            ' '.join(sorted({i['label'].split(' ')[0] for i in g},
                            key=lambda r: tuple(map(int, r.split(':'))))) for g in groups))
        print('%d verses in %d strips' % (len(refs), len(groups)))
    elif mode == 'q1rest':
        # Phase 2 (R21): the full eye pass -- every Q1 verse not already read by
        # eye in Phase 1 (prototype pivot strips) or Phase 1b (control), pivot
        # crops, 40 per strip in 2 columns -> q1_NN.png + q1_index.json
        import w22_eye_2
        refs = w22_eye_2.q1_rest()
        index = []
        for k in range(0, len(refs), 40):
            part = refs[k:k + 40]
            items = [pivot_item(by[tuple(map(int, r.split(':')))]) for r in part]
            strip(items, 'q1_%02d' % (k // 40), cols=2)
            index.append(part)
        json.dump(index, open(os.path.join(STRIPS, 'q1_index.json'), 'w'))
        print('%d verses in %d strips' % (len(refs), len(index)))
    elif mode == 'verses':
        items = []
        for ref in rest:
            ps, v = map(int, ref.split(':'))
            r = by[(ps, v)]
            if 'whole' in opts:
                items.extend(whole_items(r))
            elif 'final' in opts:
                o = next((o for o in r['other'] if o['last']), None)
                if o:
                    items.append(word_item(r, o, ' end'))
            elif r.get('pivot', {}).get('box'):
                items.append(pivot_item(r))
        name = opts.get('name', 'verses')
        for k in range(0, len(items), per):
            print(strip(items[k:k + per], '%s_%02d' % (name, k // per), cols=cols))


if __name__ == '__main__':
    main()
