"""w18_scan.py — OCR the 1662 Annexed-Book witness page by page (Wave 18).

Writes ingest/w18_scan_ocr.json: {"<pdf page>": [line, line, ...]}, the same
shape as Wave 17's w18-equivalent record for the 1892 scan. Vision OCR with
language correction OFF, so the MS's own spelling (vngodly, ioy, shew) survives.

    python3 ingest/w18_scan.py 1 577                     # the whole book
    python3 ingest/w18_scan.py 345 507 4400 w18_psalter_ocr.json

The whole book is read at 2400px, which is enough to find a passage. The
Psalter pages are read again at 4400px into their own record: at 2400 Vision
drops about one line in six on these dense pages, which is fatal for a
verse-by-verse alignment. Anything read CLOSELY is re-rendered and cropped
line by line (w18_read.py); the page record is never the last word.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w18_render as R

HERE = os.path.dirname(os.path.abspath(__file__))
OCR = os.path.join(HERE, 'bin', 'w17_ocr')
BATCH = 8


def main(lo, hi, size=2400, name='w18_scan_ocr.json'):
    REC = os.path.join(HERE, name)
    rec = json.load(open(REC)) if os.path.exists(REC) else {}
    todo = [n for n in range(lo, hi + 1) if str(n) not in rec]
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        pngs = [R.page_png(n, size) for n in chunk]
        out = subprocess.run([OCR] + pngs, capture_output=True, text=True).stdout
        for line in out.strip().split('\n'):
            if '\t' not in line:
                continue
            path, body = line.split('\t', 1)
            n = int(os.path.basename(path)[1:5])
            rec[str(n)] = [x for x in body.split('\\n') if x.strip()]
        json.dump(rec, open(REC, 'w'), indent=0)
        print('%d/%d  page %d' % (i + len(chunk), len(todo), chunk[-1]), flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(int(a[0]), int(a[1]),
         int(a[2]) if len(a) > 2 else 2400,
         a[3] if len(a) > 3 else 'w18_scan_ocr.json')
