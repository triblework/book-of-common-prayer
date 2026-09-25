"""w20_kal_strips.py -- first machine read of the 1662 Kalendar (Wave 20).

Each month is one page of the Annexed Book (PDF pp. 44-55). Whole-page OCR
reads barely a third of a ruled table, so each page is DESKEWED and its
column rules found by bin/w20_grid (dark-pixel projections), and then each of
the nine columns is cropped to a vertical strip and OCR'd on its own with
bin/w17_ocrbox. Every line keeps its y in page coordinates: rows are
recovered from pixel position, never from text order.

June (p. 49) is read from Wikimedia's own rendering of the same file, since
the local JBIG2 decoder cannot draw that page (RULINGS R14).

    python3 ingest/w20_kal_strips.py      -> ingest/w20_kal_ocr.json
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w18_render as R

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, 'bin')
PAGES = dict(zip(range(44, 56), ['January', 'February', 'March', 'April', 'May',
                                  'June', 'July', 'August', 'September',
                                  'October', 'November', 'December']))
COLS = ['golden', 'day', 'letter', 'roman', 'note', 'm1', 'm2', 'e1', 'e2']
# Offsets of the ten rules from the left frame, measured on the pages where
# all ten are detected; used ONLY to fill a rule the projection missed.
TYPICAL = [0, 151, 246, 341, 604, 1183, 1376, 1569, 1763, 1968]


def rules(g):
    xs = []
    for a, b, _ in g['vruns']:
        c = (a + b) // 2
        if xs and c - xs[-1] < 12:          # one rule detected twice
            continue
        xs.append(c)
    if len(xs) == 10:
        return xs, []
    # fill the missing rule(s) at the typical offset from the left frame
    left, filled = xs[0], []
    out = []
    for off in TYPICAL:
        want = left + off
        near = [x for x in xs if abs(x - want) < 40]
        if near:
            out.append(near[0])
        else:
            out.append(want); filled.append(want)
    return out, filled


def body(g):
    hs = [(a + b) // 2 for a, b, _ in g['hruns']]
    top = max(h for h in hs if h < 1500)
    if top < 1400:                          # the '1. Lesson' rule not detected
        top += 140
    bot = min(h for h in hs if h > 3300)
    return top + 6, bot - 6


def main():
    grids = {}
    for line in open(os.path.join(HERE, 'w20_grids.raw')):
        p, j = line.split(': ', 1)
        grids[int(p.strip('"'))] = json.loads(j)
    out = {}
    for page, month in PAGES.items():
        g = grids[page]
        xs, filled = rules(g)
        top, bot = body(g)
        png = os.path.join(R.OUT, 'd%04d.png' % page)
        cols = {}
        for i, name in enumerate(COLS):
            x0, x1 = xs[i + 0] + 7, xs[i + 1] - 7
            crop = R.crop(png, top, x0, bot - top, x1 - x0, scale=2)
            d = json.loads(subprocess.run([os.path.join(BIN, 'w17_ocrbox'), crop],
                                          capture_output=True, text=True).stdout)
            cols[name] = [{'t': l['t'], 'y': top + l['y'] // 2, 'h': l['h'] // 2,
                           'x': x0 + l['x'] // 2} for l in d['lines']]
        out[page] = {'month': month, 'angle': g['angle'], 'rules': xs,
                     'filled': filled, 'top': top, 'bot': bot, 'cols': cols}
        print(page, month, 'rules', len(xs), 'filled', filled, 'body', top, bot,
              {k: len(v) for k, v in cols.items()})
    json.dump(out, open(os.path.join(HERE, 'w20_kal_ocr.json'), 'w'), indent=0,
              ensure_ascii=False)


if __name__ == '__main__':
    main()
