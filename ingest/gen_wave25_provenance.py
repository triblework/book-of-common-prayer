#!/usr/bin/env python3
"""Wave 25 -- provenance for R24 (the apostrophe) and R25 (the possessive).

A FOLLOW-UP to every earlier generator: one sentence is appended to the note
of each record whose cell Wave 25 changed (counted from the cells against
Wave 25's base, so it cannot drift from what the cells say), and of the three
1928 Psalter records, whose possessives were read and stay. A record with no
note gets one. The verify_items are untouched: Wave 25 opens and closes no
flag.

Re-runnable: the Wave 25 sentence is the note's last; a second run replaces
it. After writing, the file is re-parsed and every record compared with the
one before: only `note` may differ, and only by the Wave 25 sentence.

    python3 ingest/gen_wave25_provenance.py
"""
from __future__ import annotations
import collections, re, subprocess, sys
from pathlib import Path
import yaml

WT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WT / 'ingest'))
import w25_witness as W

SENT = re.compile(r' ?Wave 25: .*$', re.S)


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def counts():
    """{(edition, service): (apostrophes set, [(old s, new s, evidence)])}"""
    out = {}
    for ed, rel, p in W.cells(str(WT)):
        b = subprocess.run(['git', 'show', '%s:editions/%s/%s' % (W.BASE, ed, rel)], cwd=WT,
                           capture_output=True, text=True).stdout
        b2, ch = W.set_possessives(ed, rel, b)
        n = sum(1 for x, y in zip(b2, W.curl(b2)) if x != y)
        if n or ch:
            out[(ed, rel[:-3])] = (n, [(o, w, ev) for _l, o, w, ev in ch])
    return out


def sentence(ed, svc, n, ch):
    s = ' Wave 25:'
    if n:
        s += (' %d apostrophe%s in this cell set as U+2019, the corpus\'s one encoding of the '
              'printed apostrophe (RULINGS R24, maintainer 2026-11-06, "Curly, all cells"); the '
              'carrier may carry U+0027, so this cell differs from it in that character only; '
              'quotation marks are not apostrophes and are untouched (ingest/w25_witness.py).'
              % (n, '' if n == 1 else 's'))
    for old, new, ev in ch:
        if ed == '1892':
            s += (' The possessive of small-capital LORD in the office\'s psalm follows the book, '
                  'with a lower-case s ("LORD’s" where the cell printed "LORD\'S"; R23), '
                  'read by eye off the 1892 Standard Book scan, scan page 331 (book p. 303) '
                  '(ingest/w25_eye.txt).')
    if ed == '1979' and ch:
        k = collections.Counter((o, w) for o, w, _ev in ch)
        parts = ['%d %s -> %s' % (v, o, w) for (o, w), v in sorted(k.items())]
        s += (' The possessive of small-capital LORD takes the case of its s from the face Church '
              'Publishing\'s file sets it in (Sabon-Roman a lower-case s, Sabon-RomanSC a '
              'small-capital S), where an eye read of the rendered page agrees: R11 reopened for '
              'the possessive only (R25, maintainer 2026-11-06). In this cell: %s (%s; '
              'ingest/w25_fontruns.py, ingest/w25_eye.txt). The file is the publisher\'s '
              'typesetting, not a scan of a 1979 printing.'
              % (', '.join(parts), '; '.join(ev for _o, _w, ev in ch)))
    if ed == '1928' and svc.startswith('psalter/psalms-'):
        m = sum(1 for m in W.POSS.finditer(open(W.cell_path(ed, svc + '.md'),
                                                encoding='utf-8').read()))
        s += (' Its %d possessive%s of small-capital LORD %s read by eye in both printings '
              '(1928/BCP1929.pdf and the 1952 facsimile): a small-capital S every time, which '
              'R23 sets as "S" -- the cell\'s LORD’S stands (R25; ingest/w25_eye.txt).'
              % (m, '' if m == 1 else 's', 'was' if m == 1 else 'were'))
    return s


def main():
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8')
    before = yaml.safe_load(body)['records']
    cnt = counts()
    for svc in ('psalter/psalms-1-50', 'psalter/psalms-51-100', 'psalter/psalms-101-150'):
        cnt.setdefault(('1928', svc), (0, []))
    n_rec = 0
    for (ed, svc), (n, ch) in sorted(cnt.items()):
        m = re.search(r'^  - edition: %s\n    service: %s\n' % (re.escape(ed), re.escape(svc)),
                      body, re.M)
        if not m:
            raise SystemExit('record not found: %s %s' % (ed, svc))
        nxt = re.search(r'^  (- edition:|# )', body[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(body) - m.end())
        blk = body[m.start():end]
        rec = yaml.safe_load(blk)[0]
        was = SENT.sub('', rec.get('note') or '')
        new_note = (was + sentence(ed, svc, n, ch)) if was else sentence(ed, svc, n, ch).lstrip()
        nm = re.search(r'^    note:.*(?:\n      .*)*$', blk, re.M)
        line = '    note: ' + q(new_note)
        if nm:
            blk = blk[:nm.start()] + line + blk[nm.end():]
        else:
            vm = re.search(r'^    verify_items:', blk, re.M)
            at = vm.start() if vm else len(blk.rstrip('\n')) + 1
            blk = blk[:at] + line + '\n' + blk[at:]
        body = body[:m.start()] + blk + body[end:]
        n_rec += 1
    after = yaml.safe_load(body)['records']
    if len(after) != len(before):
        raise SystemExit('record count changed')
    for a, b in zip(before, after):
        da = {k: v for k, v in a.items() if k != 'note'}
        db = {k: v for k, v in b.items() if k != 'note'}
        if da != db:
            raise SystemExit('a field other than note changed: %s %s' % (a['edition'], a['service']))
        na, nb = SENT.sub('', a.get('note') or ''), SENT.sub('', b.get('note') or '')
        if na != nb:
            raise SystemExit('a note changed beyond the Wave 25 sentence: %s %s'
                             % (a['edition'], a['service']))
    p.write_text(body, encoding='utf-8')
    print('provenance: Wave 25 sentence on %d records (%d with apostrophes, %d with possessives)'
          % (n_rec, sum(1 for v in cnt.values() if v[0]), sum(1 for v in cnt.values() if v[1])))


if __name__ == '__main__':
    main()
