"""w24_measure.py -- a pixel check on the eye reads of w24_eye.txt: is the s
after small-capital LORD's apostrophe a LOWER-CASE s or a small-capital S?
Wave 24; authoring-only.

For each window marked on the crops of w24_possessive.py (WINDOWS), the page
render (4400px) is read as a bitmap (sips -> BMP; no imaging library is
installed), the ink split into connected components (an i's dot joined to its
stem), the row's glyphs grouped into words, and each word ending <glyphs>
<apostrophe> <glyph> reported: every glyph's top, bottom, height and width,
the word before it, and every s of "is"/"his"/"this" on the same row, with the
bitmap overlap of the possessive's s against each.

What it showed (2026-11-06): this face's small capitals stand AT the x-height
(11:4: O R D tops 762, the e of "the" 763, the s 765), so height cannot tell
the two forms apart; on 56:10's row "God's" and "LORD's" end in s's of the
same size (38 x 30 px). The grouping finds the possessive in 8 of the 11
rows (27:16, 116:16, 118:23 merge or split glyphs at these thresholds): its s
is 35-38 px high and 27-30 wide; the s of "is" on three of those rows (22:28,
24:1, 137:4) 35-36 by 28-29. It is the same
witness read a second way (R14) and settles nothing alone; the reading is the
eye's (w24_eye.txt).

    W22_RENDER=<dir> python3 ingest/w24_measure.py   # after w24_possessive.py
"""
import collections, json, os, struct, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_render as R

INK = 128


def bitmap(png):
    bmp = png[:-4] + '.bmp'
    if not os.path.exists(bmp):
        subprocess.run(['sips', '-s', 'format', 'bmp', png, '--out', bmp],
                       check=True, capture_output=True)
    data = open(bmp, 'rb').read()
    off = struct.unpack_from('<I', data, 10)[0]
    w, h = struct.unpack_from('<ii', data, 18)
    bpp = struct.unpack_from('<H', data, 28)[0]
    step = bpp // 8
    stride = (w * step + 3) & ~3
    top_down = h < 0
    h = abs(h)

    def ink(x, y):
        r = y if top_down else h - 1 - y
        i = off + r * stride + x * step
        b, g, rr = data[i], data[i + 1], data[i + 2]
        return (rr * 299 + g * 587 + b * 114) // 1000 < INK
    return w, h, ink


def components(ink, x0, y0, x1, y1):
    seen = set()
    out = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if (x, y) in seen or not ink(x, y):
                continue
            stack, pts = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                pts.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1),
                               (cx + 1, cy + 1), (cx - 1, cy - 1), (cx + 1, cy - 1), (cx - 1, cy + 1)):
                    if x0 <= nx < x1 and y0 <= ny < y1 and (nx, ny) not in seen and ink(nx, ny):
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            if len(pts) < 12:                      # specks
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            out.append({'l': min(xs), 'r': max(xs), 't': min(ys), 'b': max(ys), 'n': len(pts)})
    return sorted(out, key=lambda c: c['l'])


def merge_columns(comps):
    """An i's (or j's) dot is one glyph with its stem: merge a SMALL component
    into the one it sits directly above, sharing columns; so is a small piece
    broken off a letter of the bitonal scan (inside its height, sharing
    columns). Nothing else is
    merged -- kerned letters share columns too -- so an apostrophe, which
    sits over no stem, stays a glyph of its own."""
    def small(c):
        return (c['b'] - c['t'] + 1) <= 16 and (c['r'] - c['l'] + 1) <= 16
    out = []
    for c in comps:
        o = out[-1] if out else None
        inside = lambda a, z: a['t'] >= z['t'] and a['b'] <= z['b']   # a broken-off piece
        if o and c['l'] <= o['r'] and o['l'] <= c['r'] and (
                (small(o) and (o['b'] < c['t'] or inside(o, c)))
                or (small(c) and (c['b'] < o['t'] or inside(c, o)))):
            out[-1] = {'l': min(o['l'], c['l']), 'r': max(o['r'], c['r']), 't': min(o['t'], c['t']),
                       'b': max(o['b'], c['b']), 'n': o['n'] + c['n'], 'parts': o.get('parts', 1) + 1}
        else:
            out.append(dict(c))
    return out


# Windows marked by eye on the crops of w24_possessive.py, in CROP pixels:
# (x0, x1, y) -- the span of "the LORD's" and a point on its row. Two
# comparison words a lower-case 's ends: 56:10 "God's" (same row), 147:10
# "man's" (the row above 147:11).
WINDOWS = {
    '11:4': [(1230, 1740, 125)], '22:28': [(840, 1260, 195)], '24:1': [(505, 935, 150)],
    '27:16': [(430, 830, 195)], '56:10': [(1270, 1740, 190), (200, 430, 190)],
    '113:3': [(100, 500, 195)], '115:16': [(1070, 1530, 190)], '116:16': [(980, 1420, 195)],
    '118:23': [(430, 860, 190)], '137:4': [(800, 1280, 190)],
    '147:11': [(325, 780, 195), (1200, 1470, 120)],
}


def band(ink, x0, x1, y, reach=70):
    """The contiguous run of inked pixel rows, within [x0, x1), that holds y."""
    rows = {yy: any(ink(xx, yy) for xx in range(x0, x1, 1)) for yy in range(y - reach, y + reach)}
    lo = hi = y
    while not rows.get(lo, True) and lo > y - reach:
        lo -= 1                        # y fell between glyphs: find ink nearby
    while rows.get(lo - 1):
        lo -= 1
    while rows.get(hi + 1):
        hi += 1
    return lo, hi + 1


def words_of(comps, gap=16):
    out = []
    for c in comps:
        if out and c['l'] - out[-1][-1]['r'] <= gap:
            out[-1].append(c)
        else:
            out.append([c])
    return out


def g(c):
    return {'top': c['t'], 'bottom': c['b'], 'h': c['b'] - c['t'] + 1, 'w': c['r'] - c['l'] + 1,
            'x': c['l']}


def glyph_bits(ink, c):
    return {(x - c['l'], c['b'] - y) for y in range(c['t'], c['b'] + 1)
            for x in range(c['l'], c['r'] + 1) if ink(x, y)}


def iou(a, b):
    """Best overlap of two glyph bitmaps (aligned at baseline and left edge,
    shifted up to 3px either way): |a & b| / |a | b|."""
    best = 0.0
    for dx in range(-3, 4):
        for dy in range(-2, 3):
            bb = {(x + dx, y + dy) for x, y in b}
            best = max(best, len(a & bb) / len(a | bb))
    return best


def measure(ink, x0, x1, y, line):
    """The printed row through (x0..x1, y): -> for each word in the window that
    ends <glyphs> <apostrophe> <glyph>, its glyphs, the apostrophe, the s and
    the word before it; and every s of "is"/"his"/"this" on the whole row
    (a word ending <i> <s>), with each s's bitmap overlap against them."""
    t, b = band(ink, x0, x1, y)
    lx0, lx1 = line
    # the whole row: room above for taller glyphs and below for descenders;
    # what hangs into the band from the row above (it ends near the top) is dropped
    comps = [c for c in components(ink, lx0, t - 14, lx1, b + 20) if c['b'] > t + 10]
    comps = merge_columns(comps)
    ws = []
    for wd in words_of(comps):
        while len(wd) > 1 and (wd[-1]['r'] - wd[-1]['l'] + 1) < 14:
            wd = wd[:-1]                           # a stop set close: , ; : .
        ws.append(wd)
    refs = []
    for wd in ws:
        if len(wd) >= 2 and wd[-2].get('parts') == 2 and (wd[-2]['r'] - wd[-2]['l']) < 22:
            refs.append(wd[-1])                    # the s of is / his / this
    out = []
    for k, wd in enumerate(ws):
        if len(wd) < 4 or not (x0 <= wd[0]['l'] < x1):
            continue
        ap = wd[-2]
        tops = sorted(c['t'] for c in wd[:-2])
        bots = sorted(c['b'] for c in wd[:-2])
        mid = (tops[len(tops) // 2] + bots[len(bots) // 2]) / 2
        if ap.get('parts') or ap['b'] > mid or (ap['b'] - ap['t'] + 1) > 0.7 * (bots[-1] - tops[-1] + 1):
            continue
        sb = glyph_bits(ink, wd[-1])
        out.append({'band': [t, b], 'word': [g(c) for c in wd[:-2]], 'apostrophe': g(ap),
                    's': g(wd[-1]), 'prev_word': [g(c) for c in ws[k - 1]] if k else [],
                    'refs': [dict(g(r), iou=round(iou(sb, glyph_bits(ink, r)), 3)) for r in refs],
                    'ref_pair_iou': (round(iou(glyph_bits(ink, refs[0]), glyph_bits(ink, refs[1])), 3)
                                     if len(refs) > 1 else None)})
    return out


def main():
    out = R.OUT + '/w24'
    rec = {r['verse']: r for r in json.load(open(os.path.join(out, 'w24_locate.json')))}
    res = []
    for ref, wins in WINDOWS.items():
        r = rec[ref]
        left, top = r['crop'][:2]
        _, _, ink = bitmap(R.page_png(r['page'], 4400))
        for x0, x1, y in wins:
            for f in measure(ink, left + x0, left + x1, top + y, (left, left + r['crop'][2])):
                f.update({'verse': ref, 'page': r['page']})
                res.append(f)
                pw, wd, s = f['prev_word'], f['word'], f['s']
                print('%-7s p%d  prev tops %-14s | word tops %-18s bottoms %-18s | s top %d bot %d '
                      'h %d w %d | is-s %s | ref pair %s'
                      % (ref, r['page'], ' '.join(str(c['top']) for c in pw),
                         ' '.join(str(c['top']) for c in wd), ' '.join(str(c['bottom']) for c in wd),
                         s['top'], s['bottom'], s['h'], s['w'],
                         ' '.join('t%d/h%d/w%d/%.2f' % (q['top'], q['h'], q['w'], q['iou'])
                                  for q in f['refs']), f['ref_pair_iou']))
    json.dump(res, open(os.path.join(out, 'w24_measure.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
