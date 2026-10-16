"""w22_control.py -- the control sample of the machine-clean queue (Q1).

Workstream C, Phase 1b. 150 verses drawn at random, with a recorded seed, from
the 2,311 verses w22_classify.py puts in Q1 (OCR reads ':' at the cell's pivot
and flags nothing else). Each is read WHOLE by eye off its crop, exactly as the
flagged queue was, and the disagreement rate between the machine class and the
eye decides whether a full eye pass over Q1 is needed.

    python3 ingest/w22_control.py          # draw + build strips ctl_NN.png
"""
import os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_crops as C

SEED = 20261016
N = 150


def draw():
    q1 = [l.split('\t')[0] for l in open(os.path.join(HERE, 'w22_firstpass.tsv'))
          if not l.startswith('#') and l.split('\t')[2] == 'Q1']
    pick = random.Random(SEED).sample(q1, N)
    return sorted(pick, key=lambda r: tuple(map(int, r.split(':')))), len(q1)


def main():
    refs, n = draw()
    recs, by = C.load()
    groups, cur = [], []
    for ref in refs:
        it = C.whole_items(by[tuple(map(int, ref.split(':')))])
        if cur and sum(i['rect'][3] for i in cur) + sum(i['rect'][3] for i in it) > 2300:
            groups.append(cur); cur = []
        cur.extend(it)
    if cur:
        groups.append(cur)
    for k, g in enumerate(groups):
        C.strip(g, 'ctl_%02d' % k)
    print('Q1 %d verses; seed %d; drew %d; %d strips' % (n, SEED, len(refs), len(groups)))
    print(' '.join(refs))


if __name__ == '__main__':
    main()
