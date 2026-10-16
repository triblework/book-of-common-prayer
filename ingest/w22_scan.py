"""w22_scan.py -- the 1892 Psalter's page OCR at 4400px, with geometry.

Workstream C. Wave 17's page record (w17_scan_ocr.json) was read at 2400px and
keeps text only, no boxes; a verse-by-verse pointing collation needs to know
WHERE each word sits on the page, so the Psalter (scan pages 357-536) is read
again at 4400px with bin/w22_ocr (Vision, Wave 17's settings, line AND word
boxes in one pass).

Outputs:
  ingest/w22_scan_ocr.json   the witness record kept in the repo: per page,
                             [[text, x, y, w, h], ...] for every line, in pixels
                             of the 4400px render (origin top-left), top to bottom.
  <render>/w22_words.json    the same pass with every word's box (large; it is
                             regenerated, never committed).

A second stage REPAIRS the page read where Vision is known to fail, by
re-reading BANDS of the page on their own (each band cropped out of the same
4400px render and OCR'd alone -- a second read of the same image, never a
second witness, R14):
  * a vertical GAP between consecutive rows wider than 1.5 line pitches (Vision
    drops about one line in forty here) -- the band between them is re-read;
  * a TALL observation (>= 140px) is nearly always the FIRST row of a verse 1
    with its two-line drop capital inside the box; Vision reads the row well
    and the second row separately. Splitting it into bands was tried and read
    worse (bands cut the row), so a tall observation is kept and treated, for
    row order and gap finding, as one row at its top (TALL_ROW px high); if
    the second row is missing, the gap rule re-reads it.
In the record a line's sixth field says where it came from: 'p' the page read,
'b' a band re-read of a gap.

Every page that reads to FEW lines (< 15; a full Psalter page reads ~38) is
reported; a page that reads to 0 is rendered a second way (5000px, then
`sips` re-encoding of the 4400 render) and read again before anyone calls it
blank (Wave 20's June page).

    python3 ingest/w22_scan.py [FIRST LAST]
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_render as R

BIN = os.path.join(HERE, 'bin', 'w22_ocr')
REC = os.path.join(HERE, 'w22_scan_ocr.json')
WORDS = os.path.join(R.OUT, 'w22_words.json')
SIZE = 4400
BATCH = 10


def ocr(pngs):
    env = dict(os.environ)
    out = subprocess.run([BIN] + pngs, capture_output=True, text=True,
                         env=env, check=True).stdout
    return [json.loads(l) for l in out.strip().split('\n') if l.strip()]


def second_look(n):
    """A page that read to nothing: render it two other ways and read again."""
    tries = []
    p5 = R.page_png(n, 5000)
    tries.append(('qlmanage 5000px', p5))
    p44 = R.page_png(n, SIZE)
    alt = p44[:-4] + '_sips.png'
    subprocess.run(['sips', '-s', 'format', 'png', '-s', 'formatOptions', 'best',
                    p44, '--out', alt], check=True, capture_output=True)
    tries.append(('sips re-encode', alt))
    res = []
    for how, png in tries:
        d = ocr([png])[0]
        res.append((how, len(d['lines'])))
    return res


def dump(rec):
    """One page per line, pages in order, so a re-read diffs page by page."""
    with open(REC, 'w', encoding='utf-8') as fh:
        fh.write('{\n' + ',\n'.join(
            '%s:%s' % (json.dumps(k), json.dumps(rec[k], separators=(',', ':'),
                                                ensure_ascii=False))
            for k in sorted(rec, key=int)) + '\n}\n')


TALL, TALL_ROW = 140, 85


def eff_h(l):
    """A tall observation (drop capital inside the box) counts as its top row."""
    return TALL_ROW if l['h'] >= TALL else l['h']


def rows_of(lines):
    """Vision observations -> printed rows: observations whose vertical centres
    lie within 40% of a line height are one row. -> [[obs, ...], ...] top-down."""
    obs = sorted(lines, key=lambda l: l['y'] + eff_h(l) / 2.0)
    rows = []
    for l in obs:
        c = l['y'] + eff_h(l) / 2.0
        if rows and abs(c - rows[-1][0]) < 0.4 * max(40, eff_h(l)):
            rows[-1][1].append(l)
            rows[-1][0] = (rows[-1][0] + c) / 2.0
        else:
            rows.append([c, [l]])
    return [r[1] for r in rows]


PITCH = 73          # median row pitch at 4400px (measured over the Psalter)


def repair(n, d):
    """Re-read the gaps of page n as bands. -> new line list, each line
    carrying 'src' ('p' page read, 'b' band re-read)."""
    lines = [dict(l, src='p') for l in d['lines']]
    body = [l for l in lines if l['w'] > 300]          # text rows, not folios
    if not body:
        return lines
    x0 = min(l['x'] for l in body) - 30
    x1 = max(l['x'] + l['w'] for l in body) + 30
    bands = []                                          # (top, height)
    rows = rows_of(lines)
    for a, b in zip(rows, rows[1:]):
        bot = max(l['y'] + eff_h(l) for l in a)
        top = min(l['y'] for l in b)
        if top - min(l['y'] for l in a) > 1.5 * PITCH and top - bot > 30:
            bands.append((bot - 6, top - bot + 12))
    if not bands:
        return lines
    png = R.page_png(n, SIZE)
    bdir = os.path.join(R.OUT, 'bands')
    os.makedirs(bdir, exist_ok=True)
    crops = []
    for i, (top, h) in enumerate(bands):
        out = os.path.join(bdir, 'p%04d_b%02d.png' % (n, i))
        R.crop(png, max(0, top), max(0, x0), h, x1 - x0, out=out)
        crops.append(out)
    got = ocr(crops)
    added = []
    for (top, h), g in zip(bands, got):
        for l in g['lines']:
            if not re.search(r'[A-Za-z]{2}', l['t']):
                continue
            nl = {'t': l['t'], 'x': l['x'] + x0, 'y': l['y'] + max(0, top),
                  'w': l['w'], 'h': l['h'], 'src': 'b',
                  'words': [[w[0], w[1] + x0, w[2] + max(0, top), w[3], w[4]]
                            for w in l['words']]}
            # a band line that merely repeats a row the page read already has
            # (the band's padding can catch the edge of a neighbouring row)
            if any(abs((o['y'] + eff_h(o) / 2.0) - (nl['y'] + nl['h'] / 2.0)) < 30
                   for o in lines):
                continue
            added.append(nl)
    return sorted(lines + added, key=lambda l: l['y'])


def main():
    first, last = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 \
        else (R.FIRST, R.LAST)
    rec = json.load(open(REC)) if os.path.exists(REC) else {}
    words = json.load(open(WORDS)) if os.path.exists(WORDS) else {}
    todo = [n for n in range(first, last + 1) if str(n) not in words]
    for k in range(0, len(todo), BATCH):
        batch = todo[k:k + BATCH]
        pngs = [R.page_png(n, SIZE) for n in batch]
        for n, d in zip(batch, ocr(pngs)):
            words[str(n)] = {'w': d['w'], 'h': d['h'], 'lines': d['lines']}
        dump(rec)
        json.dump(words, open(WORDS, 'w'), separators=(',', ':'))
        print('pages %d-%d done (%d/%d)' % (batch[0], batch[-1], k + len(batch), len(todo)),
              flush=True)
    # stage 2: band re-reads (idempotent: always from the page read alone)
    nb = 0
    for n in range(first, last + 1):
        d = words[str(n)]
        page_lines = [l for l in d['lines'] if l.get('src', 'p') in ('p', 'x')]
        fixed = repair(n, {'lines': [{k: v for k, v in l.items() if k != 'src'}
                                     for l in page_lines]})
        nb += sum(1 for l in fixed if l['src'] == 'b')
        d['lines'] = fixed
        rec[str(n)] = [[l['t'], l['x'], l['y'], l['w'], l['h'], l['src']] for l in fixed]
    dump(rec)
    json.dump(words, open(WORDS, 'w'), separators=(',', ':'))
    print('band re-reads added %d lines' % nb)
    few = {n: len(v) for n, v in rec.items() if len(v) < 15}
    print('pages read: %d; lines: %d; pages with < 15 lines: %s'
          % (len(rec), sum(len(v) for v in rec.values()), few))
    for n, k in sorted(few.items()):
        if k == 0:
            print('  p%s read 0 lines -- second look: %s' % (n, second_look(int(n))))


if __name__ == '__main__':
    main()
