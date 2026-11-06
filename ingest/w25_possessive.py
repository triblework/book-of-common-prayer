"""w25_possessive.py -- crops of the possessive of small-capital LORD for the
eye, in the cells Wave 24 left unread. Wave 25; authoring-only.

R23 (maintainer, 2026-11-06): where an edition is read by eye against a page
scan its letter case follows the book, and the possessive of small-capital
LORD is set "LORD's" where the book prints a lower-case s. Wave 24 read the
eleven in the 1892 Psalter. This finds the rest that have a page scan:

  1892  occasional-offices/churching.md, the office's psalm (one), against
        1892Standard/1892standard.pdf, scan page 331 (book p. 303; found by
        OCR of scan pp. 328-351 -- the Burial ends on 330, the Sea forms begin
        on 333);
  1928  the Psalter (eleven: the same verses as 1892's), against the original
        printing 1928/BCP1929.pdf (R19), and the 1952 facsimile beside it as
        the second witness within limits.

The OCR line records (w21_1929_ocr.json, w21_1952_ocr.json, committed in
Wave 21; for 1892 p. 331 an OCR made here by w25_crop.ocr_lines) say only
WHERE the row is; they supply no reading. Each crop is the row with its
neighbours, and the row alone at 2x, labelled (file name) with the place only:

  <out>/pos_1892_churching.png, _z.png
  <out>/pos_1928_<ps>_<v>_<1929|1952>.png, _z.png
  <out>/tight_<ps>_<v>_<1929|1952>.png  the word with its neighbours at 3x
  <out>/pos_1979_<place>.png, _z.png    (evidence for the R11 question only)

1979 is Church Publishing's own file (R11): a born-digital typesetting, not a
scan. Its pages are rendered the same way (pypdf split, Quick Look at 4400px)
so the eye can see the glyph the font runs name (w25_fontruns.py); the page
for each place is the one w25_fontruns found (.cache/w25_fontruns_places.json).

The eye reads go into w25_eye.txt.

    W22_RENDER=<dir> W21_RENDER=<dir> W25_OCRBOX=<ocrbox binary> \\
        python3 ingest/w25_possessive.py [--out=DIR]
"""
import difflib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w25_crop as C

POSS = re.compile(r"(?<![A-Za-z])LORD['’]S(?![A-Za-z])")
CHURCHING = 'editions/1892/occasional-offices/churching.md'
CH_PAGE = 331
SCANS = {'1929': (192, 282), '1952': (203, 293)}       # the Psalter, scan pages
WB = os.path.dirname(HERE)


def letters(s):
    return re.sub(r'[^a-z ]', '', s.lower().replace('-', ' '))


def window(text, m, k=3):
    before = text[:m.start()].split()[-k:]
    after = text[m.end():].split()[:k]
    return letters(' '.join(before + ['lord'] + after))


def heads(pages):
    """Order the book pages (scan, side) and give each the psalms it can hold:
    from the highest psalm its predecessor's running head names to the highest
    its own names ("Psalm 11", "Psalms 12, 13", "Psalm 119:1"; the Psalter-day number is not a psalm)."""
    seq, prev, out = [], 0, {}
    for n in sorted(pages):
        for side in ('L', 'R'):
            top = pages[n][side][:1]
            head = re.sub(r'Day \d+', '', top[0][0]) if top else ''
            nums = [int(x) for x in re.findall(r'(?<![:\d])(\d{1,3})(?!\d)', head)]
            nums = [x for x in nums if 1 <= x <= 150] or [prev]
            hi = max(nums)
            out[(n, side)] = (min(prev, hi), hi)
            prev = hi
    return out


def best_row(want, pages, ps=None, span=None):
    """pages: {scan: {'L': [...], 'R': [...]}} -> (score, scan, side, i0, i1);
    with ps, only the book pages whose running heads allow that psalm."""
    best = None
    for n, rec in pages.items():
        for side in ('L', 'R'):
            if ps is not None and not (span[(n, side)][0] <= ps <= span[(n, side)][1]):
                continue
            lines = rec[side]
            for i in range(len(lines)):
                for j0, j1 in ((i, i + 1), (i - 1, i + 1), (i, i + 2)):
                    if j0 < 0 or j1 > len(lines):
                        continue
                    got = letters(' '.join(l[0] for l in lines[j0:j1]))
                    sm = difflib.SequenceMatcher(None, want, got, autojunk=False)
                    blk = sm.find_longest_match(0, len(want), 0, len(got))
                    sc = blk.size / len(want)
                    if best is None or sc > best[0] or (sc == best[0] and j1 - j0 < best[4] - best[3]):
                        best = (sc, n, side, j0, j1)
    return best


def do_1892(out, rec):
    import w22_render as R
    text = open(os.path.join(WB, CHURCHING), encoding='utf-8').read()
    hits = list(POSS.finditer(text))
    if len(hits) != 1:
        raise SystemExit('churching: %d possessives' % len(hits))
    png = R.page_png(CH_PAGE, 4400)
    lines, size = C.ocr_lines(png)
    want = window(text, hits[0])
    pages = {CH_PAGE: {'L': [list(l) for l in lines], 'R': []}}
    sc, n, side, j0, j1 = best_row(want, pages)
    box = C.row_crops(png, lines, j0, j1, os.path.join(out, 'pos_1892_churching'), size)
    rec.append({'place': '1892 churching', 'scan': n, 'rows': [j0, j1], 'score': round(sc, 3),
                'crop': box, 'located_by': ' / '.join(l[0] for l in lines[j0:j1])})
    print('1892 churching   p%d rows %d-%d score %.2f' % (n, j0, j1 - 1, sc))


def do_1928(out, rec):
    import w21_render as R
    cells = w17_cells.cells('1928')
    targets = []
    for ps in sorted(cells):
        for v in sorted(cells[ps]):
            for m in POSS.finditer(cells[ps][v]):
                targets.append((ps, v, cells[ps][v], m))
    for which in ('1929', '1952'):
        ocr = json.load(open(os.path.join(HERE, 'w21_%s_ocr.json' % which), encoding='utf-8'))
        lo, hi = SCANS[which]
        pages = {int(k): v for k, v in ocr.items() if lo <= int(k) <= hi}
        span = heads(pages)
        for ps, v, text, m in targets:
            sc, n, side, j0, j1 = best_row(window(text, m, 4), pages, ps, span)
            png = R.page_png(which, n, 4400)
            W, H = R._size_of(png)
            lines = [tuple(l) for l in pages[n][side]]
            box = C.row_crops(png, lines, j0, j1,
                              os.path.join(out, 'pos_1928_%d_%d_%s' % (ps, v, which)), (W, H))
            # the word itself at 3x, with the row's own lower-case s's beside it: the
            # 1929 scan's native spread is 1491px wide, so the row crop alone is soft
            for l in lines[j0:j1]:
                mm = re.search(r"L\S{2,3}\s?[Ss]", l[0])
                if mm:
                    cx = int(l[1] + l[3] * mm.start() / max(1, len(l[0])))
                    C.crop(png, max(1, cx - 420), l[2] - 10, 1000, l[4] + 20,
                           os.path.join(out, 'tight_%d_%d_%s.png' % (ps, v, which)), 3)
                    break
            bp = 2 * n - (40 if which == '1929' else 62) + (1 if side == 'R' else 0)
            rec.append({'place': '1928 %d:%d' % (ps, v), 'pdf': which, 'scan': n, 'side': side,
                        'book_page': bp, 'rows': [j0, j1], 'score': round(sc, 3), 'crop': box,
                        'located_by': ' / '.join(l[0] for l in lines[j0:j1])})
            print('1928 %-7s %s scan %d%s (p. %d) rows %d-%d score %.2f' % (
                '%d:%d' % (ps, v), which, n, side, bp, j0, j1 - 1, sc))
    return len(targets)


# Located by hand where the page OCR garbles the row: on p. 442 Vision reads
# the two rows "in the presence of all his people," / "In the courts of the
# LORD's house," as ONE box (row 25: "In in thouresef the fol his pouse,").
OVERRIDE_1979 = {'occasional-offices/churching.md:93': (25, 26)}


def do_1979(out, rec):
    import pypdf, subprocess, w19_witness_text as WTX
    places = json.load(open(os.path.join(HERE, '.cache', 'w25_fontruns_places.json')))
    reader = pypdf.PdfReader(WTX.SRC)
    d = os.path.join(out, 'pages1979')
    os.makedirs(d, exist_ok=True)
    for p in places:
        pages = sorted({k for k, _ in p['found']})
        if 'churching' in p['place']:
            pages = [k for k in pages if k < 700]      # the office's page, not the Psalter's
        elif p['place'].startswith('Ps 116'):
            pages = [k for k in pages if k > 700]
        for k in pages:
            png = os.path.join(d, 'p%04d_4400.png' % k)
            if not os.path.exists(png):
                tmp = os.path.join(d, 'tmp%04d.pdf' % k)
                w = pypdf.PdfWriter(); w.add_page(reader.pages[k - 1]); w.write(tmp)
                subprocess.run(['qlmanage', '-t', '-s', '4400', '-o', d, tmp],
                               check=True, capture_output=True)
                os.replace(tmp + '.png', png)
                os.remove(tmp)
            lines, size = C.ocr_lines(png)
            line = open(os.path.join(WB, p['file']), encoding='utf-8').read().split('\n')[p['line'] - 1]
            m = re.search(r"(?<![A-Za-z])LORD['\u2019][Ss](?![A-Za-z])", line)
            sc, n, side, j0, j1 = best_row(window(line, m, 4), {k: {'L': [list(l) for l in lines], 'R': []}})
            if p['place'] in OVERRIDE_1979:
                (j0, j1), sc = OVERRIDE_1979[p['place']], 0.0
            tag = re.sub(r'[^A-Za-z0-9]+', '_', p['place']).strip('_')
            box = C.row_crops(png, lines, j0, j1, os.path.join(out, 'pos_1979_%s' % tag), size)
            rec.append({'place': '1979 ' + p['place'], 'pdf_page': k, 'rows': [j0, j1],
                        'score': round(sc, 3), 'crop': box,
                        'located_by': ' / '.join(l[0] for l in lines[j0:j1])})
            print('1979 %-36s p%d rows %d-%d score %.2f' % (p['place'], k, j0, j1 - 1, sc))


def main():
    out = None
    for a in sys.argv[1:]:
        if a.startswith('--out='):
            out = a[6:]
    out = out or os.path.join(os.environ.get('W22_RENDER', '.'), 'w25')
    os.makedirs(out, exist_ok=True)
    rec = []
    do_1892(out, rec)
    k = do_1928(out, rec)
    print('1928 possessives in the cells:', k)
    if os.path.exists(os.path.join(HERE, '.cache', 'w25_fontruns_places.json')):
        do_1979(out, rec)
    json.dump(rec, open(os.path.join(out, 'w25_locate.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
