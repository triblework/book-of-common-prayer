"""w21_printdiff.py -- where do the two PRINTINGS differ? (Workstream B,
read-only; writes <render>/align/w21_printdiff.json and crops.)

The 1929 printing and the 1952 facsimile were set by different compositors,
so a word one of them prints differently from the other (and from the cell)
is either that compositor's own reading/error or an OCR misreading. For every
cell word that ONE scan's alignment pairs with a different witness word (or
with nothing) while the OTHER scan pairs it exactly, the line is cropped out
of the first scan and OCR'd on its own (the second read). If the crop read
gives the cell's word, the page OCR was wrong and the item closes; if it
does not, the item goes to the eye (w21_eye.txt).

Dropped words are caught the same way: a cell word with no partner at all.
Mediant differences between the printings are w21_mediant / w21_reads
--mediants; this file is for words.

    python3 ingest/w21_printdiff.py
    python3 ingest/w21_printdiff.py --unplaced   # verses an alignment could not place
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w21_psalter as P
import w21_reads as RD


def form_set(text):
    t = re.sub(r'(\w)- \| (\w)', r'\1\2', text)
    return {P.form(w) for w in re.split(r'[\s|]+', t) if P.form(w)}


def main():
    S = {w: P.build(w) for w in ('1929', '1952')}
    ct = S['1929']['ctoks']
    items = []
    for w, o in (('1929', '1952'), ('1952', '1929')):
        A, B = S[w], S[o]
        placed = {k for k, r in enumerate(A['rows']) if r['placed']}
        for i, t in enumerate(ct):
            if t['vi'] not in placed:
                continue
            ja, jb = A['map'][i], B['map'][i]
            ok_a = ja is not None and A['wtoks'][ja]['sk'] == t['sk']
            ok_b = jb is not None and B['wtoks'][jb]['sk'] == t['sk']
            if ok_a or not ok_b:
                continue
            loc = A['wtoks'][ja] if ja is not None else RD.locate(A, i)
            if loc is None:
                continue
            items.append(dict(scan=w, ci=i, cell=t['t'], form=t['f'],
                              page_word=A['wtoks'][ja]['t'] if ja is not None else None,
                              psalm=S['1929']['verses'][t['vi']][0],
                              verse=S['1929']['verses'][t['vi']][1],
                              at=[loc['scan'], loc['side'], loc['line'], loc['book']]))
    # second read, one crop per (scan, page side, line)
    cache = {}
    for it in items:
        scan, side, line, book = it['at']
        key = (it['scan'], scan, side, line)
        if key not in cache:
            first, path = RD.crop_lines(it['scan'], scan, side, max(0, line - 1), 3,
                                        '_pd%d-%d_%s' % (scan, line, it['scan']))
            cache[key] = (first, RD.ocr(path), path)
        it['first'], it['second'], it['crop'] = cache[key]
        it['crop_has_cell_word'] = it['form'] in form_set(it['second'])
    json.dump(items, open(os.path.join(P.ALIGN_DIR, 'w21_printdiff.json'), 'w'), indent=1)
    for w in ('1929', '1952'):
        mine = [x for x in items if x['scan'] == w]
        left = [x for x in mine if not x['crop_has_cell_word']]
        print('%s: cell words this scan does not match while the other does: %d; '
              'closed by the crop read %d; to the eye %d' % (
                  w, len(mine), len(mine) - len(left), len(left)))
        for x in left:
            print('   %3d:%-3d cell %-14s page %-14s crop: %s' % (
                x['psalm'], x['verse'], x['cell'], x['page_word'], x['second'][:90]))




# ---------------------------------------------------------------------------
# Verses one scan's alignment could not PLACE (mostly a drop-capital opening
# Vision garbled): the word sweep above skips them for that scan. Each is
# cropped whole out of that scan (all its lines, full page-half width) and
# OCR'd alone; cell words the crop read does not show go to the eye.
def unplaced():
    import difflib
    S = {w: P.build(w) for w in ('1929', '1952')}
    ct = S['1929']['ctoks']
    out = []
    for w in S:
        A = S[w]
        for k, r in enumerate(A['rows']):
            if r['placed']:
                continue
            ps, v = r['psalm'], r['verse']
            reads = []
            for (scan, side), lines in sorted(RD.verse_lines(A, k).items()):
                rec = json.load(open(os.path.join(HERE, 'w21_%s_ocr.json' % w)))[str(scan)]
                L = rec[side]
                lo, hi = max(0, lines[0] - 1), min(len(L), lines[-1] + 2)
                sel = L[lo:hi]
                top = max(1, min(l[2] for l in sel) - 20)
                bot = max(l[2] + l[4] for l in sel) + 20
                left, right = (1, rec['gutter']) if side == 'L' else (rec['gutter'], rec['w'] - 1)
                path, _t, _l = RD.R.crop_at(RD.R.page_png(w, scan, 4400), top, left,
                                            bot - top, right - left, tag='_up%d-%d_%s' % (ps, v, w))
                dst = os.path.join(RD.READS, os.path.basename(path))
                os.replace(path, dst)
                reads.append(dict(scan_page=scan, side=side, book=P.book_page(w, scan, side),
                                  second=RD.ocr(dst), crop=dst))
            got = form_set(' | '.join(x['second'] for x in reads))
            cellw = [ct[i]['f'] for i in range(r['c_lo'], r['c_hi'])]
            miss = [f for f in cellw if f not in got
                    and not any(f.replace('-', '') == g.replace('-', '') for g in got)]
            out.append(dict(scan=w, psalm=ps, verse=v, missing=miss, reads=reads))
    json.dump(out, open(os.path.join(P.ALIGN_DIR, 'w21_unplaced.json'), 'w'), indent=1)
    for w in ('1929', '1952'):
        mine = [o for o in out if o['scan'] == w]
        left = [o for o in mine if o['missing']]
        print('%s: unplaced verses %d; every cell word in the crop read %d; to the eye %d'
              % (w, len(mine), len(mine) - len(left), len(left)))
        for o in left:
            print('   %3d:%-3d missing %s' % (o['psalm'], o['verse'], o['missing'][:8]))
    return out


if __name__ == '__main__':
    if '--unplaced' in sys.argv:
        unplaced()
    else:
        main()
