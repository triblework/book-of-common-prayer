"""Render pages of the 1892 subscribers'-edition scan to PNG.

No PDF rasterizer is installed, so each page is split out with pypdf and
rendered by macOS Quick Look (`qlmanage -t`), which honours the requested
max dimension.
"""
import glob, os, subprocess, sys
import pypdf

SRC = glob.glob('/Users/wtrible/Developer/bcp/scrape-cache/*1892standard.pdf*.pdf')[0]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages')
_reader = None

def reader():
    global _reader
    if _reader is None:
        _reader = pypdf.PdfReader(SRC)
    return _reader

def page_png(n, size=2400):
    """n is 1-based; -> path of the rendered PNG."""
    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, 'p%04d_%d.png' % (n, size))
    if os.path.exists(png):
        return png
    tmp = os.path.join(OUT, 'tmp%04d.pdf' % n)
    w = pypdf.PdfWriter(); w.add_page(reader().pages[n - 1]); w.write(tmp)
    subprocess.run(['qlmanage', '-t', '-s', str(size), '-o', OUT, tmp],
                   check=True, capture_output=True)
    os.replace(tmp + '.png', png)
    os.remove(tmp)
    return png

def crop(png, top, left, height, width, scale=1):
    out = png[:-4] + '_c%d_%d_%d_%d.png' % (top, left, height, width)
    subprocess.run(['sips', '-c', str(height), str(width), '--cropOffset',
                    str(top), str(left), png, '--out', out],
                   check=True, capture_output=True)
    if scale != 1:
        subprocess.run(['sips', '-z', str(height * scale), str(width * scale),
                        out, '--out', out], check=True, capture_output=True)
    return out

if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(page_png(int(a)))
