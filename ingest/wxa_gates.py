#!/usr/bin/env python3
"""wxa_gates.py -- what must hold for the 1979 witness pass (Workstream A).
DRAFT: runs now against unchanged cells (wxa_witness.ENABLED is empty).

    python3 ingest/wxa_gates.py

  1 evidence     every item in every group has an evidence entry naming its
                 book page and fragment (a pure markup normalization names
                 its rule instead); every refused item names its reason.
  2 residue      the Wave-19 Psalter collation residue is still exactly the
                 fifteen verses where the PDF's text layer drops a mark.
  3 containment  for every 1979 cell: the cell at the branch base
                 (git 710f635b..., editions/1979/, never a live tag) with
                 exactly the ENABLED groups applied == the cell now. Nothing
                 else may move. And every group applies with no stale item,
                 alone and all together.
  4 composite    tables/calendar.md and tables/eucharistic-lectionary.md are
                 the base text, and no item targets them (their witness
                 pages are a 2008 Calendar and the 2007 RCL).
  5 markup       once MARKUP is on, no e-text markup pattern survives (and in
                 the all-groups dry run, none survives now); no item's new
                 text brings markup or curly quotes in.
  6 flags        the inline VERIFY count equals 127 less the flags the
                 ENABLED groups close; which flags each group closes.
  7 scope        no item touches the Psalter, and every item's file exists.
"""
import collections
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wxa_witness as W

findings = []
COMPOSITE = ('tables/calendar.md', 'tables/eucharistic-lectionary.md')
MARKS = {
    '=x=': r'=\S[^=\n]{0,58}=|=\S=', '&N.': r'&N\.', '&mdash.': r'&mdash\.',
    '&V./&R.': r'&[VR]\.', '**X* :': r'^\*\*[A-Za-z ,()]+\* : ',
    '[[': r'\[\[', ']]': r'\]\]', '&3em.': r'&3em', 'END OF': r'END OF \w+\.TXT',
    '&LordsPrayer.': r'&LordsPrayer', '*X* label': r'^\*[A-Z][A-Za-z ]+\*  ',
    '<An Outline>': r'<An Outline|of the Faith>',
}
COMMENT = re.compile(r'<!--.*?-->', re.S)


def check(name, ok, detail=''):
    print('%-4s %s%s' % ('ok' if ok else 'FAIL', name,
                         '' if ok else '  <- ' + str(detail)[:160]))
    if not ok:
        findings.append(name)


def base(rel):
    r = subprocess.run(['git', 'show', '%s:editions/1979/%s' % (W.BASE, rel)],
                       cwd=WT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def cells():
    root = os.path.join(WT, 'editions/1979')
    return sorted(os.path.relpath(f, root) for f in
                  glob.glob(os.path.join(root, '**/*.md'), recursive=True))


def marks_left(t, prose_only_rel):
    if prose_only_rel.startswith(('psalter/', 'tables/')):
        return []
    t = COMMENT.sub('', t)
    return [k for k, p in MARKS.items() if re.search(p, t, re.M)]


def main():
    ev = json.load(open(os.path.join(HERE, 'wxa_evidence.json')))
    dropped = json.load(open(os.path.join(HERE, 'wxa_dropped.json')))
    allitems = [(g, it) for g, v in W.ITEMS.items() for it in v]

    # 1. evidence
    missing = [it['id'] for g, it in allitems if it['id'] not in ev]
    check('evidence entry for every item (%d items)' % len(allitems),
          not missing, missing[:3])
    nopage = [it['id'] for g, it in allitems
              if ev.get(it['id'], {}).get('page') is None and
              not (g == 'MARKUP' and it.get('pattern') not in ('&mdash.',)) and
              it['class'] != 'flag']
    check('every item but a pure markup rule or a flag names its page',
          not nopage, nopage[:3])
    check('every evidence entry has a book fragment or rule',
          all(v.get('book') for v in ev.values()))
    check('every refused item names its reason (%d refused)'
          % len(dropped['dropped']),
          all(d.get('reason') for d in dropped['dropped']))

    # 2. the Wave-19 residue
    try:
        import w17_cells
        import w19_psalter
        import w19_gates
        w_verses, _inc, _pg = w19_psalter.parse()
        cs = w17_cells.cells('1979')
        residue = set()
        for ps in cs:
            for v, text in cs[ps].items():
                book = w_verses.get(ps, {}).get(v)
                if book is None or w19_psalter.fold(text) != \
                        w19_psalter.fold(book, mediant=' * '):
                    residue.add((ps, v))
        check('Psalter residue is still exactly the %d text-layer artifacts'
              % len(w19_gates.ARTIFACTS), residue == w19_gates.ARTIFACTS,
              sorted(residue ^ w19_gates.ARTIFACTS))
    except Exception as e:                     # never pass silently
        check('Psalter residue computed', False, e)

    # 3. containment
    bad = []
    for rel in cells():
        b = base(rel)
        if b is None:
            bad.append((rel, 'not at base'))
            continue
        want, _ap, st = W.apply(rel, b, W.ENABLED, strict=False)
        now = open(os.path.join(WT, 'editions/1979', rel), encoding='utf-8').read()
        if st:
            bad.append((rel, 'stale %d' % len(st)))
        elif want != now:
            bad.append((rel, 'differs'))
    check('containment: base + ENABLED %s == every cell now (%d cells)'
          % (W.ENABLED or '[]', len(cells())), not bad, bad[:3])
    for g in W.GROUP_ORDER:
        st = []
        for rel in W.files([g]):
            _n, _a, s = W.apply(rel, base(rel), [g], strict=False)
            st += s
        check('group %-13s applies alone, no stale item' % g, not st, st[:2])
    st_all, results = [], {}
    for rel in W.files(W.GROUP_ORDER):
        b = base(rel)
        n, _a, s = W.apply(rel, b, W.GROUP_ORDER, strict=False)
        st_all += s
        results[rel] = (b, n)
    check('all groups together apply, no stale item', not st_all, st_all[:2])

    # 4. the composite witness
    tgt = [it['id'] for g, it in allitems if it['file'] in COMPOSITE]
    check('no item targets calendar.md or eucharistic-lectionary.md',
          not tgt, tgt[:3])
    for rel in COMPOSITE:
        now = open(os.path.join(WT, 'editions/1979', rel), encoding='utf-8').read()
        check('%s is the base text' % rel, now == base(rel))

    # 5. markup
    left = {}
    for rel in cells():
        t = results[rel][1] if rel in results else base(rel)
        m = marks_left(t, rel)
        if m:
            left[rel] = m
    check('all-groups dry run: no e-text markup pattern survives', not left,
          list(left.items())[:3])
    if 'MARKUP' in W.ENABLED:
        now_left = {rel: marks_left(open(os.path.join(WT, 'editions/1979', rel),
                                         encoding='utf-8').read(), rel)
                    for rel in cells()}
        check('MARKUP on: no pattern survives in the cells',
              not any(now_left.values()))
    def nmarks(t):
        return sum(len(re.findall(p, t, re.M)) for p in MARKS.values())
    intro = [it['id'] for g, it in allitems
             if nmarks(it['new']) > nmarks(it['old'])
             or re.search(r'[\u2018\u2019\u201c\u201d]', it['new'])]
    check('no item brings markup or curly quotes in', not intro, intro[:3])

    # 6. flags
    def nflags(t):
        return t.count('<!-- VERIFY')
    now = sum(nflags(open(os.path.join(WT, 'editions/1979', r),
                          encoding='utf-8').read()) for r in cells())
    closes = collections.Counter()
    for g in W.GROUP_ORDER:
        for rel in W.files([g]):
            b = base(rel)
            n, _a, _s = W.apply(rel, b, [g], strict=False)
            closes[g] += nflags(b) - nflags(n)
    expect = 127 - sum(closes[g] for g in W.ENABLED)
    check('inline flags now %d == 127 - flags closed by ENABLED groups (%d)'
          % (now, expect), now == expect)
    print('     flags each group would close: %s' %
          {g: c for g, c in closes.items() if c})

    # 7. scope
    ps = [it['id'] for g, it in allitems if it['file'].startswith('psalter/')]
    check('no item touches the Psalter', not ps, ps[:3])
    gone = [it['id'] for g, it in allitems
            if not os.path.exists(os.path.join(WT, 'editions/1979', it['file']))]
    check('every item names an existing cell', not gone, gone[:3])

    print('\nwxa gates: %d anomalies' % len(findings))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
