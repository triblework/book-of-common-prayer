"""Render pages of the 1662 Annexed-Book witness to PNG (Wave 18).

The witness is the 1892 Oxford type-reproduction of the manuscript annexed to
the Act of Uniformity 1662, scanned by Google Books and served by Wikimedia
Commons (PD-US). Its own OCR text layer is unusable -- it drops the spaces
between words and loses whole italic phrases, including the names in the Prayer
for the Royal Family -- so pages are re-read with the Wave-17 pipeline:
pypdf splits one page out, Quick Look rasterizes it, Vision OCR reads it.

Same shape as w17_render.py, parameterized so the PDF can be chosen.
"""
import glob, os, subprocess, sys
import pypdf

SRC = glob.glob('/Users/wtrible/Developer/bcp/scrape-cache/'
                '*The_Book_of_Common_Prayer.pdf*.pdf')[0]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages-1662')
_reader = None


def reader():
    global _reader
    if _reader is None:
        _reader = pypdf.PdfReader(SRC)
    return _reader


def page_png(n, size=2400):
    """n is 1-based (PDF page, not book page); -> path of the rendered PNG."""
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
    size = 2400
    args = sys.argv[1:]
    if args and args[0].startswith('--size='):
        size = int(args.pop(0).split('=')[1])
    for a in args:
        print(page_png(int(a), size))
