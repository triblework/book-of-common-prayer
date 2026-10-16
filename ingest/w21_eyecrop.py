"""w21_eyecrop.py -- the crops the EYE reads were taken from (Workstream B).
Read-only; writes PNGs to <render>/reads/. Three tools, one file:

  groups   stack the two scans' second-read crops (w21_reads.json) for a list of
           candidate keys; for keys whose aligned crop missed the lines (a
           garbled drop-capital opening), find the line by its text instead and
           record the crop in w21_reads.json as manual_crop (MANUAL below, the
           relocations used in Phase 1b) -- w21_evidence reads it from there;
  wide     a full page-half-width crop found by text: [[pdf, book page,
           needle, n lines, lines before, tag], ...];
  verse    a whole verse cropped full-width by its alignment location:
           [[pdf, psalm, verse, extra lines before, after], ...].

    python3 ingest/w21_eyecrop.py groups "k1|k2;k3|k4" [MANUAL-json]
    python3 ingest/w21_eyecrop.py wide '<json list>' <name>
    python3 ingest/w21_eyecrop.py verse '<json list>' <name>

Run after w21_reads.py (which rewrites w21_reads.json; re-run `groups` with
the default MANUAL afterwards). These crops only SHOW the page; the reading
is what w21_eye.txt records.
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WB = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w21_render as R
import w21_psalter as P
import w21_reads as RD
from w21_ocrstats import OFF
READS = os.path.join(R.OUT_ROOT, 'reads')
STRIP = os.path.join(HERE, 'bin', 'w20_strip')
OCR = os.path.join(HERE, 'bin', 'w17_ocr')

MANUAL = {
    "12:1:me,lord": {"1952": [355, "HELP me LORD for there is not one godly man left", 2, 1]},
    "116:1:mediant": {"1952": [486, "MY delight is in the LORD because he hath heard", 3, 1]},
    "116:1:delight": {"1952": [486, "MY delight is in the LORD because he hath heard", 3, 1]},
    "119:33:mediant": {"1929": [492, "TEACH me O LORD the way of thy statutes and I", 3, 1],
                       "1952": [492, "TEACH me O LORD the way of thy statutes and I", 3, 1]},
    "119:33:teach": {"1929": [492, "TEACH me O LORD the way of thy statutes and I", 3, 1],
                     "1952": [492, "TEACH me O LORD the way of thy statutes and I", 3, 1]},
    "141:1:call": {"1952": [517, "LORD I call upon thee haste thee unto me and", 3, 1]},
    "44:21:+or": {"1952": [396, "search it out for he knoweth the very secrets of the heart", 2, 1]},
    "123:2:mediant": {"1929": [503, "Behold even as the eyes of servants look unto the hand of their masters", 3, 1],
                      "1952": [503, "Behold even as the eyes of servants look unto the hand of their masters", 3, 1]},
    "29:4:LORDd": {"1929": [374, "It is the LORD that ruleth the sea the voice of the", 3, 0]},
}


def scan_of(which, bp):
    off = OFF[which]
    return ((bp + off) // 2, 'L') if bp % 2 == 0 else ((bp + off - 1) // 2, 'R')


def _place(p):
    dst = os.path.join(READS, os.path.basename(p))
    os.replace(p, dst)
    return dst


def find_crop(which, bp, needle, n=2, before=0, tag='m', full=False):
    scan, side = scan_of(which, bp)
    rec = json.load(open(os.path.join(HERE, 'w21_%s_ocr.json' % which)))[str(scan)]
    L = rec[side]
    want = set(re.findall(r'[a-z]+', needle.lower()))
    best = max(range(len(L)), key=lambda k: len(want & set(re.findall(r'[a-z]+', L[k][0].lower()))))
    sel = L[max(0, best - before): best + n]
    top = max(1, min(l[2] for l in sel) - 20)
    bot = max(l[2] + l[4] for l in sel) + 20
    if full:
        left, right = (1, rec['gutter']) if side == 'L' else (rec['gutter'], rec['w'] - 1)
    else:
        left, right = max(1, min(l[1] for l in sel) - 30), max(l[1] + l[3] for l in sel) + 30
    p, _, _ = R.crop_at(R.page_png(which, scan, 4400), top, left, bot - top, right - left,
                        tag='_' + tag)
    return _place(p), scan, side


def groups(spec, manual):
    path = os.path.join(P.ALIGN_DIR, 'w21_reads.json')
    d = json.load(open(path))
    by = {o['key']: o for o in d}
    for keys in [g.split('|') for g in spec.split(';')]:
        crops = []
        for k in keys:
            o = by[k]
            for w in ('1929', '1952'):
                if k in manual and w in manual[k]:
                    bp, needle, n, before = manual[k][w]
                    c, scan, side = find_crop(w, bp, needle, n, before,
                                              tag=re.sub(r'\W+', '-', k) + w)
                    o['reads'][w].update(manual_crop=c, manual_scan=scan, manual_side=side,
                                         manual_book=bp)
                    crops.append(c)
                elif w in o['reads']:
                    crops.append(o['reads'][w]['crop'])
        out = os.path.join(READS, 'eye_group_%s.png' % re.sub(r'\W+', '-', '_'.join(keys))[:80])
        subprocess.run([STRIP, out] + crops, check=True)
        print(out)
    json.dump(d, open(path, 'w'), indent=1)


def wide(items, name):
    crops = []
    for which, bp, needle, n, before, tag in items:
        c, scan, side = find_crop(which, bp, needle, n, before, tag='w' + tag, full=True)
        o = subprocess.run([OCR, c], capture_output=True, text=True).stdout
        print(tag, which, 'scan', scan, side, 'p%d' % bp, '|',
              o.split('\t', 1)[-1].strip().replace('\\n', ' | ')[:160])
        crops.append(c)
    out = os.path.join(READS, 'wide_%s.png' % name)
    subprocess.run([STRIP, out] + crops, check=True)
    print(out)


def verse(items, name):
    S, crops = {}, []
    for which, ps, v, eb, ea in items:
        A = S.setdefault(which, P.build(which))
        k = [i for i, (a, b, _t) in enumerate(A['verses']) if (a, b) == (ps, v)][0]
        for (scan, side), lines in sorted(RD.verse_lines(A, k).items()):
            rec = json.load(open(os.path.join(HERE, 'w21_%s_ocr.json' % which)))[str(scan)]
            L = rec[side]
            sel = L[max(0, lines[0] - eb): lines[-1] + 1 + ea]
            top = max(1, min(l[2] for l in sel) - 20)
            bot = max(l[2] + l[4] for l in sel) + 20
            left, right = (1, rec['gutter']) if side == 'L' else (rec['gutter'], rec['w'] - 1)
            p, _, _ = R.crop_at(R.page_png(which, scan, 4400), top, left, bot - top,
                                right - left, tag='_v%d-%d' % (ps, v))
            c = _place(p)
            o = subprocess.run([OCR, c], capture_output=True, text=True).stdout
            print('%d:%d' % (ps, v), which, 'scan', scan, side, 'p%d' % P.book_page(which, scan, side),
                  '|', o.split('\t', 1)[-1].strip().replace('\\n', ' | ')[:220])
            crops.append(c)
    out = os.path.join(READS, 'verse_%s.png' % name)
    subprocess.run([STRIP, out] + crops, check=True)
    print(out)


if __name__ == '__main__':
    os.makedirs(READS, exist_ok=True)
    cmd = sys.argv[1]
    if cmd == 'groups':
        groups(sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else MANUAL)
    elif cmd == 'wide':
        wide(json.loads(sys.argv[2]), sys.argv[3])
    elif cmd == 'verse':
        verse(json.loads(sys.argv[2]), sys.argv[3])
    else:
        raise SystemExit(__doc__)
