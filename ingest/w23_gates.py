#!/usr/bin/env python3
"""w23_gates.py -- what must hold for the 1979 witness pass (Workstream A,
Wave 23), at the stage the cells are at (w23_witness.STAGE).

    python3 ingest/w23_gates.py

  1 evidence     every item has an evidence entry naming its book page and
                 fragment (a pure markup rule or a flag drop names its rule);
                 every refused item names its reason; the new Holy Days
                 cell's rows each name their page and source.
  2 residue      the Wave-19 Psalter collation residue is still exactly the
                 fifteen verses where the PDF's text layer drops a mark.
  3 containment  for every 1979 cell: its text at the branch base
                 (git 710f635b..., editions/1979/, never a live tag) with
                 exactly the groups of commits 1..STAGE applied (and the
                 prayers re-flowed at stage 3) == the cell now; a cell new in
                 this wave equals what its generator writes; no other cell
                 is new. Every group applies (commit-1 groups alone, FLAGS
                 and MARKUP on top of commit 1) with no stale item.
  4 composite    tables/calendar.md and tables/eucharistic-lectionary.md are
                 the base text, and no item targets them (R11 addendum: their
                 witness pages are a 2008 Calendar and the 2007 RCL).
  5 markup       from stage 2, no e-text markup pattern survives in a cell;
                 at every stage, none survives the all-groups dry run, and no
                 item brings markup or curly quotes in.
  6 flags        the flag ledger: flags closed and opened against the base,
                 each matched to the items that close or open it; the inline
                 count equals 127 - closed + opened.
  7 scope        no item touches the Psalter; every item names a cell.
  8 run-on       no item ends with the words that open the next block, or
                 starts with the words that close the one before (an item
                 that ran on into its neighbour would print them twice once
                 the prayers are re-flowed -- thanksgiving-general.md:35).
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
import w23_witness as W

findings = []
COMPOSITE = ('tables/calendar.md', 'tables/eucharistic-lectionary.md')
MARKS = {
    '=x=': r'=\S[^=\n]{0,58}=|=\S=', '&N.': r'&N\.', '&mdash.': r'&mdash\.',
    '&V./&R.': r'&[VR]\.', '**X* :': r'^\*\*[A-Za-z ,()]+\* : ',
    '[[': r'\[\[', ']]': r'\]\]', '&3em.': r'&3em', 'END OF': r'END OF \w+\.TXT',
    '&LordsPrayer.': r'&LordsPrayer', '*X* label': r'^\*[A-Z][A-Za-z ]+\*  ',
    '<An Outline>': r'<An Outline|of the Faith>', '[ Page N>': r'\[ Page \d+>',
}
COMMENT = re.compile(r'<!--.*?-->', re.S)
FLAG = re.compile(r"<!-- VERIFY:?\s*'(.*?)'(\s*(?:—|;).*?)-->", re.S)


def check(name, ok, detail=''):
    print('%-4s %s%s' % ('ok' if ok else 'FAIL', name,
                         '' if ok else '  <- ' + str(detail)[:200]))
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


def now(rel):
    p = os.path.join(WT, 'editions/1979', rel)
    return open(p, encoding='utf-8').read() if os.path.exists(p) else None


def marks_left(t, rel):
    if rel.startswith(('psalter/', 'tables/')):
        return []
    t = COMMENT.sub('', t)
    return [k for k, p in MARKS.items() if re.search(p, t, re.M)]


def flags_of(t):
    return [(m.group(1), ' '.join(m.group(2).split())) for m in FLAG.finditer(t or '')]


def main():
    stage = W.STAGE
    print('stage %d: groups %s%s' % (stage, W.enabled() or '[]',
                                     ' + re-flow' if stage >= 3 else ''))
    ev = json.load(open(os.path.join(HERE, 'w23_evidence.json')))
    dropped = json.load(open(os.path.join(HERE, 'w23_dropped.json')))
    allitems = [(g, it) for g, v in W.ITEMS.items() for it in v]

    # 1. evidence
    missing = [it['id'] for g, it in allitems if it['id'] not in ev]
    check('evidence entry for every item (%d items)' % len(allitems),
          not missing, missing[:3])
    nopage = [it['id'] for g, it in allitems
              if ev.get(it['id'], {}).get('page') is None and
              not (g == 'MARKUP' and it.get('pattern') != '&mdash.') and
              it['class'] != 'flag']
    check('every item but a pure markup rule or a flag drop names its page',
          not nopage, nopage[:3])
    check('every evidence entry has a book fragment or rule',
          all(v.get('book') for v in ev.values()))
    check('every refused item names its reason (%d refused)'
          % len(dropped['dropped']),
          all(d.get('reason') for d in dropped['dropped']))
    hd = os.path.join(HERE, 'w23_dol_extra_evidence.json')
    if os.path.exists(hd):
        he = json.load(open(hd))
        check('every Holy Days row names its page and source (%d rows)'
              % len(he['rows']),
              all(r.get('page') and r.get('source') for r in he['rows']))

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
    bw = None
    if stage >= 3:
        import w23_book
        bw = w23_book.Book().joined
    bad, new_ok = [], []
    present = cells()
    for rel in present:
        b = base(rel)
        if b is None and rel not in W.NEW_CELLS:
            bad.append((rel, 'new cell not declared in this wave'))
            continue
        want = W.expected(rel, b, stage, bw)
        if want is None:
            bad.append((rel, 'present before its stage'))
        elif want != now(rel):
            bad.append((rel, 'differs from base + stage %d' % stage))
    for rel, st in W.NEW_CELLS.items():
        if stage >= st and rel not in present:
            bad.append((rel, 'new cell missing'))
    check('containment: base 710f635b + stage %d == every cell now (%d cells)'
          % (stage, len(present)), not bad, bad[:3])
    for g in W.COMMIT1:
        st = []
        dep = W.COMMIT1 if g == 'FLAGS' else [g]
        for rel in W.files([g]):
            _n, _a, s = W.apply(rel, base(rel), dep, strict=False)
            st += [x for x in s if x[0] == g]
        check('group %-13s applies%s, no stale item' % (
            g, ' on commit 1' if g == 'FLAGS' else ' alone'), not st, st[:2])
    st_all, results = [], {}
    for rel in W.files(W.GROUP_ORDER):
        b = base(rel)
        n, _a, s = W.apply(rel, b, W.GROUP_ORDER, strict=False)
        st_all += s
        results[rel] = n
    check('MARKUP on commit 1, and all groups together: no stale item',
          not st_all, st_all[:2])

    # 4. the composite witness
    tgt = [it['id'] for g, it in allitems if it['file'] in COMPOSITE]
    check('no item targets calendar.md or eucharistic-lectionary.md',
          not tgt, tgt[:3])
    for rel in COMPOSITE:
        check('%s is the base text' % rel, now(rel) == base(rel))

    # 5. markup
    left = {}
    for rel in present:
        if rel in W.NEW_CELLS:
            continue
        t = results.get(rel, base(rel))
        m = marks_left(t, rel)
        if m:
            left[rel] = m
    check('all-groups dry run: no e-text markup pattern survives', not left,
          list(left.items())[:3])
    if stage >= 2:
        now_left = {rel: marks_left(now(rel), rel) for rel in present}
        now_left = {k: v for k, v in now_left.items() if v}
        check('stage >= 2: no e-text markup pattern survives in the cells',
              not now_left, list(now_left.items())[:3])

    def nmarks(t):
        return sum(len(re.findall(p, t, re.M)) for p in MARKS.values())
    intro = [it['id'] for g, it in allitems
             if nmarks(it['new']) > nmarks(it['old'])
             or re.search(r'[‘’“”]', it['new'])]
    check('no item brings markup or curly quotes in', not intro, intro[:3])

    # 6. the flag ledger
    closed, opened = [], []
    for rel in sorted(set(present) | set(W.NEW_CELLS)):
        b, n = flags_of(base(rel)), flags_of(now(rel))
        for f in b:
            if f not in n:
                closed.append((rel,) + f)
        for f in n:
            if f not in b:
                opened.append((rel,) + f)
    total = sum(len(flags_of(now(r))) for r in present)
    want_closed = 0
    want_opened = 0
    if stage >= 1:
        want_closed = sum(1 for g, it in allitems if it['class'] == 'flag') + \
            sum(it.get('flags_closed', 0) for g, it in allitems
                if g == 'DOL_ROWS' and it['class'] != 'flag')
        want_opened = len(W.ITEMS.get('FLAGS', []))
        if os.path.exists(hd):
            want_opened += len(json.load(open(hd))['flags'])
    check('flag ledger: %d closed (items say %d), %d opened (items say %d); '
          'inline %d == 127 - %d + %d' % (len(closed), want_closed, len(opened),
                                          want_opened, total, len(closed),
                                          len(opened)),
          len(closed) == want_closed and len(opened) == want_opened and
          total == 127 - len(closed) + len(opened))
    if '--ledger' in sys.argv:
        for c in closed:
            print('  CLOSED %s  %r%s' % (c[0], c[1], c[2][:90]))
        for o in opened:
            print('  OPENED %s  %r%s' % (o[0], o[1], o[2][:90]))

    # 7. scope
    ps = [it['id'] for g, it in allitems if it['file'].startswith('psalter/')]
    check('no item touches the Psalter', not ps, ps[:3])
    gone = [it['id'] for g, it in allitems
            if not os.path.exists(os.path.join(WT, 'editions/1979', it['file']))]
    check('every item names an existing cell', not gone, gone[:3])

    # 8. run-on into a neighbouring block
    def wn(t):
        t = COMMENT.sub('', t)
        return [y for y in (re.sub(r'\W', '', x).lower() for x in t.split())
                if y]
    runon = []
    bl_cache = {}
    for g, it in allitems:
        if it['file'].startswith('tables/'):
            continue
        if it['file'] not in bl_cache:
            bl_cache[it['file']] = W.blocks(base(it['file']) or '')
        bl = bl_cache[it['file']]
        k = next((i for i, x in enumerate(bl) if x[0] == it['line']), None)
        if k is None:
            continue
        nw, ow = wn(it['new']), wn(it['old'])
        nxt = wn(bl[k + 1][2]) if k + 1 < len(bl) else []
        prv = wn(bl[k - 1][2]) if k > 0 else []
        for n in range(min(len(nw), len(nxt)), 1, -1):
            if nw[-n:] == nxt[:n] and ow[-n:] != nxt[:n] and \
                    bl[k][2].rstrip().endswith(it['old'].rstrip()):
                runon.append((it['id'], 'next', ' '.join(nw[-n:])))
                break
        for n in range(min(len(nw), len(prv)), 1, -1):
            if nw[:n] == prv[-n:] and ow[:n] != prv[-n:] and \
                    bl[k][2].lstrip().startswith(it['old'].lstrip()):
                runon.append((it['id'], 'prev', ' '.join(nw[:n])))
                break
    check('no item runs on into a neighbouring block (%d items)'
          % len(allitems), not runon, runon[:3])

    print('\nw23 gates (stage %d): %d anomalies' % (stage, len(findings)))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
