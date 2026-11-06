"""w24_possessive.py -- crops of the 11 possessives of small-capital LORD in
the 1892 Psalter, for the eye. Wave 24; authoring-only.

The cells print the possessive "LORD'S" (one with a curly apostrophe, 147:11);
Wave 22 read one of them (24:1) as small-capital LORD with a LOWER-CASE s and
left the rest unkeyed, as an encoding question (RULINGS R23). This finds each
one's printed row on the 4400px page render -- the committed line record
w22_scan_ocr.json says WHERE; it supplies no reading -- and crops:

  <out>/pos_<psalm>_<verse>.png     the row with the row above and below
  <out>/pos_<psalm>_<verse>_z.png   the row alone, enlarged 2x

Each crop is labelled (file name) with the verse only, never with what to
expect. The eye reads go into w24_eye.txt; w24_keys.py keys them.

    W22_RENDER=<dir> python3 ingest/w24_possessive.py [--out=DIR]
"""
import difflib, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w22_render as R

TARGETS = ['11:4', '22:28', '24:1', '27:16', '56:10', '113:3', '115:16',
           '116:16', '118:23', '137:4', '147:11']
POSS = re.compile(r"(?<![A-Za-z])LORD['’]S(?![A-Za-z])")
FIRST, LAST = 357, 536
# Located by hand where the OCR garbles the row: 24:1 is a verse 1, its first
# row read with the two-line drop capital inside it (w22_scan: a TALL row).
OVERRIDE = {'24:1': (381, 25, 26)}


def letters(s):
    return re.sub(r'[^a-z ]', '', s.lower().replace('-', ' '))


def eye_pages():
    """{verse: scan page} from Wave 22's eye record, which read every verse."""
    out = {}
    for ln in open(os.path.join(HERE, 'w22_eye.txt'), encoding='utf-8'):
        m = re.match(r'^(\d+:\d+)\tp(\d+)\t', ln)
        if m and m.group(1) not in out:
            out[m.group(1)] = int(m.group(2))
    return out


def locate(text, m, pages, near):
    """-> (page, line index, line, score) of the printed row best matching the
    words around the possessive, on the verse's page (from the eye record) or
    the next. A window of up to three words either side."""
    before = text[:m.start()].split()[-3:]
    after = text[m.end():].split()[:3]
    want = letters(' '.join(before + ['lord'] + after))
    best = None
    for n in (near, near + 1):
        lines = pages[str(n)]
        for i, ln in enumerate(lines):
            # a row may break the window: score the row joined with its neighbours
            for j0, j1 in ((i, i + 1), (i - 1, i + 1), (i, i + 2)):
                if j0 < 0 or j1 > len(lines):
                    continue
                got = letters(' '.join(l[0] for l in lines[j0:j1]))
                sm = difflib.SequenceMatcher(None, want, got, autojunk=False)
                blk = sm.find_longest_match(0, len(want), 0, len(got))
                sc = blk.size / len(want)
                if best is None or sc > best[3]:
                    best = (n, i, ln, sc, (j0, j1))
    return best


def crop(png, left, top, width, height, out, scale=1):
    subprocess.run(['sips', '-c', str(height), str(width), '--cropOffset', str(top), str(left),
                    png, '--out', out], check=True, capture_output=True)
    if scale != 1:
        subprocess.run(['sips', '-z', str(height * scale), str(width * scale), out, '--out', out],
                       check=True, capture_output=True)
    got = subprocess.run(['sips', '-g', 'pixelHeight', '-g', 'pixelWidth', out],
                         check=True, capture_output=True, text=True).stdout
    h = int(re.search(r'pixelHeight: (\d+)', got).group(1))
    w = int(re.search(r'pixelWidth: (\d+)', got).group(1))
    if (h, w) != (height * scale, width * scale):      # the sips centre-crop trap (Wave 21)
        raise SystemExit('crop %s came out %dx%d, wanted %dx%d' % (out, w, h, width * scale,
                                                                 height * scale))
    return out


def main():
    out = R.OUT + '/w24'
    for a in sys.argv[1:]:
        if a.startswith('--out='):
            out = a[6:]
    os.makedirs(out, exist_ok=True)
    pages = json.load(open(os.path.join(HERE, 'w22_scan_ocr.json'), encoding='utf-8'))
    cells = w17_cells.cells('1892')
    near = eye_pages()
    rec = []
    for ref in TARGETS:
        ps, v = map(int, ref.split(':'))
        text = cells[ps][v]
        hits = list(POSS.finditer(text))
        if len(hits) != 1:
            raise SystemExit('%s: %d possessives in the cell' % (ref, len(hits)))
        if ref in OVERRIDE:
            n, j0, j1 = OVERRIDE[ref]
            sc = 0.0
        else:
            n, i, ln, sc, (j0, j1) = locate(text, hits[0], pages, near[ref])
        png = R.page_png(n, 4400)
        lines = pages[str(n)]
        rows = lines[max(0, j0 - 1):min(len(lines), j1 + 1)]
        top = min(l[2] for l in rows) - 12
        bot = max(l[2] + l[4] for l in rows) + 12
        left = min(l[1] for l in rows) - 60
        right = max(l[1] + l[3] for l in rows) + 60
        base = os.path.join(out, 'pos_%d_%d' % (ps, v))
        crop(png, left, top, right - left, bot - top, base + '.png')
        zr = lines[j0:j1]
        ztop = min(l[2] for l in zr) - 8
        zbot = max(l[2] + l[4] for l in zr) + 8
        crop(png, left, ztop, right - left, zbot - ztop, base + '_z.png', 2)
        rec.append({'verse': ref, 'page': n, 'rows': [j0, j1], 'score': round(sc, 3),
                    'crop': [left, top, right - left, bot - top],
                    'located_by': ' / '.join(l[0] for l in lines[j0:j1])})
        print('%-7s p%d rows %d-%d score %.2f' % (ref, n, j0, j1 - 1, sc))
    json.dump(rec, open(os.path.join(out, 'w24_locate.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
