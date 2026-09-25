"""w20_bands.py -- cut a Kalendar page into row bands for the eye read (Wave 20).

    python3 ingest/w20_bands.py PAGE [ROWS_PER_BAND]
Prints each band's crop path and, for each row in it, the two machine reads
(A | B) of the columns kept by R13, so the eye read can be checked against
them cell by cell."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w18_render as R

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = ['day', 'letter', 'note', 'm1', 'm2', 'e1', 'e2']

page = sys.argv[1]
per = int(sys.argv[2]) if len(sys.argv) > 2 else 8
rec = json.load(open(os.path.join(HERE, 'w20_kal_reads.json')))[page]
tag = 'A' if 'A' in rec else 'B'
r = rec[tag]
png = os.path.join(R.OUT, '%s%04d_desk.png' % (tag, int(page)))
xs, rows, half = r['rules'], r['rows'], int(r['pitch'] * 0.6)
for b in range(0, len(rows), per):
    band = rows[b:b + per]
    top = band[0]['y'] - half
    bot = band[-1]['y'] + half
    left = xs[1] - 4
    crop = R.crop(png, top, left, bot - top, xs[9] - left + 4)
    print('BAND', b + 1, '-', b + len(band), crop)
    for k, row in enumerate(band):
        i = b + k
        ra = rec['A']['rows'][i]['cells'] if 'A' in rec else {}
        rb = rec['B']['rows'][i]['cells']
        print('  %2d' % (i + 1), ' | '.join('%s/%s' % (ra.get(c, '-') or '·', rb[c] or '·')
                                          for c in KEEP))
