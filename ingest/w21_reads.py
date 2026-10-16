"""w21_reads.py -- the second machine read for every Phase-1b candidate, on
BOTH scans (Workstream B, read-only; crops and the table go to the render
dir, <render>/align/w21_reads.json and <render>/reads/).

First read: the page OCR record (w21_<pdf>_ocr.json) -- the line(s) the
alignment puts the candidate on. Second read: those lines cropped out of the
4400 px render by their pixel boxes (w21_render.crop_at, size-checked) and
OCR'd on their own (bin/w17_ocr). Two lines are cropped (the candidate's line
and the next), because a mediant or a broken word often spans them.

Candidates come from w21_lexical (both directions, and the compounds broken
at a line end), from w21_mediant (every verse that agrees on neither scan,
and every 'moved'), and five fixed items: the three flagged mediants, 29:4's
`LORDd`, 109:21's `~`. Nothing here decides a reading; the eye read
(ingest/w21_eye.txt) does wherever the two machine reads disagree or the
candidate survives.

    python3 ingest/w21_reads.py            # -> crops + table
    python3 ingest/w21_reads.py --strips   # also stack each candidate's two crops
    python3 ingest/w21_reads.py --mediants # re-read verses one scan left unconfirmed
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w21_psalter as P
import w21_render as R
import w21_lexical as LX
import w21_mediant as MD

OCR = os.path.join(HERE, 'bin', 'w17_ocr')
STRIP = os.path.join(HERE, 'bin', 'w20_strip')
READS = os.path.join(R.OUT_ROOT, 'reads')
FIXED = [(18, 28, 'mediant'), (109, 21, 'mediant'), (119, 1, 'mediant'),
         (29, 4, 'LORDd'), (109, 21, '~')]


def ocr(path):
    out = subprocess.run([OCR, path], capture_output=True, text=True).stdout
    return out.split('\t', 1)[1].strip().replace('\\n', ' | ') if '\t' in out else ''


def locate(A, ci):
    """Cell token index -> the witness token the alignment pairs with it, or
    the nearest paired neighbour."""
    m = A['map']
    # forward first, within the verse: a verse's first word shares a line with
    # its next few; only then look back
    for k in list(range(ci, ci + 6)) + list(range(ci - 1, ci - 12, -1)) + list(range(ci + 6, ci + 12)):
        if 0 <= k < len(m) and m[k] is not None \
                and A['wtoks'][m[k]]['sk'] == A['ctoks'][k]['sk']:
            return dict(A['wtoks'][m[k]], back=k < ci)
    return None


def crop_lines(which, scan, side, line, n=2, tag=''):
    rec = json.load(open(os.path.join(HERE, 'w21_%s_ocr.json' % which)))[str(scan)][side]
    sel = rec[line:line + n] or rec[-n:]
    png = R.page_png(which, scan, 4400)
    top = max(1, min(l[2] for l in sel) - 25)
    left = max(1, min(l[1] for l in sel) - 30)
    bot = max(l[2] + l[4] for l in sel) + 25
    right = max(l[1] + l[3] for l in sel) + 30
    path, _t, _l = R.crop_at(png, top, left, bot - top, right - left, tag=tag)
    dst = os.path.join(READS, os.path.basename(path))
    os.replace(path, dst)
    return ' | '.join(l[0] for l in sel), dst


def candidates(S):
    _S, cs, und, ss = LX.run()
    out = []
    ct = S['1929']['ctoks']
    for c in cs:
        out.append(dict(key='%d:%d:%s' % (c['psalm'], c['verse'], c['form']), psalm=c['psalm'],
                        verse=c['verse'], kind='cell-word', cell=c['word'], ci=c['ci'],
                        att=c['att'], contra=c['contra']))
    for c in und:
        out.append(dict(key='%d:%d:%s' % (c['psalm'], c['verse'], c['form']), psalm=c['psalm'],
                        verse=c['verse'], kind='hyphen-at-break', cell=c['word'], ci=c['ci'],
                        att=c['att'], clear_elsewhere=c['clear_elsewhere']))
    seen = set()
    for c in ss:
        k = '%d:%d:+%s' % (c['psalm'], c['verse'], c['form'])
        if k in seen:
            for o in out:
                if o['key'] == k:
                    o['at'][c['scan']] = c['at']
            continue
        seen.add(k)
        out.append(dict(key=k, psalm=c['psalm'], verse=c['verse'], kind='scan-word',
                        scanword=c['word'], at={c['scan']: c['at']}, both=c['both']))
    med = {}
    for w in ('1929', '1952'):
        _t, rows, _A = MD.run(w, S[w])
        for o in rows:
            med.setdefault((o['psalm'], o['verse']), {})[w] = o['kind']
    for (p, v), d in sorted(med.items()):
        if len(d) == 2 or 'moved' in d.values():
            if (p, v, 'mediant') in FIXED:
                continue
            out.append(dict(key='%d:%d:mediant' % (p, v), psalm=p, verse=v, kind='mediant',
                            outcome=d))
    for p, v, what in FIXED:
        out.append(dict(key='%d:%d:%s' % (p, v, what), psalm=p, verse=v,
                        kind='fixed-' + ('mediant' if what == 'mediant' else 'reading')))
    # the cell token each item is about
    starts = {}
    for i, t in enumerate(ct):
        starts.setdefault(t['vi'], []).append(i)
    vidx = {(ps, v): k for k, (ps, v, _t) in enumerate(S['1929']['verses'])}
    for o in out:
        idx = starts[vidx[(o['psalm'], o['verse'])]]
        if 'ci' not in o:
            if o['kind'] in ('mediant', 'fixed-mediant'):
                piv = [i for i in idx if ct[i]['med']]
                o['ci'] = piv[0] if piv else None
                if o['ci'] is None:     # the flagged verses: where the book points
                    hint = {(18, 28): 'adversity', (109, 21): 'poor', (119, 1): 'way'}
                    o['ci'] = next(i for i in idx if ct[i]['sk'].startswith(hint[(o['psalm'], o['verse'])]))
            elif o['kind'] == 'fixed-reading':
                key = o['key'].split(':', 2)[2]
                if key == '~':
                    o['ci'] = next(i for i in idx if ct[i]['t'].startswith('poor'))
                else:
                    o['ci'] = next(i for i in idx if key in ct[i]['t'])
            else:
                o['ci'] = idx[0]
    return out


def main(strips=False):
    os.makedirs(READS, exist_ok=True)
    S = {w: P.build(w) for w in ('1929', '1952')}
    cands = candidates(S)
    for o in cands:
        o['reads'] = {}
        for w in ('1929', '1952'):
            if o['kind'] == 'scan-word' and w in o['at']:
                scan, side, line, book = o['at'][w]
            else:
                t = locate(S[w], o['ci'])
                if t is None:
                    continue
                scan, side, line, book = t['scan'], t['side'], t['line'], t['book']
            n = 2
            if o['kind'] != 'scan-word' and t.get('back'):
                # found only by looking back: the candidate is on the lines after
                # the previous verse's word (a drop-capital opening Vision garbled)
                n = 4
            tag = '_%s_%s' % (re.sub(r'[^0-9A-Za-z]+', '-', o['key']), w)
            first, path = crop_lines(w, scan, side, line, n, tag)
            o['reads'][w] = dict(scan_page=scan, side=side, line=line, book_page=book,
                                 first=first, second=ocr(path), crop=path)
        if strips and len(o['reads']) == 2:
            out = os.path.join(READS, 'strip_%s.png' % re.sub(r'[^0-9A-Za-z]+', '-', o['key']))
            subprocess.run([STRIP, out, o['reads']['1929']['crop'], o['reads']['1952']['crop']],
                           check=True)
            o['strip'] = out
    json.dump(cands, open(os.path.join(P.ALIGN_DIR, 'w21_reads.json'), 'w'), indent=1)
    kinds = {}
    for o in cands:
        kinds[o['kind']] = kinds.get(o['kind'], 0) + 1
    print('candidates %d %s; crops %d' % (len(cands), kinds,
                                        sum(len(o['reads']) for o in cands)))




# ---------------------------------------------------------------------------
# Mediant re-reads: every verse whose mediant one scan's page OCR did not
# confirm (unread / unplaced / moved) while the other scan's did. The whole
# verse is cropped out of THAT scan (all its lines, by pixel box) and OCR'd on
# its own; a mark in the crop read is the second machine read. Verses whose
# crop still shows no mark go to the eye.
MARKS_RX = re.compile('[*"\'•’“”·]')


def verse_lines(A, k):
    """-> {(scan, side): [line, ...]} for verse k of alignment A, from its
    partnered witness tokens, else from the neighbouring verses' edges."""
    rows, m, wt = A['rows'], A['map'], A['wtoks']
    r = rows[k]
    js = [m[i] for i in range(r['c_lo'], r['c_hi']) if m[i] is not None]
    if not js:
        prev = next((m[i] for i in range(r['c_lo'] - 1, -1, -1) if m[i] is not None), 0)
        nxt = next((m[i] for i in range(r['c_hi'], len(m)) if m[i] is not None), len(wt) - 1)
        js = list(range(prev, nxt + 1))
    lo, hi = min(js), max(js)
    out = {}
    for j in range(lo, hi + 1):
        t = wt[j]
        for sc, sd, ln in ((t['scan'], t['side'], t['line']),
                           (t.get('scan2', t['scan']), t.get('side2', t['side']), t.get('line2', t['line']))):
            out.setdefault((sc, sd), set()).add(ln)
    return {k2: sorted(v) for k2, v in out.items()}


def mediant_rereads():
    os.makedirs(READS, exist_ok=True)
    S = {w: P.build(w) for w in ('1929', '1952')}
    med = {}
    for w in S:
        _t, rows, _A = MD.run(w, S[w])
        for o in rows:
            med.setdefault((o['psalm'], o['verse']), {})[w] = o['kind']
    vidx = {(ps, v): k for k, (ps, v, _t) in enumerate(S['1929']['verses'])}
    out = []
    for (p, v), d in sorted(med.items()):
        if len(d) != 1 or 'absent' in d.values():
            continue                    # both-scan items are in the main table
        w = next(iter(d))
        A = S[w]
        reads = []
        for (scan, side), lines in sorted(verse_lines(A, vidx[(p, v)]).items()):
            lo, hi = lines[0], lines[-1]
            first, path = crop_lines(w, scan, side, lo, hi - lo + 1,
                                     '_med-%d-%d_%s' % (p, v, w))
            reads.append(dict(scan_page=scan, side=side, lines=[lo, hi],
                              book_page=P.book_page(w, scan, side), first=first,
                              second=ocr(path), crop=path))
        # the mark must follow the cell's pivot word in the crop read (a crop
        # holds whole lines, so a neighbouring verse's mark may be in it too)
        r = A['rows'][vidx[(p, v)]]
        piv = [A['ctoks'][i] for i in range(r['c_lo'], r['c_hi']) if A['ctoks'][i]['med']]
        word = re.escape(piv[0]['t'].rstrip(',;:.!?')) if piv else None
        pat = re.compile(r'%s[,;:.!?]?\s*[*"\'\u2022\u2019\u201c\u201d\u00b7]' % word, re.I) if word else None
        marked = bool(pat and any(pat.search(x['second'].replace(' | ', ' ')) for x in reads))
        out.append(dict(key='%d:%d:mediant' % (p, v), psalm=p, verse=v, scan=w,
                        outcome=d[w], pivot=piv[0]['t'] if piv else None,
                        crop_mark=marked, reads=reads))
    json.dump(out, open(os.path.join(P.ALIGN_DIR, 'w21_mediant_rereads.json'), 'w'), indent=1)
    for w in ('1929', '1952'):
        mine = [o for o in out if o['scan'] == w]
        print('%s: verses re-read %d; a mark in the crop read %d; to the eye %d %s' % (
            w, len(mine), sum(o['crop_mark'] for o in mine),
            sum(not o['crop_mark'] for o in mine),
            [o['key'] for o in mine if not o['crop_mark']]))
    return out


if __name__ == '__main__':
    if '--mediants' in sys.argv:
        mediant_rereads()
    else:
        main('--strips' in sys.argv)
