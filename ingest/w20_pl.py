"""w20_pl.py -- the 1662 Proper Lessons and Proper Psalms (Wave 20).

Input  ingest/w20_pl_eye.txt  the eye read, as printed
Output editions/1662/tables/proper-lessons.md, proper-psalms.md (with --write)
       ingest/w20_pl_check.json

Machine check. The two-part table on PDF pp. 36-38 has no uniform row pitch
(occasions run to one, two or four printed lines), so it is not cut into
cells; each printed COLUMN of each page-half is OCR'd as a strip, on both
renderings (A local, B Wikimedia's), and every token of the eye read must be
found in that column's machine text, within a WINDOW of rows around its own
place (Wave 15: a cover test needs a window). Sensitivity is PROVED, not
assumed: readings this table prints nowhere are injected, one per column,
and every one must be reported missing.

    python3 ingest/w20_pl.py [--write]
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w18_render as R
from w20_cite import to_arabic
from w20_norm import LOOK

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BIN = os.path.join(HERE, 'bin')
LABEL = ['Morning 1', 'Morning 2', 'Evening 1', 'Evening 2']
# column rules per page-half, measured by bin/w20_grid on the deskewed renders
RULES = {'A': {36: ([526, 856, 1174, 1490], [1540, 1857, 2173, 2495]),
               37: ([560, 881, 1196, 1514], [1566, 1882, 2197, 2520]),
               38: ([546, 867, 1183, 1499], [1550, 1866, 2183, 2505])},
         'B': {36: ([526, 856, 1172, 1489], [1540, 1856, 2173, 2495]),
               37: ([559, 881, 1197, 1513], [1567, 1883, 2197, 2515]),
               38: ([548, 865, 1181, 1496], [1548, 1864, 2181, 2504])}}
BODY = {36: (1150, 3630), 37: (780, 3620), 38: (780, 2160)}
WINDOW = 0.15     # a token must be found within 15% of its column's token order


def parse(path):
    secs, cur, psalms, title, at = [], None, None, None, None
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if line.startswith('@ '):
            _, pg, hf = line.split()
            at = (int(pg), 'LR'.index(hf))
            continue
        if line.startswith('title: '):
            if psalms is not None:
                psalms['title'] = line[7:]
            else:
                title = line[7:]
        elif line.startswith('## PSALMS'):
            psalms = {'rows': []}
        elif line.startswith('## '):
            m = re.match(r'## (.*) (\d+)$', line)
            name = m.group(1)
            cont = name.endswith('(continued)')
            if cont:
                name = name[:-len(' (continued)')]
            cur = {'name': name, 'page': int(m.group(2)), 'rows': [], 'cont': cont}
            secs.append(cur)
        elif line and not line.startswith('#'):
            parts = [p.strip() for p in line.split('|')]
            if psalms is not None:
                psalms['rows'].append({'occ': parts[0], 'm': parts[1], 'e': parts[2]})
            else:
                assert len(parts) == 5, line
                cur['rows'].append({'occ': parts[0], 'cells': parts[1:], 'at': at})
    return title, secs, psalms


def toks(s):
    s = (s or '').translate(LOOK).lower()
    return re.findall(r'[a-z]+|\d+', s)


def column_reads(tag, page):
    """{(half, col): [token, ...] top to bottom} for occasion/mattens/evensong."""
    png = os.path.join(R.OUT, '%s%04d_desk.png' % (tag, page))
    top, bot = BODY[page]
    out = {}
    for h, xs in enumerate(RULES[tag][page]):
        for c in range(3):
            crop = R.crop(png, top, xs[c] + 6, bot - top, xs[c + 1] - xs[c] - 12, scale=2)
            d = json.loads(subprocess.run([os.path.join(BIN, 'w17_ocrbox'), crop],
                                          capture_output=True, text=True).stdout)
            lines = sorted(d['lines'], key=lambda l: l['y'])
            out[(h, c)] = [t for l in lines for t in toks(l['t'])]
    return out


def machine_check(secs, inject=False, reads=None):
    """Every eye token must appear in its printed column, on A or B, at about
    the same place in the column's top-to-bottom token order (|position
    difference| <= WINDOW of the column). Returns (found, missing, injected)."""
    reads = reads or {p: {t: column_reads(t, p) for t in 'AB'} for p in (36, 37, 38)}
    eye = {}
    for s in secs:
        for r in s['rows']:
            p, h = r['at']
            cells = [r['occ'],
                     ' '.join(x for x in (r['cells'][0], r['cells'][1]) if x),
                     ' '.join(x for x in (r['cells'][2], r['cells'][3]) if x)]
            for c, text in enumerate(cells):
                eye.setdefault((p, h, c), []).extend((r['occ'], t) for t in toks(text))
    injected = []
    if inject:      # one reading per column that this table prints nowhere
        for (key, fake) in zip(sorted(eye)[:3], ('zorobabel', 'lxxvii', 'xcix')):
            lst = eye[key]; lst.insert(len(lst) // 2, ('INJECTED', fake)); injected.append(fake)
    found, miss = 0, []
    for (p, h, c), lst in eye.items():
        for i, (occ, t) in enumerate(lst):
            if len(t) == 1 and t in 'abc':
                continue
            q = i / len(lst)
            ok = False
            for tag in 'AB':
                m = reads[p][tag][(h, c)]
                if any(tok == t and abs(j / max(len(m), 1) - q) <= WINDOW for j, tok in enumerate(m)):
                    ok = True
            if ok:
                found += 1
            else:
                miss.append('p%d%s col%d %s: %r' % (p, 'LR'[h], c, occ, t))
    return found, miss, injected, reads


def render_lessons(title, secs):
    L = ['# Tables of Proper Lessons', '', title]
    for s in secs:
        if not s['cont']:
            L += ['', '## ' + s['name'], '']
        for r in s['rows']:
            cells = [r['occ']]
            for lab, v in zip(LABEL, r['cells']):
                if v:
                    cells.append('%s: %s' % (lab, to_arabic(v)))
            L.append(' | '.join(cells))
    return '\n'.join(L) + '\n'


def render_psalms(ps):
    L = ['# Proper Psalms on Certain Days', '', ps['title'], '']
    for r in ps['rows']:
        m = ', '.join(to_arabic(x) for x in r['m'].split(' / '))
        e = ', '.join(to_arabic(x) for x in r['e'].split(' / '))
        L.append('%s | Morning: %s | Evening: %s' % (r['occ'], m, e))
    return '\n'.join(L) + '\n'


def main():
    title, secs, ps = parse(os.path.join(HERE, 'w20_pl_eye.txt'))
    print('rows per section:', [(s['name'][:20], s['page'], len(s['rows'])) for s in secs])
    found, miss, _, reads = machine_check(secs)
    print('tokens found by a machine read within the window:', found, ' missing from both:', len(miss))
    for m in miss:
        print('   ', m)
    f2, miss2, inj, _ = machine_check(secs, inject=True, reads=reads)
    caught = [t for t in inj if any(m.endswith(repr(t)) for m in miss2)]
    print('sensitivity: injected', inj, 'caught', caught)
    assert caught == inj, 'the cover test is not sensitive'
    json.dump({'found': found, 'missing': miss, 'injected': inj, 'caught': caught},
              open(os.path.join(HERE, 'w20_pl_check.json'), 'w'), indent=1)
    if '--write' in sys.argv:
        for name, text in (('proper-lessons', render_lessons(title, secs)),
                           ('proper-psalms', render_psalms(ps))):
            p = os.path.join(ROOT, 'editions', '1662', 'tables', name + '.md')
            open(p, 'w', encoding='utf-8').write(text)
            print('wrote', p)


if __name__ == '__main__':
    main()
