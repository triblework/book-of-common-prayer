"""w20_kal.py -- the 1662 Kalendar: check the eye read, then build the cell (Wave 20).

Input  ingest/w20_kal_eye.txt   the eye read, as printed (roman, MS spelling)
       ingest/w20_kal_reads.json the two machine reads (w20_kal_read.py)
Output editions/1662/tables/calendar.md  (with --write)
       ingest/w20_kal_check.json         the audit record

Checks (a structural check only FINDS a suspect cell; the scan decides it):
  rows    each month has its printed number of rows (Feb prints a 29th)
  letter  the Sunday letters run A..G without a break across the year
          (the 29th of February prints none)
  blank   a row with all four lesson cells blank carries a note (a holy day)
  course  the Old Testament runs on through M1, E1, M1, E1...; the second
          lessons run on through M2 and through E2 separately; a chapter that
          goes backwards, repeats, or jumps by more than 3 is listed
  machine each kept cell is compared with the two machine reads: 'both' (A
          and B agree with the eye read), 'one', 'none'; and 'contra' where A
          and B agree with EACH OTHER against the eye read -- every contra
          cell was looked at again.

    python3 ingest/w20_kal.py [--write]
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w20_cite import to_arabic, chapters
from w20_norm import key

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKIP = int(os.environ.get('W20_SKIP', '1'))   # a chapter may run on by this much unlisted
ROWS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
COLS = ['letter', 'note', 'm1', 'm2', 'e1', 'e2']
LABEL = {'m1': 'Morning 1', 'm2': 'Morning 2', 'e1': 'Evening 1', 'e2': 'Evening 2'}


def parse(path):
    months, cur = [], None
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if line.startswith('## '):
            name, page = line[3:].split()
            cur = {'month': name, 'page': int(page), 'rows': [], 'notes': []}
            months.append(cur)
        elif line.startswith('note: '):
            cur['notes'].append(line[6:])
        elif line and not line.startswith('#') and cur is not None:
            parts = [p.strip() for p in line.split('|')]
            assert len(parts) == 7, line
            row = {'day': int(parts[0]), 'doubt': {}}
            for c, v in zip(COLS, parts[1:]):
                if '??' in v:
                    v, why = [x.strip() for x in v.split('??', 1)]
                    row['doubt'][c] = why
                row[c] = v
            cur['rows'].append(row)
    return months


def checks(months, reads):
    out = {'rows': [], 'letter': [], 'blank': [], 'course': [], 'machine': {}}
    for k, m in enumerate(months):
        if len(m['rows']) != ROWS[k] or [r['day'] for r in m['rows']] != list(range(1, ROWS[k] + 1)):
            out['rows'].append(m['month'])
    # letters
    seq, i = 'ABCDEFG', 0
    for m in months:
        for r in m['rows']:
            L = r['letter'].rstrip('.')
            if m['month'] == 'February' and r['day'] == 29:
                if L:
                    out['letter'].append('February 29 prints a letter')
                continue
            if L != seq[i % 7]:
                out['letter'].append('%s %d: %s, expected %s' % (m['month'], r['day'], L, seq[i % 7]))
            i += 1
    # blanks
    for m in months:
        for r in m['rows']:
            if not any(r[c] for c in LABEL) and not r['note']:
                out['blank'].append('%s %d' % (m['month'], r['day']))
    # courses
    def run(stream, name):
        book, last = None, None
        for where, cell in stream:
            if not cell:
                continue
            b, nums = chapters(cell)
            if b:
                if b != book:
                    book, last = b, None
            for n in nums:
                if last is not None and (n <= last or n > last + SKIP):
                    out['course'].append('%s %s: %s after %s (%s)' % (name, where, n, last, book))
                last = n
    ot, m2, e2 = [], [], []
    for m in months:
        for r in m['rows']:
            w = '%s %d' % (m['month'][:3], r['day'])
            ot += [(w + ' M1', r['m1']), (w + ' E1', r['e1'])]
            m2.append((w, r['m2'])); e2.append((w, r['e2']))
    run(ot, 'OT'); run(m2, 'M2'); run(e2, 'E2')
    # machine agreement
    tally = {c: {'both': 0, 'one': 0, 'none': 0, 'empty': 0} for c in COLS}
    contra = []
    for m in months:
        rec = reads[str(m['page'])]
        for j, r in enumerate(m['rows']):
            a = rec['A']['rows'][j]['cells'] if 'A' in rec else None
            b = rec['B']['rows'][j]['cells']
            for c in COLS:
                e = key(r[c])
                ka = key(a[c]) if a else None
                kb = key(b[c])
                if not e:
                    tally[c]['empty'] += 1
                n = (ka == e) + (kb == e)
                if e:
                    tally[c]['both' if n == 2 else 'one' if n == 1 else 'none'] += 1
                if a and ka and ka == kb and ka != e:
                    contra.append('%s %d %s: eye %r, A=B %r' % (m['month'], r['day'], c, r[c], a[c]))
    out['machine'] = {'tally': tally, 'contra': contra}
    return out


def render(months):
    L = ['# The Kalendar', '']
    for m in months:
        L += ['## ' + m['month'], '']
        for r in m['rows']:
            cells = ['%s %d' % (m['month'], r['day']),
                     'Sunday Letter: ' + (r['letter'].rstrip('.') or '—')]
            for c in ('m1', 'm2', 'e1', 'e2'):
                cells.append('%s: %s' % (LABEL[c], to_arabic(r[c]) if r[c] else '—'))
            cells.append('Kalendar Note: ' + (r['note'] or '—'))
            L.append(' | '.join(cells))
            for c, why in r['doubt'].items():
                shown = to_arabic(r[c]) if c in LABEL else r[c]
                L.append("<!-- VERIFY: '%s'; %s %d, %s: %s (Annexed Book, PDF p. %d) -->"
                         % (shown, m['month'], r['day'],
                            LABEL.get(c, 'Kalendar Note'), why, m['page']))
        for n in m['notes']:
            L.append('Footnote | ' + n)
        L.append('')
    return '\n'.join(L).rstrip('\n') + '\n'


def main():
    months = parse(os.path.join(HERE, 'w20_kal_eye.txt'))
    reads = json.load(open(os.path.join(HERE, 'w20_kal_reads.json')))
    res = checks(months, reads)
    json.dump(res, open(os.path.join(HERE, 'w20_kal_check.json'), 'w'), indent=1,
              ensure_ascii=False)
    for k in ('rows', 'letter', 'blank', 'course'):
        print(k, len(res[k]))
        for x in res[k]:
            print('   ', x)
    print('machine agreement (non-empty eye cells):')
    for c, t in res['machine']['tally'].items():
        print('   %-6s %s' % (c, t))
    print('contra (A and B agree against the eye read):', len(res['machine']['contra']))
    for x in res['machine']['contra']:
        print('   ', x)
    if '--write' in sys.argv:
        p = os.path.join(ROOT, 'editions', '1662', 'tables', 'calendar.md')
        open(p, 'w', encoding='utf-8').write(render(months))
        print('wrote', p)


if __name__ == '__main__':
    main()
