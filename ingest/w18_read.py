"""w18_read.py — read one printed line of the 1662 Annexed-Book witness twice.

Wave 17's rule carried forward: a reading counts only when two independent
machine reads agree, and anything else is read by eye off the crop. The page
OCR in w18_scan_ocr.json is the first read; this module supplies the second,
by cropping the line out of a 4400px render and OCR'ing that crop on its own.

    python3 ingest/w18_read.py 346 "Kiss the son lest he be angry"
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w18_render as R

HERE = os.path.dirname(os.path.abspath(__file__))
OCR = os.path.join(HERE, 'bin', 'w17_ocr')
BOX = os.path.join(HERE, 'bin', 'w17_ocrbox')


def words(s):
    return set(re.findall(r"[a-z]+", s.lower()))


def boxes(page, size=4400):
    png = R.page_png(page, size)
    out = subprocess.run([BOX, png], capture_output=True, text=True).stdout
    return png, json.loads(out.strip().split('\n')[0])


def ocr(path):
    out = subprocess.run([OCR, path], capture_output=True, text=True).stdout
    return out.split('\t', 1)[1].strip().replace('\\n', ' ') if '\t' in out else ''


def read_line(page, needle, size=4400, pad=(30, 26), scale=2, span=1,
              before=0):
    """Crop the line that best matches `needle` -- plus `span`-1 lines after it
    and `before` lines above it, because a verse's mediant often sits on the
    line above the words that matched -- and OCR the crop on its own.
    -> {page, first, second, crop}."""
    png, d = boxes(page, size)
    want = words(needle)
    scored = sorted(d['lines'], key=lambda l: -len(want & words(l['t'])))
    best = scored[0]
    after = sorted((l for l in d['lines'] if l['y'] > best['y']),
                   key=lambda l: l['y'])
    above = sorted((l for l in d['lines'] if l['y'] < best['y']),
                   key=lambda l: -l['y'])
    grp = above[:before][::-1] + [best] + after[:span - 1]
    top = min(l['y'] for l in grp) - pad[1]
    bot = max(l['y'] + l['h'] for l in grp) + pad[1]
    left = min(l['x'] for l in grp) - pad[0]
    right = max(l['x'] + l['w'] for l in grp) + pad[0]
    top, left = max(top, 0), max(left, 0)
    crop = R.crop(png, top, left, bot - top, right - left, scale=scale)
    return {'page': page, 'first': ' '.join(l['t'] for l in grp),
            'second': ocr(crop), 'crop': crop,
            'overlap': len(want & words(best['t']))}


if __name__ == '__main__':
    r = read_line(int(sys.argv[1]), sys.argv[2],
                  span=int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    print('page   ', r['page'], 'overlap', r['overlap'])
    print('first  ', r['first'])
    print('second ', r['second'])
    print('crop   ', r['crop'])
