"""wxa_apply.py -- the file->file applier for wxa_witness.

    python3 ingest/wxa_apply.py                      # dry run, ENABLED groups
    python3 ingest/wxa_apply.py --groups ALL         # dry run, every group
    python3 ingest/wxa_apply.py --groups WORDS,SPELLING
    python3 ingest/wxa_apply.py --groups ALL --each  # each group alone too
    python3 ingest/wxa_apply.py --groups ALL --resurvey
          # write the result to the scratch render dir (NOT editions/) and
          # re-run the word-for-word survey on it
    python3 ingest/wxa_apply.py --groups ... --write # writes editions/1979

It always starts from the BRANCH-BASE text of each cell (git 710f635b...),
so a re-run is idempotent and the result is exactly base + these groups --
the containment wxa_gates.py checks. A dry run writes nothing; --write
refuses unless --groups is given by name (never ALL by default) and every
item applies cleanly.
"""
import collections
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wxa_witness as W

SCRATCH = ('/private/tmp/claude-501/-Users-wtrible-Developer-bcp--claude-'
           'worktrees-bcp-wave-20-coordinator-5838d5/ff7c7f54-263d-4ce2-ac10-'
           'c0c8399ab47d/scratchpad/render/a/applied')


def base_text(rel):
    r = subprocess.run(['git', 'show', '%s:editions/1979/%s' % (W.BASE, rel)],
                       cwd=WT, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('no base text for %s' % rel)
    return r.stdout


def run(groups, write=False, out_dir=None, quiet=False):
    per = collections.defaultdict(collections.Counter)
    stale_all = []
    results = {}
    for rel in W.files(groups):
        text = base_text(rel)
        new, applied, stale = W.apply(rel, text, groups, strict=False)
        for g, _i in applied:
            per[rel][g] += 1
        stale_all += [(rel,) + s for s in stale]
        results[rel] = (text, new)
    if not quiet:
        gs = [g for g in W.GROUP_ORDER if g in groups]
        print('%-56s ' % 'file' + ' '.join('%5s' % g[:5] for g in gs) + ' total')
        tot = collections.Counter()
        for rel in sorted(per):
            tot.update(per[rel])
            print('%-56s ' % rel[:56] + ' '.join('%5d' % per[rel][g] for g in gs)
                  + ' %5d' % sum(per[rel].values()))
        print('%-56s ' % 'TOTAL' + ' '.join('%5d' % tot[g] for g in gs)
              + ' %5d' % sum(tot.values()))
        print('stale: %d' % len(stale_all))
        for s in stale_all[:20]:
            print('  STALE %s %s %s (%s)' % s)
    if write:
        if stale_all:
            raise SystemExit('stale items: nothing written')
        for rel, (old, new) in results.items():
            if new != old:
                open(os.path.join(WT, 'editions/1979', rel), 'w',
                     encoding='utf-8').write(new)
        print('written: %d files' % sum(1 for o, n in results.values() if o != n))
    if out_dir:
        for rel, (old, new) in results.items():
            p = os.path.join(out_dir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(new)
    return per, stale_all, results


def resurvey(results):
    """Re-align every corrected prose paragraph; count those still differing
    from the book in their words."""
    import wxa_book as B
    import wxa_survey as S
    import wxa_items as I
    bk = B.Book()
    still = collections.Counter()
    total = collections.Counter()
    for rel, (_old, new) in sorted(results.items()):
        if rel.startswith('tables/') and rel != 'tables/feasts-and-fasts.md':
            continue
        head = None
        for blk in I.blocks(new):
            if blk['kind'] == 'heading':
                head = blk['text']
                continue
            if blk['kind'] in ('row', 'comment'):
                continue
            w = [x[0] for x in I.cell_spans(blk['text'])]
            if len(w) < 12:
                continue
            r = I.locate_in(bk, rel, blk['line'], head, [], w, [])
            fam = rel.split('/')[0]
            total[fam] += 1
            if r is None or [o for o in r[3] if o[0] != 'equal']:
                still[fam] += 1
    print('\nRE-SURVEY of the corrected text (paragraphs of 12+ words):')
    for fam in sorted(total):
        print('  %-28s %4d of %4d still differ in words' % (fam, still[fam],
                                                          total[fam]))
    print('  %-28s %4d of %4d' % ('TOTAL', sum(still.values()),
                                   sum(total.values())))


def main():
    args = sys.argv[1:]
    groups = list(W.ENABLED)
    if '--groups' in args:
        v = args[args.index('--groups') + 1]
        groups = list(W.GROUP_ORDER) if v == 'ALL' else v.split(',')
        bad = set(groups) - set(W.GROUP_ORDER)
        if bad:
            raise SystemExit('unknown group(s): %s' % sorted(bad))
    write = '--write' in args
    if write and ('--groups' not in args or 'ALL' in args):
        raise SystemExit('--write needs --groups named one by one')
    if not groups:
        print('no group enabled (wxa_witness.ENABLED is empty): nothing to do')
        return
    if '--each' in args:
        print('EACH GROUP ALONE on the branch base:')
        for g in groups:
            per, stale, _r = run([g], quiet=True)
            print('  %-14s applied %4d  stale %d' % (
                g, sum(sum(c.values()) for c in per.values()), len(stale)))
        print()
    out = SCRATCH if '--resurvey' in args else None
    per, stale, results = run(groups, write=write, out_dir=out)
    if '--resurvey' in args:
        resurvey(results)


if __name__ == '__main__':
    main()
