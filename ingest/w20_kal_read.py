"""w20_kal_read.py -- two machine reads of every 1662 Kalendar cell (Wave 20).

For each month page, and for each of two renderings of the Annexed Book PDF:

  A  the local render (pypdf split -> Quick Look, 4400px; w18_render), and
  B  Wikimedia's server-side render of the same file (1920px, fetched by
     w20_fetch and scaled to the same frame) -- a second DECODING of the one
     witness, not a second witness (RULINGS R14). June has only B.

the page is deskewed and its ten column rules found (bin/w20_grid), the
Roman-date column is OCR'd as a strip to give one y per day (it prints exactly
one entry per civil day, so it is the row index; February's unprinted 29th
row is placed one pitch below the 28th), and then every cell -- row band x
column band -- is cut out and OCR'd on its own (bin/w20_cells). Nothing is
taken from text order.

    python3 ingest/w20_kal_read.py      -> ingest/w20_kal_reads.json
"""
import json, os, statistics, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w18_render as R

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, 'bin')
PG = os.path.join(HERE, 'pages-1662')
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
ROWS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]   # Feb prints a 29th row
COLS = ['golden', 'day', 'letter', 'roman', 'note', 'm1', 'm2', 'e1', 'e2']
TYPICAL = [0, 151, 246, 341, 604, 1183, 1376, 1569, 1763, 1968]


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


def grid(src, dst):
    return json.loads(run(os.path.join(BIN, 'w20_grid'), src, dst))


def rules(g):
    xs = []
    for a, b, _ in g['vruns']:
        c = (a + b) // 2
        if xs and c - xs[-1] < 12:
            continue
        xs.append(c)
    left, out, filled = xs[0], [], []
    for off in TYPICAL:
        want = left + off
        near = [x for x in xs if abs(x - want) < 40]
        out.append(near[0] if near else want)
        if not near:
            filled.append(want)
    return out, filled


def body(g):
    hs = [(a + b) // 2 for a, b, _ in g['hruns']]
    top = max(h for h in hs if h < 1500)
    if top < 1400:
        top += 140
    return top + 6, min(h for h in hs if h > 3300) - 6


def rows_from_roman(png, xs, top, bot, n):
    crop = R.crop(png, top, xs[3] + 7, bot - top, xs[4] - xs[3] - 14, scale=2)
    d = json.loads(run(os.path.join(BIN, 'w17_ocrbox'), crop))
    ys = sorted(top + (l['y'] + l['h'] // 2) // 2 for l in d['lines'])
    # merge detections closer than a third of a row
    merged = []
    for y in ys:
        if merged and y - merged[-1] < 20:
            continue
        merged.append(y)
    pitch = statistics.median(b - a for a, b in zip(merged, merged[1:]))
    note = ''
    if len(merged) != n:
        # rebuild a regular ladder anchored on the detections, then snap
        y0 = merged[0]
        ladder = [y0 + round(k * pitch) for k in range(n)]
        snapped = []
        for y in ladder:
            near = [m for m in merged if abs(m - y) < pitch / 3]
            snapped.append(near[0] if near else y)
        note = 'roman strip gave %d rows for %d; ladder pitch %.1f' % (len(merged), n, pitch)
        merged = snapped
    return merged, pitch, note


def read(png, g, n):
    xs, filled = rules(g)
    top, bot = body(g)
    ys, pitch, note = rows_from_roman(png, xs, top, bot, n)
    half = int(pitch * 0.55)
    rects = [[xs[i] + 5, y - half, xs[i + 1] - xs[i] - 10, 2 * half]
             for y in ys for i in range(9)]
    rp = png[:-4] + '_rects.json'
    json.dump(rects, open(rp, 'w'))
    cells = json.loads(run(os.path.join(BIN, 'w20_cells'), png, rp))
    rows = [{'y': y, 'cells': {c: cells[k * 9 + i]['t'] for i, c in enumerate(COLS)}}
            for k, y in enumerate(ys)]
    return {'rules': xs, 'filled': filled, 'angle': g['angle'], 'top': top,
            'bot': bot, 'pitch': pitch, 'note': note, 'rows': rows}


def main():
    out = {}
    for k, month in enumerate(MONTHS):
        page = 44 + k
        rec = {'month': month, 'page': page}
        for tag, src in (('A', 'p%04d_4400.png' % page), ('B', 'c%04d_4400.png' % page)):
            if tag == 'A' and page == 49:
                continue          # the local decoder draws June blank (R14)
            dst = os.path.join(PG, '%s%04d_desk.png' % (tag, page))
            g = grid(os.path.join(PG, src), dst)
            rec[tag] = read(dst, g, ROWS[k])
            print(page, month, tag, 'angle', g['angle'], 'filled', rec[tag]['filled'],
                  'rows', len(rec[tag]['rows']), rec[tag]['note'])
        out[page] = rec
    json.dump(out, open(os.path.join(HERE, 'w20_kal_reads.json'), 'w'),
              indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
