"""w21_render.py -- render pages of the 1928 American page scans (Workstream B).

Three justus scans of the 1928 book are in play, all "PDF graphics": one JPEG
2000 page image per PDF page, each image a two-page spread (left and right book
pages side by side), with an unproofread Acrobat Paper Capture OCR layer laid
over it (font /HiddenHorzOCR) that is NOT read here.

    1952   1928Standard/1952std.pdf  -- the 1952 facsimile of the Standard Book
    1929   1928/BCP1929.pdf          -- "the original 1928 printing"
    1936   1928/BCP1936.pdf          -- the 1936 printing

Two render paths, because a page one decoder rejects must be looked at another
way before it is called blank (Wave 20, Annexed Book p. 49):

    ql    pypdf splits the page out; macOS Quick Look rasterizes it at --size
          (the long edge), as w17/w18_render do;
    sips  the page's one image XObject is written out as-is (.jp2, or .jpg for
          a DCT page) and macOS `sips` converts it -- the NATIVE pixels -- then
          scales the long edge to --size (Wave 15's route, w15_src.scan_png).

Both are renderings of ONE file: never a second witness (R14).

    python3 ingest/w21_render.py --pdf 1952 --size 2400 1 2 3
    python3 ingest/w21_render.py --pdf 1929 --size 4400 --method sips 150
    W21_RENDER=<dir> overrides the output root (default: the session's
    render dir, below); PNGs go in <root>/<pdf>/.
"""
import glob, os, subprocess, sys
import pypdf

CACHE = '/Users/wtrible/Developer/bcp/scrape-cache/'
PDFS = {
    '1952': 'justus.anglican.org_resources_bcp_1928Standard_1952std.pdf.*.pdf',
    '1929': 'justus.anglican.org_resources_bcp_1928_BCP1929.pdf.*.pdf',
    '1936': 'justus.anglican.org_resources_bcp_1928_BCP1936.pdf.*.pdf',
}
OUT_ROOT = os.environ.get('W21_RENDER') or (
    '/private/tmp/claude-501/-Users-wtrible-Developer-bcp--claude-worktrees-'
    'bcp-wave-20-coordinator-5838d5/ff7c7f54-263d-4ce2-ac10-c0c8399ab47d/'
    'scratchpad/render/b')
_readers = {}


def src(which):
    if os.path.exists(which):
        return which
    hits = glob.glob(CACHE + PDFS[which])
    if len(hits) != 1:
        raise SystemExit('%s: expected one cached PDF, found %d' % (which, len(hits)))
    return hits[0]


def reader(which):
    if which not in _readers:
        _readers[which] = pypdf.PdfReader(src(which))
    return _readers[which]


def outdir(which, out=None):
    d = out or os.path.join(OUT_ROOT, os.path.basename(which) if os.path.exists(which) else which)
    os.makedirs(d, exist_ok=True)
    return d


def _size_of(png):
    r = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', png],
                       capture_output=True, text=True).stdout.split()
    return int(r[r.index('pixelWidth:') + 1]), int(r[r.index('pixelHeight:') + 1])


def page_png(which, n, size=2400, method='ql', out=None):
    """n is the 1-based PDF (scan) page; -> path of the rendered PNG."""
    d = outdir(which, out)
    png = os.path.join(d, 'p%04d_%d%s.png' % (n, size, '' if method == 'ql' else '_' + method))
    if os.path.exists(png):
        return png
    page = reader(which).pages[n - 1]
    if method == 'ql':
        tmp = os.path.join(d, 'tmp%04d.pdf' % n)
        w = pypdf.PdfWriter(); w.add_page(page); w.write(tmp)
        subprocess.run(['qlmanage', '-t', '-s', str(size), '-o', d, tmp],
                       check=True, capture_output=True)
        os.replace(tmp + '.png', png)
        os.remove(tmp)
        return png
    if method == 'sips':
        xo = page['/Resources'].get('/XObject') or {}
        imgs = [v.get_object() for v in xo.values()
                if v.get_object().get('/Subtype') == '/Image']
        if len(imgs) != 1:
            raise SystemExit('page %d: %d images; use --method ql' % (n, len(imgs)))
        f = str(imgs[0].get('/Filter'))
        ext = '.jp2' if 'JPX' in f else '.jpg' if 'DCT' in f else None
        if ext is None:
            raise SystemExit('page %d: filter %s not handled by sips route' % (n, f))
        raw = png[:-4] + ext
        with open(raw, 'wb') as fh:
            fh.write(imgs[0]._data)
        subprocess.run(['sips', '-s', 'format', 'png', raw, '--out', png],
                       check=True, capture_output=True)
        os.remove(raw)
        if size:
            subprocess.run(['sips', '-Z', str(size), png, '--out', png],
                           check=True, capture_output=True)
        return png
    raise SystemExit('unknown method %r' % method)


def crop_at(png, top, left, height, width, scale=1, tag=''):
    """Crop with sips; -> (path, top, left) of the crop actually made.

    GOTCHAS found here, both silent: `sips -c H W --cropOffset 0 0` ignores the
    offset and crops about the CENTRE; and some in-bounds requests (e.g. a
    crop running to the bottom edge from offset (1, 0)) come back UNCROPPED.
    So every crop is checked against the size asked for, and an origin or
    edge crop that sips mangles is retried one pixel in (the outermost pixel
    row/column of these scans is margin). A crop that still fails raises."""
    W, H = _size_of(png)
    tries = [(top, left, height, width)]
    if top == 0 or left == 0 or top + height >= H or left + width >= W:
        tries += [(top, left + 1, height, width - 1), (top + 1, left, height - 1, width),
                  (top + 1, left + 1, height - 1, width - 1)]
    for t, l, h, w in tries:
        if (t, l) == (0, 0):
            continue
        out = png[:-4] + '_c%d_%d_%d_%d%s.png' % (t, l, h, w, tag)
        subprocess.run(['sips', '-c', str(h), str(w), '--cropOffset',
                        str(t), str(l), png, '--out', out],
                       check=True, capture_output=True)
        if _size_of(out) == (w, h):
            if scale != 1:
                subprocess.run(['sips', '-z', str(int(h * scale)), str(int(w * scale)),
                                out, '--out', out], check=True, capture_output=True)
            return out, t, l
        os.remove(out)
    raise SystemExit('sips could not crop %s at %s' % (png, (top, left, height, width)))


def crop(png, top, left, height, width, scale=1, tag=''):
    return crop_at(png, top, left, height, width, scale, tag)[0]


def half(png, side, gutter=None):
    """Crop one book page out of a two-page spread: side 'L' or 'R'. The
    gutter defaults to the middle; w21_scan finds the real one from the OCR
    boxes and passes it."""
    w, h = _size_of(png)
    g = gutter or w // 2
    if side == 'L':
        return crop(png, 0, 0, h, g, tag='_L')
    return crop(png, 0, g, h, w - g, tag='_R')


if __name__ == '__main__':
    args = sys.argv[1:]
    which, size, method, out, side = '1952', 2400, 'ql', None, None
    while args and args[0].startswith('--'):
        k = args.pop(0)
        v = k.split('=', 1)[1] if '=' in k else args.pop(0)
        k = k.split('=')[0]
        if k == '--pdf': which = v
        elif k == '--size': size = int(v)
        elif k == '--method': method = v
        elif k == '--out': out = v
        elif k == '--half': side = v
        else: raise SystemExit('unknown option ' + k)
    for a in args:
        lo, _, hi = a.partition('-')
        for n in range(int(lo), int(hi or lo) + 1):
            p = page_png(which, n, size, method, out)
            print(half(p, side) if side else p)
