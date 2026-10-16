"""w21_mediant.py -- does the scan print a mediant where the 1928 cell does?
(Workstream B; w18_mediant's method, read-only.)

The 1928 cells print the mediant as ' : ' (w13_render turns the justus
source's '*' into the corpus's ' : '); the book prints an ASTERISK -- a large
star in the 1929 printing, a small raised one in the 1952 facsimile, which
Vision often reads as " ' or a bullet. All of these are one mark class here.

For every verse (alignment from w21_psalter): take the cell word the mediant
follows (its pivot), find its witness partner, and ask whether a mark follows
it. Outcomes:

    agree    the witness word partnered with the pivot carries the mark
    moved    the pivot's partner carries no mark but another word of the
             verse's witness span does -- a candidate for a different
             pointing, read by eye
    unread   no partner for the pivot, or no mark anywhere in the verse's
             span: OCR damage, NOT evidence of absence
    absent   the cell prints no mediant in this verse; reported with what the
             witness shows (a mark, and on which word)

Unplaced verses (w21_psalter) are counted apart.

    python3 ingest/w21_mediant.py            # both scans
    python3 ingest/w21_mediant.py --final    # after w21_reads --mediants and the eye
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w21_psalter as P


def classify(A, r):
    ct, wt, m = A['ctoks'], A['wtoks'], A['map']
    idx = range(r['c_lo'], r['c_hi'])
    piv = [i for i in idx if ct[i]['med']]
    span = range(r['w_lo'], r['w_hi']) if r['w_lo'] is not None else range(0)
    marked = [j for j in span if wt[j].get('mark')]
    if not piv:
        return 'absent', None, [(j, wt[j]['t']) for j in marked]
    i = piv[0]
    if m[i] is None:
        return 'unread', i, []
    if wt[m[i]].get('mark'):
        return 'agree', i, []
    # the mark may sit on the next token when Vision split "word" and "*"
    if marked:
        return 'moved', i, [(j, wt[j]['t']) for j in marked]
    return 'unread', i, []


def run(which, A=None):
    A = A or P.build(which)
    out, tally = [], {'agree': 0, 'moved': 0, 'unread': 0, 'absent': 0, 'unplaced': 0}
    for r in A['rows']:
        kind, i, extra = classify(A, r)
        if not r['placed'] and kind != 'absent':
            tally['unplaced'] += 1
            out.append(dict(psalm=r['psalm'], verse=r['verse'], kind='unplaced'))
            continue
        tally[kind] += 1
        if kind != 'agree':
            out.append(dict(psalm=r['psalm'], verse=r['verse'], kind=kind,
                            pivot=A['ctoks'][i]['t'] if i is not None else None,
                            pages=r['pages'],
                            marks=[t for _j, t in extra]))
    return tally, out, A


def main():
    res = {}
    for which in ('1929', '1952'):
        tally, out, _A = run(which)
        res[which] = {(o['psalm'], o['verse']): o for o in out}
        print('%s: verses 2508: agree %d, moved %d, unread %d, absent %d, unplaced %d'
              % (which, tally['agree'], tally['moved'], tally['unread'], tally['absent'],
                 tally['unplaced']))
        for o in out:
            if o['kind'] in ('absent', 'moved'):
                print('   %-6s %3d:%-3d pivot=%-14s pages=%s marks=%s' % (
                    o['kind'], o['psalm'], o['verse'], o['pivot'],
                    [p[2] for p in o['pages']], o['marks'][:3]))
    both = set(res['1929']) & set(res['1952'])
    print('verses NOT agreeing on either scan: %d %s' % (
        len(both), sorted(both)[:40]))
    json.dump({w: [dict(v, key='%d:%d' % k) for k, v in sorted(res[w].items())]
               for w in res}, open(os.path.join(P.ALIGN_DIR, 'w21_mediant.json'), 'w'),
              indent=0)
    return res




def final():
    """Every verse's mediant on each scan, after the second reads and the eye:
    page OCR agree -> crop read (w21_reads --mediants: mark after the pivot)
    -> eye (w21_eye.txt 'mark after' / 'NO asterisk')."""
    rer = json.load(open(os.path.join(P.ALIGN_DIR, 'w21_mediant_rereads.json')))
    crop_ok = {(o['scan'], o['psalm'], o['verse']) for o in rer if o['crop_mark']}
    eye_yes, eye_no = set(), set()
    for line in open(os.path.join(HERE, 'w21_eye.txt'), encoding='utf-8'):
        if line.startswith('#') or ' | ' not in line:
            continue
        key, scan, _bp, what = [x.strip() for x in line.split(' | ')[:4]]
        rest = line.split(' | ')[4] if line.count(' | ') >= 4 else ''
        ps, v, kind = key.split(':', 2)
        if kind != 'mediant':
            continue
        if what.startswith('mark after'):
            eye_yes.add((scan, int(ps), int(v)))
        elif 'NO asterisk' in rest or what.startswith('no asterisk'):
            eye_no.add((scan, int(ps), int(v)))
    for which in ('1929', '1952'):
        tally, rows, _A = run(which)
        bad = {(o['psalm'], o['verse']): o['kind'] for o in rows}
        n = {'page OCR': 0, 'crop read': 0, 'eye: printed': 0, 'eye: NOT printed': 0,
             'cell unpointed, book points (eye)': 0, 'unresolved': []}
        for (ps, v), kind in sorted(bad.items()):
            t = (which, ps, v)
            if kind == 'absent':
                n['cell unpointed, book points (eye)'] += t in eye_yes
                if t not in eye_yes:
                    n['unresolved'].append('%d:%d' % (ps, v))
            elif t in eye_no:
                n['eye: NOT printed'] += 1
            elif t in crop_ok:
                n['crop read'] += 1
            elif t in eye_yes:
                n['eye: printed'] += 1
            else:
                n['unresolved'].append('%d:%d' % (ps, v))
        n['page OCR'] = tally['agree']
        print('%s: %s' % (which, n))
        print('   not printed by eye: %s' % sorted('%d:%d' % (p, v) for s, p, v in eye_no if s == which))


if __name__ == '__main__':
    if '--final' in sys.argv:
        final()
    else:
        main()
