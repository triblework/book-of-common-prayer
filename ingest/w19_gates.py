#!/usr/bin/env python3
"""w19_gates.py — what must hold after the 1979 witness pass (Wave 19).

    python3 ingest/w19_gates.py

  1 evidence     every correction is found in the book, with its page
                 (ingest/w19_evidence.json, rebuilt by w19_evidence.py).
  2 collation    the corrected Psalter cell differs from the book in exactly
                 the fifteen verses where the PDF's text layer is known to
                 drop a mark, and nowhere else.
  3 containment  the PUBLISHED cells, with exactly this wave's corrections
                 applied, equal the new cells. Nothing else moved.
  4 defects      none of the keying defects this wave names survives anywhere
                 in the 1979 text.
  5 flags        the 1979 inline VERIFY count fell from 143 to 127, and no
                 psalter flag is left.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w17_cells
import w19_cells
import w19_psalter
import w19_witness as W

TAG = 'v1979^{commit}'
PSALTER = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')
# The PDF's text layer drops the pointing asterisk in ten verses, prints a
# dash for it in one, and carries a stray "I" or quotation mark in four more.
# Those are extraction artifacts, not readings; see w19_witness.__doc__.
ARTIFACTS = {(24, 10), (33, 16), (34, 3), (40, 11), (40, 16), (65, 11),
             (69, 18), (71, 21), (83, 16), (83, 17), (105, 21), (105, 22),
             (107, 28), (119, 166), (144, 15)}
DEFECTS = ('fulfull', 'asbrant', 'wwe ', 'Am the ordering', 'Almighty god',
           'BCPSALTER', 'winge!d', 'Zee%b', 'Issac', 'confort',
           'to be the way, t Amen')
findings = []


def check(name, ok, detail=''):
    print('%-4s %s%s' % ('ok' if ok else 'FAIL', name,
                         '' if ok else '  <- ' + str(detail)[:140]))
    if not ok:
        findings.append(name)


def strip(t):
    return re.sub(r'\n?<!-- VERIFY.*?-->\n?', '\n', t, flags=re.S)


def published(path):
    return subprocess.run(['git', 'show', '%s:%s' % (TAG, path)],
                          cwd=WT, capture_output=True, text=True).stdout


def main():
    ev = json.load(open(os.path.join(HERE, 'w19_evidence.json')))
    by = {}
    for r in ev:
        by.setdefault((r['kind'], str(r['where'])), []).append(r)

    # 1. evidence
    for (n, v) in sorted(W.VERSES):
        check('evidence for Psalm %d:%d' % (n, v),
              ('psalm-verse', '%d:%d' % (n, v)) in by)
    for was in sorted(W.HEADINGS):
        check('evidence for the heading %r' % was, ('psalm-heading', was) in by)
    check('every evidence entry names a page', all(r['page'] for r in ev))

    # 2. the collation residue
    rows, _chain, _t, _v = None, None, None, None
    w_verses, _inc, _pg = w19_psalter.parse()
    cells = w17_cells.cells('1979')
    residue = set()
    for ps in cells:
        for v, text in cells[ps].items():
            book = w_verses.get(ps, {}).get(v)
            if book is None:
                residue.add((ps, v))
            elif w19_psalter.fold(text) != w19_psalter.fold(book, mediant=' * '):
                residue.add((ps, v))
    check('the Psalter now differs from the book only where its text layer '
          'drops a mark (%d verses)' % len(ARTIFACTS),
          residue == ARTIFACTS, sorted(residue ^ ARTIFACTS))

    # 3. containment
    for f in PSALTER:
        old = published('texts/original/psalter/%s.md' % f)
        new = open(os.path.join(WT, 'editions/1979/psalter/%s.md' % f),
                   encoding='utf-8').read()
        if not old:
            check('containment %s: published cell available' % f, False)
            continue
        out, psalm = [], None
        for line in strip(old).split('\n'):
            m = re.match(r'^## Psalm (\d+)', line)
            if m:
                psalm = int(m.group(1))
            mv = re.match(r'^(\d+) ', line)
            if psalm and mv:
                v = int(mv.group(1))
                fix = W.VERSES.get((psalm, v))
                if fix:
                    was, now = (fix[0].replace(' * ', ' : '),
                                fix[1].replace(' * ', ' : '))
                    line = line.replace(was, now)
            if line.startswith('> '):
                head = line[2:].strip()
                if head in W.HEADINGS:
                    line = '> ' + W.HEADINGS[head][0]
            out.append(line)
        check('containment %s: published + this wave == new cell' % f,
              re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()
              == strip(new).strip())

    def words(t):
        return re.findall(r"[\w']+", t)

    def flat(t):
        return ' '.join(t.split())
    # The published tree is sentence-split, so its line breaks differ from the
    # cell's; compare on one flattened line.
    for rel, subs in sorted(w19_cells.EDITS.items()):
        old = published('texts/original/' + rel.replace('editions/1979/', ''))
        new = open(os.path.join(WT, rel), encoding='utf-8').read()
        if not old:
            check('containment %s: published cell available' % rel, False)
            continue
        got = flat(strip(old))
        for a, b in subs:
            got = got.replace(flat(a), flat(b))
        check('containment %s: published + this wave == new cell (words)' % rel,
              words(got) == words(flat(strip(new))))

    # 4. the defects are gone
    left = []
    for root, _d, files in os.walk(os.path.join(WT, 'editions/1979')):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            p = os.path.join(root, fn)
            body = strip(open(p, encoding='utf-8').read())
            for d in DEFECTS:
                if d in body:
                    left.append((os.path.relpath(p, WT), d))
    check('no named keying defect survives in the 1979 text', not left, left[:4])

    # 5. flags
    n = 0
    for root, _d, files in os.walk(os.path.join(WT, 'editions/1979')):
        for fn in files:
            if fn.endswith('.md'):
                n += open(os.path.join(root, fn),
                          encoding='utf-8').read().count('<!-- VERIFY')
    check('1979 inline flags 143 -> 127', n == 127, n)
    ps_flags = sum(open(os.path.join(WT, 'editions/1979/psalter/%s.md' % f),
                        encoding='utf-8').read().count('<!-- VERIFY')
                   for f in PSALTER)
    check('no flag is left in the 1979 Psalter', ps_flags == 0, ps_flags)

    print('\nw19 gates: %d anomalies' % len(findings))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
