"""w22_render.py -- render pages of the 1892 Standard Book scan to PNG.

Workstream C (the full 1892 pointing collation). Wave 17's w17_render.py,
with the output directory a parameter: page renders are large and transient
and belong OUTSIDE the repo. Default out dir: $W22_RENDER, else the scratchpad
render dir named in the brief.

No PDF rasterizer is installed: each page is split out with pypdf and rendered
by macOS Quick Look (`qlmanage -t -s <px>`), which honours the requested max
dimension. `crop()` wraps `sips`.

    python3 ingest/w22_render.py [--size=4400] [--out=DIR] N [N ...]
"""
import glob, os, subprocess, sys
import pypdf

SRC = glob.glob('/Users/wtrible/Developer/bcp/scrape-cache/*1892standard.pdf*.pdf')[0]
DEFAULT_OUT = ('/private/tmp/claude-501/-Users-wtrible-Developer-bcp--claude-'
               'worktrees-bcp-wave-20-coordinator-5838d5/ff7c7f54-263d-4ce2-'
               'ac10-c0c8399ab47d/scratchpad/render/c')
OUT = os.environ.get('W22_RENDER', DEFAULT_OUT)
FIRST, LAST = 357, 536          # the Psalter, scan pages (1-based)
_reader = None


def reader():
    global _reader
    if _reader is None:
        _reader = pypdf.PdfReader(SRC)
    return _reader


def page_png(n, size=4400, out=None):
    """n is 1-based; -> path of the rendered PNG (cached)."""
    out = out or os.path.join(OUT, 'pages')
    os.makedirs(out, exist_ok=True)
    png = os.path.join(out, 'p%04d_%d.png' % (n, size))
    if os.path.exists(png):
        return png
    tmp = os.path.join(out, 'tmp%04d_%d_%d.pdf' % (n, size, os.getpid()))
    w = pypdf.PdfWriter(); w.add_page(reader().pages[n - 1]); w.write(tmp)
    subprocess.run(['qlmanage', '-t', '-s', str(size), '-o', out, tmp],
                   check=True, capture_output=True)
    os.replace(tmp + '.png', png)
    os.remove(tmp)
    return png


def crop(png, top, left, height, width, scale=1, out=None):
    """Crop with sips; `out` defaults to a name beside the page render."""
    out = out or png[:-4] + '_c%d_%d_%d_%d.png' % (top, left, height, width)
    subprocess.run(['sips', '-c', str(height), str(width), '--cropOffset',
                    str(top), str(left), png, '--out', out],
                   check=True, capture_output=True)
    if scale != 1:
        subprocess.run(['sips', '-z', str(int(height * scale)),
                        str(int(width * scale)), out, '--out', out],
                       check=True, capture_output=True)
    return out


if __name__ == '__main__':
    size, out, pages = 4400, None, []
    for a in sys.argv[1:]:
        if a.startswith('--size='):
            size = int(a.split('=', 1)[1])
        elif a.startswith('--out='):
            out = a.split('=', 1)[1]
        else:
            pages.append(int(a))
    for n in pages:
        print(page_png(n, size, out))
