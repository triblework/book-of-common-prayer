"""w21_scan.py -- OCR the 1928 American page scans, book page by book page
(Workstream B).

Each scan page of these PDFs is a two-page SPREAD. Lines are assigned to the
left or right book page by their pixel boxes, never by OCR text order: the
gutter is the x in the middle fifth of the spread that the fewest OCR line
boxes cross (the centre of the widest such run), and a line belongs to the
side its box centre falls on. Lines that straddle the gutter are counted.

Two modes:
    spread   OCR the whole rendered spread once (bin/w17_ocrbox) and split it;
    halves   do that to find the gutter, then crop each book page out of the
             render at the gutter and OCR the crop on its own (the record keeps
             the half-page OCR; coordinates are put back in spread pixels).

Within a book page, Vision's observations are merged into printed lines by
their vertical centres (a verse number or a mark Vision returns as a separate
box joins the line it sits on), then ordered top to bottom.

Writes ingest/w21_<pdf>_ocr.json (or --name):
    {"<scan page>": {"w":W, "h":H, "gutter":g, "straddle":k, "mode":m,
                     "L": [[text, x, y, w, h], ...], "R": [...]}}

    python3 ingest/w21_scan.py --pdf 1952 --size 4400 --mode halves 203-295
    python3 ingest/w21_scan.py --pdf 1929 --size 4400 --mode halves 192-284

Vision runs with language correction OFF (w17_ocr.swift), so the page's own
spelling survives. A page or half with 0 lines is listed at the end of every
run: it must be rendered another way (w21_render --method sips) and LOOKED AT
before it is called blank (Wave 20, Annexed Book p. 49).
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w21_render as R

HERE = os.path.dirname(os.path.abspath(__file__))
BOX = os.path.join(HERE, 'bin', 'w17_ocrbox')
BATCH = 6


def ocrbox(pngs):
    out = subprocess.run([BOX] + pngs, capture_output=True, text=True).stdout
    got = {}
    for line in out.strip().split('\n'):
        if line.strip():
            d = json.loads(line)
            got[d['path']] = d
    return [got.get(p, {'path': p, 'w': 0, 'h': 0, 'lines': []}) for p in pngs]


def gutter(d):
    W = d['w']
    lo, hi = int(W * 0.4), int(W * 0.6)
    best, runs, cur = None, [], None
    counts = []
    for x in range(lo, hi, 4):
        c = sum(1 for l in d['lines'] if l['x'] < x < l['x'] + l['w'])
        counts.append((x, c))
    m = min(c for _, c in counts)
    for x, c in counts:
        if c == m:
            cur = [x, x] if cur is None else [cur[0], x]
        elif cur is not None:
            runs.append(cur); cur = None
    if cur is not None:
        runs.append(cur)
    a, b = max(runs, key=lambda r: r[1] - r[0])
    return (a + b) // 2, m


def merge(lines):
    """Observations -> printed lines (by vertical centre), top to bottom."""
    if not lines:
        return []
    hs = sorted(l['h'] for l in lines)
    tol = hs[len(hs) // 2] * 0.5
    rows = []
    for l in sorted(lines, key=lambda l: l['y'] + l['h'] / 2.0):
        c = l['y'] + l['h'] / 2.0
        if rows and abs(c - rows[-1]['c']) <= tol:
            rows[-1]['obs'].append(l)
            n = len(rows[-1]['obs'])
            rows[-1]['c'] = (rows[-1]['c'] * (n - 1) + c) / n
        else:
            rows.append({'c': c, 'obs': [l]})
    out = []
    for r in rows:
        obs = sorted(r['obs'], key=lambda l: l['x'])
        x0 = min(l['x'] for l in obs); y0 = min(l['y'] for l in obs)
        x1 = max(l['x'] + l['w'] for l in obs); y1 = max(l['y'] + l['h'] for l in obs)
        out.append([' '.join(l['t'] for l in obs), x0, y0, x1 - x0, y1 - y0])
    return out


def record(which, n, size, mode, method):
    png = R.page_png(which, n, size, method)
    d = ocrbox([png])[0]
    g, k = gutter(d) if d['lines'] else (d['w'] // 2, 0)
    rec = {'w': d['w'], 'h': d['h'], 'gutter': g, 'straddle': k, 'mode': mode,
           'method': method}
    if mode == 'spread':
        L = [l for l in d['lines'] if l['x'] + l['w'] / 2.0 < g]
        Rr = [l for l in d['lines'] if l['x'] + l['w'] / 2.0 >= g]
    else:
        lp, ly, lx = R.crop_at(png, 0, 0, d['h'], g, tag='_L')
        rp, ry, rx = R.crop_at(png, 0, g, d['h'], d['w'] - g, tag='_R')
        dl, dr = ocrbox([lp, rp])
        L = [dict(l, x=l['x'] + lx, y=l['y'] + ly) for l in dl['lines']]
        Rr = [dict(l, x=l['x'] + rx, y=l['y'] + ry) for l in dr['lines']]
        os.remove(lp); os.remove(rp)
    rec['L'], rec['R'] = merge(L), merge(Rr)
    return rec


def main(argv):
    which, size, mode, method, name = '1952', 4400, 'halves', 'ql', None
    pages = []
    while argv:
        a = argv.pop(0)
        if a.startswith('--'):
            k, v = (a.split('=', 1) if '=' in a else (a, argv.pop(0)))
            if k == '--pdf': which = v
            elif k == '--size': size = int(v)
            elif k == '--mode': mode = v
            elif k == '--method': method = v
            elif k == '--name': name = v
            else: raise SystemExit('unknown option ' + k)
        else:
            lo, _, hi = a.partition('-')
            pages += range(int(lo), int(hi or lo) + 1)
    path = os.path.join(HERE, name or 'w21_%s_ocr.json' % which)
    rec = json.load(open(path)) if os.path.exists(path) else {}
    todo = [n for n in pages if str(n) not in rec]
    for i, n in enumerate(todo):
        rec[str(n)] = record(which, n, size, mode, method)
        if (i + 1) % BATCH == 0 or i + 1 == len(todo):
            json.dump(rec, open(path, 'w'), indent=0, sort_keys=True)
            print('%d/%d  page %d' % (i + 1, len(todo), n), flush=True)
    empty = ['%s%s' % (n, s) for n in pages for s in 'LR'
             if not rec.get(str(n), {}).get(s)]
    print('pages %d; halves with 0 lines: %s' % (len(pages), empty or 'none'))


if __name__ == '__main__':
    main(sys.argv[1:])
