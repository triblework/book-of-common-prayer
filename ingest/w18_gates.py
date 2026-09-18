#!/usr/bin/env python3
"""w18_gates.py — what must hold after the 1662 witness pass (Wave 18).

    python3 ingest/w18_gates.py

  1 evidence      every reading this wave claims has an entry in
                  w18_evidence.json, and the second read says what the wave
                  says it says. A 'blank' item must NOT read the names.
  2 corrections   both mediants are evidenced, and both are in the new cells.
  3 containment   the PUBLISHED 1662 psalter cells, with exactly these two
                  corrections applied, equal the new cells; and the published
                  structured cells, minus the website chrome, have exactly the
                  new cells' words. Nothing else moved.
  4 chrome        no cell in the corpus carries scraped site furniture.
  5 mediants      all 2,508 verses of the 1662 Psalter carry exactly one.
  6 flags         the 1662 VERIFY count fell from 15 to 7 -- three psalter
                  readings and five monarch flags closed -- and no monarch
                  flag is left asking for a scan.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w13_1662
import w17_cells
import w18_witness as W

TAG = 'v1662^{commit}'
PSALTER = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')
STRUCTURED = ('daily-office/morning-prayer.md', 'daily-office/evening-prayer.md',
              'the-litany/litany.md', 'ordinal/ordering-deacons.md',
              'holy-communion/holy-communion.md',
              'occasional-offices/public-baptism.md',
              'occasional-offices/prayers-at-sea.md')
CHROME = ('enable JavaScript', 'Turnon.js', 'Popular search items',
          'Copy to clipboard', 'Skip to main content', 'Accept all cookies')
findings = []


def check(name, ok, detail=''):
    print('%-4s %s%s' % ('ok' if ok else 'FAIL', name,
                         '' if ok else '  <- ' + str(detail)[:120]))
    if not ok:
        findings.append(name)


def strip(t):
    return re.sub(r'\n<!-- VERIFY.*?-->', '', t, flags=re.S)


def published(path):
    return subprocess.run(['git', 'show', '%s:%s' % (TAG, path)],
                          cwd=WT, capture_output=True, text=True).stdout


def main():
    ev = {r['id']: r for r in
          json.load(open(os.path.join(HERE, 'w18_evidence.json')))}

    # 1. evidence
    for it in W.ITEMS:
        r = ev.get(it['id'])
        if not r:
            check('evidence %s exists' % it['id'], False)
            continue
        seen = it['expect'] in r['second']
        if it['kind'] == 'blank':
            check('evidence %s: the page does not name them' % it['id'],
                  not seen and bool(r['eye']), r['second'][:80])
        else:
            check('evidence %s: second read shows %r' % (it['id'], it['expect']),
                  seen, r['second'][:80])
        check('evidence %s: page recorded' % it['id'], r['page'] == it['page'])

    # 2. the two corrections
    cells = w17_cells.cells('1662')
    for (n, v), (was, now) in sorted(W.POINTING.items()):
        check('correction %d:%d evidenced' % (n, v),
              ('ps-%d-%d' % (n, v)) in ev)
        check('correction %d:%d in the cell' % (n, v), now in cells[n][v],
              cells[n][v][:70])
        check('correction %d:%d: the old reading is gone' % (n, v),
              was not in cells[n][v])
    check('no word is introduced by this wave', not W.introduced(),
          W.introduced())

    # 3a. containment -- psalter (line by line, corrections applied)
    for f in PSALTER:
        old = published('texts/original/psalter/%s.md' % f)
        new = open(os.path.join(WT, 'editions/1662/psalter/%s.md' % f),
                   encoding='utf-8').read()
        if not old:
            check('containment %s: published cell available' % f, False)
            continue
        out, psalm, verse = [], None, None
        for line in strip(old).split('\n'):
            m = re.match(r'^## Psalm (\d+)', line)
            if m:
                psalm, verse = int(m.group(1)), 0
            mv = re.match(r'^(\d+) ', line)
            if psalm and (mv or (verse == 0 and line
                                 and not line.startswith(('#', '>')))):
                verse = int(mv.group(1)) if mv else 1
                head = mv.group(0) if mv else ''
                body = line[len(head):]
                fix = W.POINTING.get((psalm, verse))
                if fix and fix[0] in body:
                    body = body.replace(fix[0], fix[1])
                line = head + body
            out.append(line)
        check('containment %s: published + the two mediants == new cell' % f,
              '\n'.join(out) == strip(new))

    # 3b. containment -- structured cells (word for word). The published tree
    # is sentence-split, so lines do not correspond; words do.
    def words(t):
        return re.findall(r"[\w']+", t)
    for rel in STRUCTURED:
        old = published('texts/original/%s' % rel)
        new = open(os.path.join(WT, 'editions/1662/%s' % rel),
                   encoding='utf-8').read()
        if not old:
            check('containment %s: published cell available' % rel, False)
            continue
        kept = [l for l in strip(old).split('\n')
                if not any(c in l for c in CHROME)]
        check('containment %s: same words as published, less the chrome' % rel,
              words('\n'.join(kept)) == words(strip(new)))

    # 4. no site chrome anywhere in the corpus
    hits = []
    for root, _dirs, files in os.walk(os.path.join(WT, 'editions')):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            p = os.path.join(root, fn)
            t = open(p, encoding='utf-8').read()
            if any(c in t for c in CHROME):
                hits.append(os.path.relpath(p, WT))
    check('no scraped site chrome in any cell', not hits, hits[:3])

    # 5. the pointing is complete
    bad = [(n, v) for n in cells for v, t in cells[n].items()
           if t.count(' : ') != 1]
    check('every 1662 verse carries exactly one mediant (%d verses)'
          % sum(len(v) for v in cells.values()), not bad, bad[:6])

    # 6. flags
    n_flags = 0
    for root, _dirs, files in os.walk(os.path.join(WT, 'editions/1662')):
        for fn in files:
            if fn.endswith('.md'):
                n_flags += open(os.path.join(root, fn),
                                encoding='utf-8').read().count('<!-- VERIFY')
    # 15 before this wave: 3 in the Psalter, 5 on the monarch's name, 4 on the
    # Royal Family, and one each on the communion rubric, "Foreasmuch" and the
    # psalm-cento at sea. Eight are closed; the other seven are rewritten.
    check('1662 open flags 15 -> 7', n_flags == 7, n_flags)
    kings = sum(1 for rel in STRUCTURED
                if 'reign-dependent; reconcile' in
                open(os.path.join(WT, 'editions/1662/%s' % rel),
                     encoding='utf-8').read())
    check('the monarch flags are closed', kings == 0, kings)

    print('\nw18 gates: %d anomalies' % len(findings))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
