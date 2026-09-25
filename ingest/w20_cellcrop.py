"""w20_cellcrop.py -- crop one Kalendar cell for a second look by eye (Wave 20).
    python3 ingest/w20_cellcrop.py PAGE DAY COL [TAG] [SCALE]  -> crop path"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w18_render as R
COLS = ['golden', 'day', 'letter', 'roman', 'note', 'm1', 'm2', 'e1', 'e2']


def cell(page, day, col, tag=None, scale=3):
    rec = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'w20_kal_reads.json')))[str(page)]
    tag = tag or ('A' if 'A' in rec else 'B')
    r = rec[tag]; xs = r['rules']; y = r['rows'][day - 1]['y']; half = int(r['pitch'] * 0.6)
    i = COLS.index(col)
    return R.crop(os.path.join(R.OUT, '%s%04d_desk.png' % (tag, page)), y - half, xs[i] - 4,
                  2 * half, xs[i + 1] - xs[i] + 8, scale=scale)


if __name__ == '__main__':
    a = sys.argv[1:]
    print(cell(int(a[0]), int(a[1]), a[2], a[3] if len(a) > 3 else None,
               int(a[4]) if len(a) > 4 else 3))
