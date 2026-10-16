"""w21_evidence.py -- build ingest/w21_evidence.json, the witness record of
Workstream B (w17_evidence's shape, one record per candidate, per scan).

    key -> {psalm, verse, class,
            scans: {"1929"|"1952": {page, side, book, first, second, auto, eye}}}

  page/side  the scan (PDF) page and half; book = the printed folio
  first      the page OCR of the line(s) (w21_<pdf>_ocr.json)
  second     the same lines cropped from the 4400px render and OCR'd alone
  auto       True when the second read itself shows what the eye read records
  eye        the reading taken by eye (ingest/w21_eye.txt)

Machine reads come from the render-dir tables written by w21_reads.py,
w21_reads.py --mediants and w21_printdiff.py (regenerate those first). A
book page in w21_eye.txt that disagrees with the machine record stops the
build.

    python3 ingest/w21_evidence.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w21_psalter as P
import w21_witness as W
from w21_ocrstats import OFF

EYE = os.path.join(HERE, 'w21_eye.txt')
OUT = os.path.join(HERE, 'w21_evidence.json')
MARK = '[*"\'•’“”·]'


def norm(frag):
    return re.sub(r'[^a-z~+-]', '', frag.lower())


def scan_of(which, bp):
    off = OFF[which]
    return ((bp + off) // 2, 'L') if bp % 2 == 0 else ((bp + off - 1) // 2, 'R')


def eye_rows():
    rows = []
    section = None
    for line in open(EYE, encoding='utf-8'):
        if line.startswith('# ---'):
            section = line.strip('# -\n').strip()
            continue
        if line.startswith('#') or not line.strip():
            continue
        parts = [x.strip() for x in line.rstrip('\n').split(' | ')]
        key, scan, book, what = parts[:4]
        note = parts[4] if len(parts) > 4 else ''
        rows.append(dict(key=key, scan=scan, book=int(book), eye=what, note=note,
                         section=section))
    return rows


def _ocr(path):
    import subprocess
    if not os.path.exists(path):
        return None
    out = subprocess.run([os.path.join(HERE, 'bin', 'w17_ocr'), path],
                         capture_output=True, text=True).stdout
    return out.split('\t', 1)[1].strip().replace('\\n', ' | ') if '\t' in out else ''


def machine():
    A = os.path.join(P.ALIGN_DIR, '%s')
    reads = json.load(open(A % 'w21_reads.json'))
    rer = json.load(open(A % 'w21_mediant_rereads.json'))
    pdf = json.load(open(A % 'w21_printdiff.json'))
    upl = json.load(open(A % 'w21_unplaced.json'))
    idx = {}
    for o in reads:
        ps, v, frag = o['key'].split(':', 2)
        for w, r in o['reads'].items():
            if r.get('manual_crop'):
                # the alignment put the first crop on the wrong lines (a garbled
                # drop-capital opening); the eye read used a crop found by text
                rec = dict(page=r['manual_scan'], side=r['manual_side'], book=r['manual_book'],
                           first=None, second=_ocr(r['manual_crop']))
            else:
                rec = dict(page=r['scan_page'], side=r['side'], book=r['book_page'],
                           first=r['first'], second=r['second'])
            idx.setdefault((int(ps), int(v), w), []).append((norm(frag), rec))
    for o in rer:
        for r in o['reads']:
            idx.setdefault((o['psalm'], o['verse'], o['scan']), []).append(
                ('mediant', dict(page=r['scan_page'], side=r['side'], book=r['book_page'],
                                 first=r['first'], second=r['second'])))
    for o in upl:
        for r in o['reads']:
            idx.setdefault((o['psalm'], o['verse'], o['scan']), []).append(
                ('verse', dict(page=r['scan_page'], side=r['side'], book=r['book'],
                               first=None, second=r['second'])))
    for o in pdf:
        sc, sd, ln, bk = o['at']
        idx.setdefault((o['psalm'], o['verse'], o['scan']), []).append(
            (norm(o['form']), dict(page=sc, side=sd, book=bk, first=o['first'],
                                   second=o['second'])))
    return idx


def klass(key, section):
    for c in W.CORRECTIONS:
        if c['key'] == key:
            return 'correction:' + c['kind']
    for d in W.DISAGREE:
        if d['key'] == key:
            return 'printing-difference:' + d['kind']
    if key in W.UNDECIDABLE:
        return 'undecidable-hyphen'
    if key == '109:21:~':
        return 'correction:pointing'      # the tilde is where the asterisk stands
    return {'mediants the page OCR missed, present by eye': 'mediant-confirmed',
            'page-OCR noise: the page prints the cell\'s word (no correction)': 'ocr-noise',
            '1929 broken or worn type: the word is the cell\'s, a letter is damaged':
                'worn-type',
            'cell compounds the 1929 page OCR did not show whole (cell form stands)':
                'hyphen-confirmed',
            'word sweep: the page prints the cell\'s word (drop capitals, small capitals,':
                'ocr-noise',
            'verses an alignment could not place (drop-capital openings): the whole':
                'unplaced-verse-read'}.get(section, section)


def words(s):
    return re.findall(r"[a-z]+(?:-[a-z]*)?", (s or '').lower())


def contiguous(frag, text, no_mark=False):
    """The fragment's words occur consecutively in the read (punctuation
    ignored); with no_mark, no mediant glyph stands between them."""
    fw, tw = words(frag), words(text)
    if not fw:
        return False
    for i in range(len(tw) - len(fw) + 1):
        if tw[i:i + len(fw)] == fw:
            if not no_mark:
                return True
            # find the span in the raw text and look for a mark inside it
            rx = r'\W+'.join(re.escape(x) for x in fw)
            m = re.search(rx, text.lower())
            if m and not re.search(MARK, text[m.start():m.end()]):
                return True
    return False


def auto(rec, note, eye):
    s = (rec.get('second') or '').replace(' | ', ' ')
    if not s:
        return None
    m = re.match(r'mark after (.+)', eye)
    if m:
        w = re.escape(m.group(1).split('|')[-1].strip().rstrip(',;:.'))
        return bool(re.search(w + r'[,;:.!?]?\s*' + MARK, s, re.I))
    if eye.startswith(('as the cell', 'no asterisk')):
        return None                 # judged against the cell / the whole verse, by eye
    frag = re.sub(r'\s*/\s*', ' ', eye)
    return contiguous(frag, s, no_mark='NO asterisk' in note)


def main():
    idx = machine()
    out, problems = {}, []
    for r in eye_rows():
        ps, v, frag = r['key'].split(':', 2)
        ps, v = int(ps), int(v)
        cands = idx.get((ps, v, r['scan']), [])
        want = norm(frag)
        hit = next((m for f, m in cands if f == want), None) or \
            next((m for f, m in cands if f == 'mediant' and want.startswith('mediant')), None) or \
            next((m for f, m in cands if m['book'] == r['book']), None)
        sc, sd = scan_of(r['scan'], r['book'])
        rec = dict(page=sc, side=sd, book=r['book'], eye=r['eye'] + (' -- ' + r['note'] if r['note'] else ''))
        if hit:
            if hit['book'] != r['book']:
                problems.append((r['key'], r['scan'], 'eye p%d vs machine p%d' % (r['book'], hit['book'])))
            rec.update(first=hit['first'], second=hit['second'])
            rec['auto'] = auto(hit, r['note'], r['eye'])
        else:
            # a crop made for the eye read (full-width verse / line crops in the
            # render dir), named by scan page and verse
            import glob
            pats = [os.path.join(P.w21_render.OUT_ROOT, 'reads',
                                 'p%04d_4400_*%s%d-%d*.png' % (sc, t, ps, v))
                    for t in ('_v', '_w', '_med-')]
            hits = sorted(h for pat in pats for h in glob.glob(pat))
            if hits:
                sec = ' | '.join(x for x in (_ocr(h) for h in hits) if x)
                rec.update(first=None, second=sec)
                rec['auto'] = auto(dict(second=sec), r['note'], r['eye'])
            else:
                rec.update(first=None, second=None, auto=None)
        e = out.setdefault(r['key'], dict(psalm=ps, verse=v, cls=klass(r['key'], r['section']),
                                          scans={}))
        e['scans'][r['scan']] = rec
    if problems:
        for p in problems:
            print('PAGE MISMATCH', p)
        raise SystemExit('w21_evidence: %d page mismatches' % len(problems))
    json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False, sort_keys=True)
    by = {}
    for e in out.values():
        by[e['cls']] = by.get(e['cls'], 0) + 1
    n_eye = sum(len(e['scans']) for e in out.values())
    n_auto = sum(1 for e in out.values() for s in e['scans'].values() if s['auto'])
    print('evidence: %d keys, %d scan readings by eye (%d also machine-confirmed by the '
          'crop read); by class %s' % (len(out), n_eye, n_auto, by))
    return out


if __name__ == '__main__':
    main()
