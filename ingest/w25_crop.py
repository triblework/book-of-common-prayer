"""w25_crop.py -- shared crop helpers for Wave 25's eye reads; authoring-only.

Wave 24's size-checked crop (w24_possessive.crop), with the OCR line record
made on the spot: the page render is OCR'd with the Vision line-box binary
(ingest/w17_ocrbox.swift, compiled to $W25_OCRBOX) only to say WHERE a row
is. It supplies no reading; every reading is the eye's.

    crop(png, left, top, width, height, out, scale=1)   size-checked (Wave 21)
    ocr_lines(png)     -> [(text, x, y, w, h)] in page pixels, top-left origin
    row_crops(png, lines, i0, i1, base)   the rows i0..i1-1 with a row of
                       context either side -> base.png, and those rows alone
                       at 2x -> base_z.png; -> the crop boxes
"""
import json, os, re, subprocess

OCRBOX = os.environ.get('W25_OCRBOX', 'ocrbox')


def crop(png, left, top, width, height, out, scale=1):
    left, top = max(0, left), max(0, top)
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


def ocr_lines(png):
    cache = png[:-4] + '_ocr.json'
    if not os.path.exists(cache):
        out = subprocess.run([OCRBOX, png], check=True, capture_output=True, text=True).stdout
        open(cache, 'w').write(out)
    o = json.loads(open(cache).read())
    return [(l['t'], l['x'], l['y'], l['w'], l['h']) for l in o['lines']], (o['w'], o['h'])


def row_crops(png, lines, i0, i1, base, size):
    W, H = size
    rows = lines[max(0, i0 - 1):min(len(lines), i1 + 1)]
    top = min(l[2] for l in rows) - 12
    bot = min(H, max(l[2] + l[4] for l in rows) + 12)
    left = max(0, min(l[1] for l in rows) - 60)
    right = min(W, max(l[1] + l[3] for l in rows) + 60)
    crop(png, left, top, right - left, bot - top, base + '.png')
    zr = lines[i0:i1]
    ztop = min(l[2] for l in zr) - 8
    zbot = min(H, max(l[2] + l[4] for l in zr) + 8)
    crop(png, left, ztop, right - left, zbot - ztop, base + '_z.png', 2)
    return [left, top, right - left, bot - top]
