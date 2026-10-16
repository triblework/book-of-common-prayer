"""w22_book.py -- page OCR of the WHOLE 1892 Standard Book scan (596 pages),
for one question only: does the book print a word elsewhere that the Psalter
breaks across a line (Psalm 1:3 "water-" / "side")?

Workstream C. Read at 2400px (locating resolution; Wave 17) with bin/w22_ocr,
text only. The record goes to the render dir (<render>/w22_book_ocr.json); it
is a search index, not a witness record, and is not committed. Pages that read
to 0 lines are reported and rendered a second way before being called blank.

    python3 ingest/w22_book.py                # OCR every page not yet read
    python3 ingest/w22_book.py --grep REGEX   # search the record
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_render as R

BIN = os.path.join(HERE, 'bin', 'w22_ocr')
REC = os.path.join(R.OUT, 'w22_book_ocr.json')
N_PAGES = 596
SIZE = 2400


def read(pngs):
    out = subprocess.run([BIN] + pngs, capture_output=True, text=True, check=True).stdout
    return [json.loads(l) for l in out.strip().split('\n') if l.strip()]


def main():
    rec = json.load(open(REC)) if os.path.exists(REC) else {}
    todo = [n for n in range(1, N_PAGES + 1) if str(n) not in rec]
    for k in range(0, len(todo), 10):
        batch = todo[k:k + 10]
        pngs = [R.page_png(n, SIZE) for n in batch]
        for n, d in zip(batch, read(pngs)):
            rec[str(n)] = [l['t'] for l in d['lines']]
        json.dump(rec, open(REC, 'w'))
        print('%d/%d' % (k + len(batch), len(todo)), flush=True)
    zero = [n for n, v in rec.items() if not v]
    print('pages %d, lines %d, pages read to 0 lines: %s'
          % (len(rec), sum(len(v) for v in rec.values()), sorted(zero, key=int)))
    for n in sorted(zero, key=int):
        alt = R.page_png(int(n), 4400)
        print('  p%s at 4400px: %d lines' % (n, len(read([alt])[0]['lines'])))


def grep(rx):
    rec = json.load(open(REC))
    pat = re.compile(rx, re.I)
    for n in sorted(rec, key=int):
        lines = rec[n]
        for i, l in enumerate(lines):
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if pat.search(l) or (l.rstrip().endswith('-') and pat.search(l.rstrip()[:-1] + nxt)):
                print('p%s: %s%s' % (n, l, ('  /  ' + nxt) if l.rstrip().endswith('-') else ''))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--grep':
        grep(sys.argv[2])
    else:
        main()
