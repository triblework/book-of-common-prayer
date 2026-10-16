#!/usr/bin/env python3
"""wxa_report.py -- the generated tables of A_REPORT.md's "Phase 2" section
(Workstream A, Wave 23). Bodies stay out: every quotation is a key of at
most six words, an item id, or a page.

    python3 ingest/wxa_report.py [--gates DIR] [--proposed DIR] [--out FILE]

  --gates DIR     saved gate outputs (s1_*, s2_*, s3_*, c3_* .txt), pasted
  --proposed DIR  where the proposed copies of files this workstream may
                  not edit are written (editions.yaml, provenance.yaml,
                  w14_audit.py, w14_fidelity.py, w19_gates.py); the report
                  carries their unified diffs, and each copy is tested
                  in place (verify_index on a scratch root, the gates by
                  exec with their own __file__)
  --out FILE      append to FILE (default: stdout)
"""
import collections
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wxa_witness as W

SCRATCH = ('/private/tmp/claude-501/-Users-wtrible-Developer-bcp--claude-'
           'worktrees-bcp-wave-20-coordinator-5838d5/ff7c7f54-263d-4ce2-ac10-'
           'c0c8399ab47d/scratchpad/render/a')
FLAG = re.compile(r"<!-- VERIFY:?\s*'(.*?)'(\s*(?:—|;).*?)-->", re.S)
SHORT = {'MEDIANT_STOPS': 'MED', 'RUBRIC_STOPS': 'RUB', 'DOL_DISPUTED': 'DOL_D',
         'PASSAGES': 'PASS', 'HEADINGS': 'HEAD', 'SPELLING': 'SPELL'}
out = io.StringIO()


def p(*a):
    print(*a, file=out)


def git(*a):
    return subprocess.run(['git', '-C', WT] + list(a), capture_output=True,
                          text=True).stdout


def base(rel):
    return git('show', '%s:editions/1979/%s' % (W.BASE, rel))


def now(rel):
    f = os.path.join(WT, 'editions/1979', rel)
    return open(f, encoding='utf-8').read() if os.path.exists(f) else ''


def six(s, n=6):
    w = ' '.join(str(s).split()).split(' ')
    return ' '.join(w[:n]) + (' ...' if len(w) > n else '')


def cell_esc(s):
    return str(s).replace('|', '\\|')


# ---------------------------------------------------------------------------
def commits():
    p('### P2.1 Commit 1 -- items applied, per file and group\n')
    groups = W.COMMIT1
    p('| file | ' + ' | '.join(SHORT.get(g, g) for g in groups) + ' | total |')
    p('|---|' + '---|' * (len(groups) + 1))
    tot = collections.Counter()
    for rel in sorted(W.files(groups)):
        c = collections.Counter(g for g, _it in W.items_for(rel, groups))
        tot.update(c)
        p('| %s | %s | %d |' % (rel, ' | '.join(str(c[g] or '') for g in groups),
                                sum(c.values())))
    p('| **all** | %s | **%d** |' % (' | '.join(str(tot[g]) for g in groups),
                                    sum(tot.values())))
    ev = json.load(open(os.path.join(HERE, 'wxa_dol_extra_evidence.json')))
    src = collections.Counter(r['source'] for r in ev['rows'])
    p('\nNew cell `tables/daily-office-lectionary-holy-days.md` (generator '
      '`wxa_dol_extra.py`): %d rows -- %s; %d flags (P2.6).\n'
      % (len(ev['rows']), ', '.join('%s %d' % kv for kv in sorted(src.items())),
         len(ev['flags'])))

    p('### P2.2 Commit 2 -- MARKUP, per file and pattern\n')
    pat_tot = collections.Counter(it.get('pattern') for it in W.ITEMS['MARKUP'])
    p('By pattern: ' + ', '.join('`%s` %d' % kv for kv in pat_tot.most_common())
      + ' -- %d items.\n' % sum(pat_tot.values()))
    p('| file | items | patterns |')
    p('|---|---|---|')
    for rel in sorted(W.files(['MARKUP'])):
        c = collections.Counter(it.get('pattern') for g, it in
                                W.items_for(rel, ['MARKUP']))
        p('| %s | %d | %s |' % (rel, sum(c.values()), ', '.join(
            '`%s` %d' % kv for kv in c.most_common()).replace('|', '\\|')))

    p('\n### P2.3 Commit 3 -- the re-flow, per file\n')
    import wxa_book
    import wxa_reflow
    bw = wxa_book.Book().joined
    p('| file | breaks joined | fragments | paragraphs | words rejoined |')
    p('|---|---|---|---|---|')
    t = collections.Counter()
    for rel in sorted(r for r in W.files(W.GROUP_ORDER) +
                      [os.path.relpath(f, os.path.join(WT, 'editions/1979'))
                       for f in __import__('glob').glob(os.path.join(
                           WT, 'editions/1979', W.REFLOW_DIR, '*.md'))]
                      if r.startswith(W.REFLOW_DIR)):
        if t['seen:' + rel]:
            continue
        t['seen:' + rel] = 1
        s2 = W.expected(rel, base(rel), 2)
        _n, j, b, a = wxa_reflow.reflow(s2, bw)
        g = len(wxa_reflow.reflow.glued)
        t.update({'j': j, 'b': b, 'a': a, 'g': g, 'files': 1})
        p('| %s | %d | %d | %d | %s |' % (rel, j, b, a, g or ''))
    p('| **%d files** | %d | %d | %d | %d |\n' % (t['files'], t['j'], t['b'],
                                                  t['a'], t['g']))


# ---------------------------------------------------------------------------
def flags_of(text):
    outl = []
    for m in FLAG.finditer(text or ''):
        line = text[:m.start()].count('\n') + 1
        outl.append((m.group(1), ' '.join(m.group(2).split()), line))
    return outl


def ledger():
    p('### P2.4 The flag ledger (against 710f635b)\n')
    closed, opened = [], []
    rels = sorted(set(os.path.relpath(f, os.path.join(WT, 'editions/1979'))
                      for f in __import__('glob').glob(
                          os.path.join(WT, 'editions/1979/**/*.md'),
                          recursive=True)))
    for rel in rels:
        b, n = flags_of(base(rel)), flags_of(now(rel))
        bk = [(k, note) for k, note, _l in b]
        nk = [(k, note) for k, note, _l in n]
        closed += [(rel, l, k, note) for k, note, l in b if (k, note) not in nk]
        opened += [(rel, l, k, note) for k, note, l in n if (k, note) not in bk]
    total = sum(len(flags_of(now(r))) for r in rels)
    p('Closed %d, opened %d; inline 1979 flags %d = 127 - %d + %d.\n'
      % (len(closed), len(opened), total, len(closed), len(opened)))
    closers = {}
    for g, v in W.ITEMS.items():
        for it in v:
            if it['class'] == 'flag' or it.get('closes_flag'):
                closers.setdefault(it['file'], []).append(it['id'])
    p('**Closed** (file:line at the base -- key -- what closes it)\n')
    p('| file:line | key | closed by | the flag said |')
    p('|---|---|---|---|')
    for rel, l, k, note in closed:
        by = ('the restored collect (PASSAGES, `%s`)' % closers[rel][0]
              if rel in closers and rel.startswith('collects') else
              'DOL_ROWS row repair (the book prints the row)')
        p('| %s:%d | `%s` | %s | %s |' % (rel, l, cell_esc(six(k, 8)), by,
                                          cell_esc(six(note.lstrip('—; '), 14))))
    p('\n**Opened** (file:line now -- key -- note)\n')
    p('| file:line | key | note |')
    p('|---|---|---|')
    for rel, l, k, note in opened:
        p('| %s:%d | `%s` | %s |' % (rel, l, cell_esc(six(k, 8)),
                                     cell_esc(six(note.lstrip('—; '), 22))))
    p('')
    return closed, opened


# ---------------------------------------------------------------------------
def refused():
    import wxa_hand as H
    d = json.load(open(os.path.join(HERE, 'wxa_dropped.json')))
    p('### P2.5 Refused and dropped, with reasons\n')
    p('**Items not made** (%d; `wxa_dropped.json`)\n' % len(d['dropped']))
    p('| file:line | class | reason | page | what (first six words) |')
    p('|---|---|---|---|---|')
    for x in d['dropped']:
        p('| %s:%d | %s | %s | %s | %s |' % (
            x['file'], x['line'], x['class'], cell_esc(x['reason']),
            x.get('page'), cell_esc(six(x['what']))))
    hand_at = {(h['file'], h['line']) for h in H.HAND}
    p('\n**Edge notes** (%d): one- or two-word typo fixes kept at an edge '
      'where the book runs on (they cut nothing); each block was looked at:\n'
      % len(d.get('edge_notes', [])))
    p('| file:line | edge | fix | page | disposition |')
    p('|---|---|---|---|---|')
    for x in d.get('edge_notes', []):
        disp = ('the lost stretch is hand-keyed (wxa_hand)' if (x['file'], x['line'])
                in hand_at else
                'the wrap split a word; the re-flow joins it' if 'harvest' in x['file']
                else 'layout only: the book sets a heading, list or second '
                'column there (nothing lost)')
        p('| %s:%d | %s | `%s` | %s | %s |' % (x['file'], x['line'], x['edge'],
                                               cell_esc(x['what']), x['page'], disp))
    # A15: the Phase-1b passage refusals and what became of each
    old = json.loads(git('show', '3a54bd4:ingest/wxa_dropped.json'))['dropped']
    d8 = [x for x in old if x['class'] == 'd8']
    flagged = {(f['file'], f['line']) for f in H.FLAGGED}
    mk = collections.defaultdict(list)
    for it in W.ITEMS['MARKUP']:
        mk[(it['file'], it['line'])].append(it)
    hid = {(it['file'], it['line']): it['id'] for it in W.ITEMS['PASSAGES']
           if it['class'] == 'hand'}
    p('\n**A15 -- the %d passages Phase 1b refused, and what became of each**\n'
      % len(d8))
    p('| file:line | Phase-1b reason | page | now |')
    p('|---|---|---|---|')
    n = collections.Counter()
    for x in d8:
        k = (x['file'], x['line'])
        if k in hid:
            what = 'hand-keyed: `%s`' % hid[k]
            n['hand'] += 1
        elif k in flagged:
            what = 'flagged (a mediant would be taken from the file)'
            n['flag'] += 1
        elif any(it.get('pattern') == '[ Page N>' for it in mk.get(k, [])):
            what = 'only the e-text\'s `[ Page N>` marker: MARKUP (no word lost)'
            n['markup'] += 1
        else:
            what = 'STILL OPEN'
            n['open'] += 1
        p('| %s:%d | %s | %s | %s |' % (x['file'], x['line'],
                                        cell_esc(x['reason']), x.get('page'), what))
    p('\nA15 tally: %s.\n' % ', '.join('%s %d' % kv for kv in sorted(n.items())))
    hp = [it for it in W.ITEMS['PASSAGES'] if it['class'] == 'hand']
    p('Hand-keyed passages in all: %d (each a PASSAGES item of class `hand`, '
      'its book text cut between the anchors in `wxa_hand.py`).\n' % len(hp))


# ---------------------------------------------------------------------------
def dol():
    d = json.load(open(os.path.join(HERE, 'wxa_dropped.json')))
    import wxa_tables as T
    T.compare(T.cell_dol(text=base('tables/daily-office-lectionary.md')),
              T.book_dol())
    p('### P2.6 The DOL second check (A13), and the Holy Days rows (A14)\n')
    p('`line` is the row\'s line at the base; the occasion is the book\'s '
      '(for a row the e-text had filed under the week before, the cell\'s '
      'heading at the base is given after it in brackets).\n')
    by_line = collections.defaultdict(list)
    for g in ('DOL_DISPUTED', 'FLAGS', 'DOL_FIX', 'DOL_ROWS'):
        for it in W.ITEMS.get(g, []):
            if it['file'] == 'tables/daily-office-lectionary.md':
                by_line[it['line']].append((g, it))
    p('| line | occasion / column | cell | book | other year | elsewhere | '
      'continuity | supports | outcome |')
    p('|---|---|---|---|---|---|---|---|---|')
    tally = collections.Counter()
    for c in d['dol_disputes']:
        ch = c.get('checks', {})
        oy = ch.get('other_year')
        oy = ('-' if not oy else '%s' % (oy if isinstance(oy, str) else
                                          ', '.join('%s=%s' % kv for kv in
                                                    sorted(oy.items()))))
        el = ch.get('elsewhere') or {}
        el = ', '.join('%s %s' % (k.replace('_reading_in_', '@').replace(
            'cell', 'c').replace('book', 'b'), v) for k, v in sorted(el.items()))
        if ch.get('witness_artifact'):
            el += '; witness artifact'
        its = by_line.get(c['line'], [])
        if any(g == 'DOL_DISPUTED' for g, _i in its):
            oc = "book's reading taken (DOL_DISPUTED)"
        elif any(g == 'FLAGS' for g, _i in its):
            oc = 'VERIFY, both readings (FLAGS)'
        elif c['supports'] == 'cell':
            oc = 'cell kept'
        else:
            oc = 'cell kept (%s)' % c['supports']
        tally[oc] += 1
        bk = T.MATCH.get(c['line'])
        occ = c['occasion']
        if bk and T.head_key(bk[1] or '') != T.head_key(occ.split(' / ')[1]):
            occ = '%s / %s / %s [%s]' % (bk[0], bk[1], bk[2],
                                         occ.split(' / ')[1])
        p('| %d | %s / %s | `%s` | `%s` | %s | %s | %s | %s | %s |' % (
            c['line'], cell_esc(occ), c['column'], cell_esc(c['cell']),
            cell_esc(c['book']), cell_esc(oy)[:60], cell_esc(el),
            ch.get('continuity', '-'), c['supports'], oc))
    p('\nOutcomes: %s.\n' % ', '.join('%s: %d' % kv for kv in tally.most_common()))
    ev = json.load(open(os.path.join(HERE, 'wxa_dol_extra_evidence.json')))
    p('**Holy Days / Special Occasions rows** (book pp. 996-1001; `source` '
      '= the carrier row checked field by field, or the witness):\n')
    p('| row | source | page | e-text entry |')
    p('|---|---|---|---|')
    for r in ev['rows']:
        p('| %s | %s | %s | %s |' % (cell_esc(r['row']), r['source'], r['page'],
                                     cell_esc(r.get('etext_entry') or '-')))
    p('\nFlags in the new cell: ' + '; '.join(
        '%s `%s`' % (cell_esc(a), cell_esc(b)) for a, b, _n in ev['flags']) + '.\n')


# ---------------------------------------------------------------------------
GATES = ['wxa_gates', 'w13_fidelity', 'w13_audit', 'w14_fidelity', 'w14_audit',
         'w15_fidelity', 'w15_audit', 'w16_gates', 'w17_gates', 'w18_gates',
         'w19_gates', 'w20_gates', 'verify']


def gates(gdir):
    p('### P2.7 Gates, per commit\n')
    p('Each stage was written from the base (`wxa_apply.py --stage N --write`) '
      'and gated before its commit; `c3` is the committed tip after commit 3 '
      '(commit 4 touches no cell).\n')
    p('| gate | ' + ' | '.join(['commit 1', 'commit 2', 'commit 3', 'tip']) + ' |')
    p('|---|---|---|---|---|')
    for gname in GATES:
        row = []
        for st in ('s1', 's2', 's3', 'c3'):
            f = os.path.join(gdir, '%s_%s.txt' % (st, gname))
            if not os.path.exists(f):
                row.append('-')
                continue
            t = open(f).read().strip().split('\n')
            if gname == 'verify':
                n = sum(1 for l in t if l.startswith('  - '))
                row.append('OK' if 'OK' in t[0] else '%d complaints' % n)
            else:
                summ = [l for l in t if re.match(
                    r'^(audit|fidelity|w\d+ \w+|wxa gates)[^:]*:', l)]
                row.append(cell_esc((summ[-1] if summ else t[-1])[:70]))
        p('| %s | %s |' % (gname, ' | '.join(row)))
    for gname in ('w19_gates', 'w20_gates', 'w17_gates', 'w14_fidelity', 'w14_audit'):
        f = os.path.join(gdir, 'c3_%s.txt' % gname)
        if not os.path.exists(f):
            continue
        t = open(f).read().split('\n')
        bad = [l for l in t if l.startswith(('FAIL', 'ANOMALY', '  - ')) or
               'UNATTESTED' in l or l.startswith('w17 pointing')]
        p('\n`%s` at the tip -- the failing lines:\n' % gname)
        p('```')
        for l in bad:
            p(l[:240])
        p('```')
    f = os.path.join(gdir, 'c3_verify.txt')
    if os.path.exists(f):
        t = [l for l in open(f).read().split('\n') if l.startswith('  - ')]
        p('\n`tools/verify_index.py --root . --check` at the tip: %d complaints '
          '(provenance.yaml is off limits to this workstream; P2.8 has the '
          'diff that settles every one):\n' % len(t))
        p('```')
        for l in t:
            p(l[:200])
        p('```\n')


# ---------------------------------------------------------------------------
def yq(s):
    return json.dumps(s, ensure_ascii=False)


def block_range(lines, svc):
    """(start, end) line indexes of provenance.yaml's 1979 entry for svc."""
    for i, l in enumerate(lines):
        if l.strip() == '- edition: 1979' and i + 1 < len(lines) and \
                lines[i + 1].strip() == 'service: %s' % svc:
            j = i + 1
            while j < len(lines) and not lines[j].startswith('  - edition:') \
                    and not re.match(r'^\S', lines[j]):
                j += 1
            return i, j
    return None


def item_ranges(lines, a, b):
    """[(start, end)] of each verify_items entry inside block [a, b)."""
    outl, cur = [], None
    for i in range(a, b):
        if lines[i].startswith('      - '):
            if cur is not None:
                outl.append((cur, i))
            cur = i
        elif cur is not None and not lines[i].startswith('        '):
            outl.append((cur, i))
            cur = None
    if cur is not None:
        outl.append((cur, b))
    return outl


def norm_sig(t):
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()


def proposed(pdir, closed, opened):
    os.makedirs(pdir, exist_ok=True)
    p('### P2.8 Proposed diffs for files this workstream may not edit\n')
    p('Each is generated by `wxa_report.py` and tested on a scratch copy; '
      'none is applied here.\n')

    # editions.yaml
    src = open(os.path.join(WT, 'editions.yaml'), encoding='utf-8').read()
    lines = src.split('\n')
    i = next(k for k, l in enumerate(lines) if l.strip() == '- id: 1979')
    j = next(k for k in range(i, len(lines)) if lines[k].strip().startswith('present:'))
    lines[j] = lines[j].replace('tables/daily-office-lectionary, ',
                                'tables/daily-office-lectionary, '
                                'tables/daily-office-lectionary-holy-days, ', 1)
    newy = '\n'.join(lines)
    fy = os.path.join(pdir, 'editions.yaml')
    open(fy, 'w', encoding='utf-8').write(newy)

    # provenance.yaml
    src = open(os.path.join(WT, 'provenance.yaml'), encoding='utf-8').read()
    lines = src.split('\n')
    # removals: the closed flags' items
    kill = set()
    for rel, _l, k, note in closed:
        svc = rel[:-3]
        r = block_range(lines, svc)
        if not r:
            continue
        for a, b in item_ranges(lines, *r):
            body = '\n'.join(lines[a:b])
            m = re.search(r'source_reading:\s*(".*?"|\'.*?\'|.*)$', body, re.M)
            sig = None
            if m:
                sig = norm_sig(json.loads(m.group(1)) if m.group(1).startswith('"')
                               else m.group(1).strip("'"))
            nm = re.search(r'note:\s*(".*")\s*$', body, re.M)
            nnote = json.loads(nm.group(1)) if nm else ''
            if sig and sig == norm_sig(k):
                kill.add((a, b))
            elif not sig and norm_sig(k) in norm_sig(nnote) and \
                    'absent from the public-domain e-text' in nnote and \
                    'absent from the public-domain e-text' in note:
                kill.add((a, b))
    for a, b in sorted(kill, reverse=True):
        del lines[a:b]
    # additions: the opened flags, under their service; the new cell's entry
    add = collections.defaultdict(list)
    for rel, _l, k, note in opened:
        add[rel[:-3]].append((k, note))
    newcell = 'tables/daily-office-lectionary-holy-days'
    for svc, fl in add.items():
        if svc == newcell:
            continue
        r = block_range(lines, svc)
        a, b = r
        has = any(lines[x].strip() == 'verify_items:' for x in range(a, b))
        empty = [x for x in range(a, b) if lines[x].strip() == 'verify_items: []']
        if empty:                    # an empty list: it becomes the list
            lines[empty[0]] = '    verify_items:'
            has = True
        ins = [] if has else ['    verify_items:']
        for k, note in fl:
            ins += ['      - anchor: %s' % yq(svc.split('/')[-1]),
                    '        source_reading: %s' % yq(k),
                    '        note: %s' % yq(note if note.startswith((';', '—'))
                                            else '; ' + note)]
        while b > a and not lines[b - 1].strip():
            b -= 1
        lines[b:b] = ins
    r = block_range(lines, 'tables/daily-office-lectionary')
    ev = json.load(open(os.path.join(HERE, 'wxa_dol_extra_evidence.json')))
    entry = ['  - edition: 1979',
             '    service: %s' % newcell,
             '    source_url: "http://justus.anglican.org/resources/bcp/bcplectn.txt"',
             '    retrieved: 2026-10-16',
             '    status: transcribed',
             '    depth: table',
             '    verifier: %s' % yq('claude-opus-5.5 (wxa_dol_extra.py: carrier rows '
                                     'checked field by field against Church '
                                     "Publishing's PDF; wxa_gates, w14_audit)"),
             '    note: %s' % yq(
                 "The Daily Office Lectionary's Holy Days and Special Occasions "
                 '(book pp. 996-1001), which the 1993 e-text carries after its '
                 'two-year table. %d rows: %d carrier rows, each field checked '
                 "against Church Publishing's PDF; %d rows from the witness "
                 '(entries the e-text lost or damaged). Ruling A14 (Wave 23).'
                 % (len(ev['rows']),
                    sum(1 for x in ev['rows'] if x['source'] == 'carrier'),
                    sum(1 for x in ev['rows'] if x['source'] != 'carrier'))),
             '    verify_items:']
    for k, note in add.get(newcell, []):
        entry += ['      - anchor: %s' % yq(newcell.split('/')[-1]),
                  '        source_reading: %s' % yq(k),
                  '        note: %s' % yq(note)]
    a, b = r
    while b > a and not lines[b - 1].strip():
        b -= 1
    lines[b:b] = entry
    fp = os.path.join(pdir, 'provenance.yaml')
    open(fp, 'w', encoding='utf-8').write('\n'.join(lines))

    # w19_gates.py: pin the cell containment and the flag count to Wave 19's
    # own commit (as 050662b pinned the published side, R18)
    w19 = open(os.path.join(HERE, 'w19_gates.py'), encoding='utf-8').read()
    w19n = w19.replace(
        "        new = open(os.path.join(WT, rel), encoding='utf-8').read()\n"
        "        if not old:\n"
        "            check('containment %s: published cell available' % rel, False)",
        "        # pinned to Wave 19's own commit: later waves edit these cells\n"
        "        new = subprocess.run(['git', '-C', WT, 'show', W19 + ':' + rel],\n"
        "                             capture_output=True, text=True).stdout\n"
        "        if not old:\n"
        "            check('containment %s: published cell available' % rel, False)", 1)
    w19n = w19n.replace(
        "    n = 0\n"
        "    for root, _d, files in os.walk(os.path.join(WT, 'editions/1979')):\n"
        "        for fn in files:\n"
        "            if fn.endswith('.md'):\n"
        "                n += open(os.path.join(root, fn),\n"
        "                          encoding='utf-8').read().count('<!-- VERIFY')\n",
        "    n = 0          # counted at Wave 19's own commit (later waves move it)\n"
        "    for f in subprocess.run(['git', '-C', WT, 'ls-tree', '-r', '--name-only',\n"
        "                             W19, 'editions/1979'], capture_output=True,\n"
        "                            text=True).stdout.split():\n"
        "        if f.endswith('.md'):\n"
        "            n += subprocess.run(['git', '-C', WT, 'show', W19 + ':' + f],\n"
        "                                capture_output=True,\n"
        "                                text=True).stdout.count('<!-- VERIFY')\n", 1)
    if 'import subprocess' not in w19n:
        w19n = w19n.replace('import os', 'import os\nimport subprocess', 1)
    w19n = re.sub(r'(\nHERE = .*\n)', r"\1W19 = '19c6759'   # Wave 19's commit "
                  r"on authoring\n", w19n, count=1)
    open(os.path.join(pdir, 'w19_gates.py'), 'w', encoding='utf-8').write(w19n)

    # w14_audit.py: the DOL row count and the Holy Days row shapes
    import w14_audit as A14
    from pathlib import Path
    w14 = open(os.path.join(HERE, 'w14_audit.py'), encoding='utf-8').read()
    def nrows(t):
        return len([x for x in t.split('\n') if ' | ' in x and
                    not x.startswith('<!--')])
    grow = collections.Counter()
    nit = collections.Counter()
    for it in W.ITEMS['DOL_ROWS']:
        grow[it['class']] += nrows(it['new']) - nrows(it['old'])
        nit[it['class']] += 1
    want = nrows(now('tables/daily-office-lectionary.md'))
    w14n = w14.replace(
        "    ('1979', 'tables/daily-office-lectionary'): 784,",
        "    ('1979', 'tables/daily-office-lectionary'): %d,  # Wave 23: + %d lost\n"
        "    # rows, + %d rows that %d merged rows had swallowed, read off Church\n"
        "    # Publishing's PDF (DOL_ROWS); 784 was the 1993 e-text's own count"
        % (want, grow['lost-row'], grow['merged-row'], nit['merged-row']), 1)
    pages = {r['row']: r['page'] for r in ev['rows']}
    shapes = []
    f = Path(os.path.join(WT, 'editions/1979', newcell + '.md'))
    for anchor, rows in A14.sections(f).items():
        cnt = collections.Counter(A14.labels_of(r) for r in rows)
        top = cnt.most_common(1)[0][0]
        for r in rows:
            lab = A14.labels_of(r)
            if lab == top:
                continue
            occ = r.split(' | ')[0].strip()
            pg = next((v for k, v in pages.items() if k.startswith(occ)), None)
            if occ.startswith('Eve of'):
                why = ('the book prints an Eve with its evening psalms and '
                       'lessons only (p. %s).' % pg)
            elif occ == 'Footnote':
                why = ("the book's footnote to the Special Occasions, set as "
                       'the e-text sets it (p. 1001).')
            else:
                why = ('the book prints this day with morning and evening '
                       'psalms and lessons; the section\'s majority are its '
                       'Eves (p. %s).' % pg)
            shapes.append((occ, why))
    seen = set()
    kg = ''
    for occ, why in shapes:
        if occ in seen:
            continue
        seen.add(occ)
        kg += '    (%r, %r, %r):\n        %r,\n' % ('1979', newcell, occ, why)
    w14n = w14n.replace("\n}\n\n\ndef KNOWN_GOOD_KEYS", "\n    # Wave 23 -- the "
                        "Holy Days cell, read off Church Publishing's PDF\n"
                        + kg + "}\n\n\ndef KNOWN_GOOD_KEYS", 1)
    open(os.path.join(pdir, 'w14_audit.py'), 'w', encoding='utf-8').write(w14n)

    # w14_fidelity.py: the 8 words the witness restores in
    # order-how-rest-of-scripture
    w14f = open(os.path.join(HERE, 'w14_fidelity.py'), encoding='utf-8').read()
    oh = [it for it in W.ITEMS['PASSAGES']
          if it['file'] == 'front-matter/order-how-rest-of-scripture.md']
    w14fn = w14f.replace(
        "\ndef source_tokens(urls):",
        "\n# Wave 23: words the e-text swallowed, restored from Church Publishing's\n"
        "# PDF (the witness; %s, p. %s) -- attested there, not in bcplectn.txt\n"
        "WITNESS_ATTESTED = {\n"
        "    ('1979', 'front-matter/order-how-rest-of-scripture'): {\n"
        "        'brackets', 'case', 'entire', 'indicate', 'instances',\n"
        "        'omitted', 'repetition', 'whole'},\n"
        "}\n\n\ndef source_tokens(urls):" % (oh[-1]['id'], oh[-1]['page']), 1)
    w14fn = w14fn.replace(
        "        missing = sorted(cell_tokens(p) - source_tokens(urls) - SUPPLIED)",
        "        missing = sorted(cell_tokens(p) - source_tokens(urls) - SUPPLIED\n"
        "                         - WITNESS_ATTESTED.get((ed, service), set()))", 1)
    open(os.path.join(pdir, 'w14_fidelity.py'), 'w', encoding='utf-8').write(w14fn)

    # the diffs, and the tests
    for name, orig in (('editions.yaml', os.path.join(WT, 'editions.yaml')),
                       ('provenance.yaml', os.path.join(WT, 'provenance.yaml')),
                       ('ingest/w14_audit.py', os.path.join(HERE, 'w14_audit.py')),
                       ('ingest/w14_fidelity.py', os.path.join(HERE, 'w14_fidelity.py')),
                       ('ingest/w19_gates.py', os.path.join(HERE, 'w19_gates.py'))):
        mine = os.path.join(pdir, os.path.basename(name))
        dd = subprocess.run(['diff', '-u', '--label', 'a/' + name, '--label',
                             'b/' + name, orig, mine], capture_output=True,
                            text=True).stdout
        if name == 'editions.yaml':
            # the present: line is one long list; show the change, not the line
            dd = ('in the `- id: 1979` entry\'s `present:` list, after '
                  '`tables/daily-office-lectionary,` insert '
                  '`tables/daily-office-lectionary-holy-days,` (one list item; '
                  'the copy at `%s` has it)\n' % mine)
            p('**%s**: %s' % (name, dd))
            continue
        p('**%s** (%d lines of diff):\n' % (name, dd.count('\n')))
        p('```diff')
        p(dd.rstrip())
        p('```\n')
    # test: verify_index on a scratch root with the proposed provenance
    vt = os.path.join(pdir, 'vroot')
    os.makedirs(vt, exist_ok=True)
    for nm, target in (('provenance.yaml', fp),
                       ('editions', os.path.join(WT, 'editions'))):
        lk = os.path.join(vt, nm)
        if os.path.lexists(lk):
            os.remove(lk)
        os.symlink(target, lk)
    r = subprocess.run([sys.executable, os.path.join(WT, 'tools/verify_index.py'),
                        '--root', vt, '--check'], capture_output=True, text=True)
    p('Test: `verify_index.py --check` on a scratch root holding the proposed '
      'provenance.yaml and these editions/: exit %d -- %s\n'
      % (r.returncode, (r.stdout + r.stderr).strip().split('\n')[0][:200]))
    for nm in ('w14_audit.py', 'w14_fidelity.py', 'w19_gates.py'):
        src = open(os.path.join(pdir, nm), encoding='utf-8').read()
        code = ('import sys, runpy\nsys.argv=[%r]\n'
                "g={'__name__':'__main__','__file__':%r}\n"
                'try:\n    exec(compile(%r, %r, "exec"), g)\n'
                'except SystemExit as e:\n    sys.exit(e.code)\n'
                % (nm, os.path.join(HERE, nm), src, os.path.join(HERE, nm)))
        r = subprocess.run([sys.executable, '-c', code], capture_output=True,
                           text=True, cwd=WT)
        last = (r.stdout + r.stderr).strip().split('\n')[-1]
        p('Test: the proposed `%s`, run in place: exit %d -- %s\n'
          % (nm, r.returncode, last[:160]))


# ---------------------------------------------------------------------------
def evidence():
    ev = json.load(open(os.path.join(HERE, 'wxa_evidence.json')))
    p('### Appendix P2-E -- evidence keys with pages, every item\n')
    p('Key = `GROUP:file:line:n` in `wxa_evidence.json` (the book fragment, the '
      'cell fragment and the check sit there). Listed per file and group as '
      '`line:n p.page` (MARKUP: the rule; a flag: its note names the page).\n')
    p('| file | group | keys |')
    p('|---|---|---|')
    per = collections.defaultdict(list)
    for g, v in W.ITEMS.items():
        for it in v:
            e = ev.get(it['id'], {})
            pg = e.get('page')
            tail = it['id'].split(':')
            key = '%s:%s' % (tail[-2], tail[-1])
            if g == 'MARKUP' and pg is None:
                per[(it['file'], g)].append('%s %s' % (key, it.get('pattern')))
            else:
                per[(it['file'], g)].append('%s p.%s' % (key, pg))
    for (rel, g), ks in sorted(per.items()):
        p('| %s | %s | %s |' % (rel, g, cell_esc(', '.join(ks))))
    p('')


def main():
    a = sys.argv[1:]
    gdir = a[a.index('--gates') + 1] if '--gates' in a else os.path.join(SCRATCH, 'gates')
    pdir = a[a.index('--proposed') + 1] if '--proposed' in a else \
        os.path.join(SCRATCH, 'proposed')
    commits()
    closed, opened = ledger()
    refused()
    dol()
    gates(gdir)
    proposed(pdir, closed, opened)
    evidence()
    text = out.getvalue()
    if '--out' in a:
        with open(a[a.index('--out') + 1], 'a', encoding='utf-8') as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
